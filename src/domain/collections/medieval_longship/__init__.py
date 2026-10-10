# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Longship set: the Viking Age in oak, sea and the northern sky, drawn in the medieval collection's hand.

Every sheet is built of oak planks, weathered silver brown by day and tarred dark by night, framed in a carved
plait of two strands with a prow beast risen at each top corner of a header, open-jawed over the gunwale, and
standing on the hull's lower strake with its clinker rivets; a row of painted round shields hangs along the
gunwale across the top, pausing whole on either side of the month's mark at its top centre when the design is the
month's. Titles are chip-carved into the oak, each stroke cut to a lit face and a dark one, and painted with red
ochre as the runestones were; by night they are inlaid with bronze in the firelight. Headers open on a fjord: its
walls of snowy crags rise at the sides, the longship sails under her striped sail with her oars out, her wake
behind her and spray at her bow, and the longhouse stands on the far shore with its gable beasts, its smoke and a
raven on its ridge; by day the sun on the water; by night the
aurora hangs its curtains across the sky, drifting and shimmering and greening the water and the snow, the moon
shines, the brazier burns and the window is lit. The section header is the dragon ship herself rowing in, her stem
swept up to a great carved head with its jaws open over the sheet and a lantern hung from it, and the strip's
lookout keeps watch on his crag by his beacon. A phone's H1 lays the whole fjord under its words, and its H2 and H3
stand the dragon ship's bow and the lookout under theirs. A header too heavy for its budget is drawn lighter by
thinning only its texture: the planks' grain, the faint stars, the outer rings of each light and some of the small
ornament. The footer stands on the fjord's water with the longship sailing at its right end and a brazier at the
corner of its notes; links are oak tags riveted with iron; badges are planks nailed up and painted; and the
elements are built of oak, rope, iron, stacked shields, helmed warriors, a bronze brooch and a runestone with its
serpent painted round it.
"""
from __future__ import annotations

import math

from ...holidays.designs import WIDE
from ...holidays.designs.badges import inside
from ...holidays.pixel import sphere, tube
from ..hand import CollectionSet
from . import art as A
from .palette import C, NIGHT_SKY, RAMP, TOKENS, X, step

OAK, TAR, IRON, BRONZE, ROPE = RAMP["oak"], RAMP["tar"], RAMP["iron"], RAMP["bronze"], RAMP["rope"]
RED, CREAM, OCHRE = RAMP["red"], RAMP["cream"], RAMP["ochre"]
LINK_SPRITES = ("shield", "axes", "ship", "hammer")
SHEET_RULE = 20   # the row an element's sheet rules off its tag and title at


class Longship(CollectionSet):
    key = "medieval-longship"
    name = "Longship"
    collection = "medieval"
    # What the design is, in words, for the page that shows the collection.
    tagline = (
        "A longship rowing home up a fjord under the northern lights, framed in carved oak with prow beasts at "
        "the corners.")
    about = (
        "Every sheet is built of oak planks, weathered silver brown by day and tarred dark by night. It is framed "
        "in a carved two-strand plait, with open-jawed prow beasts rising at a header's top corners and a row of "
        "painted round shields hung along the gunwale. Titles are chip-carved into the oak, each stroke cut to a "
        "lit upper face and a dark lower one, and painted with red ochre as the runestones were; by night they are "
        "inlaid with bronze that catches the firelight. Headers "
        "open on a fjord between walls of snowy crags, where the longship sails under her striped sail with her "
        "oars out, her wake behind her and spray at her bow, and on the far shore a longhouse with carved gable "
        "beasts sends up its smoke while a raven keeps watch from the ridge. By day the sun lies on the water; by "
        "night the aurora hangs three green bands with a violet fringe and curtains of rays across the sky, "
        "drifting and shimmering and greening the sea and the snow, while the moon shines, the brazier burns and "
        "the longhouse window glows. The section header is the dragon ship herself rowing in, her stem swept up "
        "to a great carved head with its jaws open over the sheet and a lantern burning on it by night, and the "
        "strip's lookout keeps watch on his crag by his beacon. On a phone the whole fjord lies under the words, "
        "and the dragon ship and the lookout stand under theirs at full height. The footer stands on the fjord's "
        "water with the longship sailing at its right end and a brazier at the corner of its notes, links are oak "
        "tags riveted with iron, and badges are painted planks nailed up. The elements are built of oak, rope and "
        "iron: histograms stack painted shields with a bronze boss on the tallest, placards stand as lichen-grey "
        "runestones with a red ochre serpent painted round the words, and helmed warriors with braided beards and "
        "a bronze brooch fill out the rest.")
    tokens = frozenset(TOKENS)

    # ---- colour and paper
    def ink(self, night):
        """The words in the hand's two inks, the titles bronze by night and red ochre by day."""
        return dict(
            title=BRONZE[4] if night else RED[2], shadow=TAR[0] if night else OAK[2],
            body=self.hand.body[night], muted=self.hand.muted[night],
            rule=X["rule_night"] if night else OAK[2], accent=BRONZE[5] if night else X["accent_day"],
            tag=RED[2], tag_ink=CREAM[5],
            fill=C["fill_night"] if night else C["fill"], dim=X["dim_night"] if night else X["dim_day"],
        )

    def lit(self, night):
        """By night the carved letters are inlaid with bronze; by day they are painted red ochre. (`title_text` draws
        the cut round them first, and by night the firelight's glow behind them.)"""
        if night:
            return dict(paint=A.INLAY, night=True)
        return dict(night=False)

    def paper(self, p, night, uid="p"):
        """The planks; the drawing keeps which sheet it is (`uid`, "p" for a header or a footer, "pl" for a
        placard) for the hooks the layout calls without saying."""
        p.sheet = uid
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        if not night:
            return C["paper"]
        return NIGHT_SKY[min(len(NIGHT_SKY) - 1, int(y * len(NIGHT_SKY) / p.h))]

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        """More stars than the kit asks for, round the aurora; fewer on a drawing made lighter."""
        n = round(n * (0.6 if p.lite else 1.2))
        A.stars(p, x0, y0, x1, y1, max(4, n), seed=seed, twinkling=twinkling, faint=faint, avoid=avoid)

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The planks, by night under the stars with the aurora hung across the top of the sheet, its curtains
        ending above the words under the title (the second box the layout keeps clear): drifting and
        shimmering across a wide moving header, still on a still one and fainter on a phone's."""
        super().sky(p, night, y1, seed=seed, motion=motion, avoid=avoid)
        if night:
            wide = p.w == WIDE
            words = avoid[1][1] + 2 if len(avoid) > 1 else y1
            A.aurora(p, 4, 6, p.w - (3 if wide else 4), min(y1 - 4, words, 60 if wide else 50), seed=seed + 7,
                     motion=motion and wide, strong=wide)

    def frame(self, p, night, webs=False):
        """The border: a carved plait down the sides and along the top, a prow beast risen at each top corner
        of a header and an iron boss at each of any other sheet's, and the strake of a hull along the foot; but
        a footer (the sheet the layout frames without webs on the paper of a banner) stands on the fjord's water
        instead (see `_footed`)."""
        A.frame(p, night, heads=webs, strake=0 if (not webs and getattr(p, "sheet", "") == "p") else 4)

    def top_centre(self, p) -> tuple:
        """The columns of a header's top kept for the month's mark: its box and two units either side of it."""
        n = self.hand.mark_size
        x0 = p.w // 2 - n // 2
        return x0 - 2, x0 + n + 2

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """The shields hung along the gunwale, its ends tucked under the prow beasts' jaws; where the month's mark
        is drawn, they pause for it at the top centre (see `art.gunwale`)."""
        A.gunwale(p, x0 + 22, x1 - 22, y, night, seed=seed, clear=self.top_centre(p) if self.marked else None)

    def tag(self, p, x, y, w, h, night):
        """The block of red paint a tag's cream letters sit on: lit along its top, shaded along its foot.
        The ribbon under a certificate's seal, the one tag set low on its sheet, is a woven braid."""
        p.rect(x, y, w, h, RED[2])
        p.hline(x, x + w, y, RED[4])
        p.hline(x, x + w, y + h - 1, RED[0])
        if y >= 30 and h >= 9 and x >= 9 and x + w + 4 <= (100 if p.w == WIDE else 88) - 2:
            A.braid(p, x, y, w, h, night)

    def title_text(self, p, x, y, s, night, scale):
        """Letters chip-carved into the oak by day and painted with red ochre, as the runestones were: each stroke cut
        to a ridge, its face turned to the light paler than the ochre of its face in shade, the cut's upper edge
        catching the light along every upper edge of a letter, its lower face dark under every lower edge, and the
        shadow the letters throw beyond it; by night the whole cut inlaid with bronze in the firelight's glow, with a
        glint here and there that twinkles. On a runestone the letters are cut into the granite instead. A drawing
        made lighter keeps all of it but the glow's outer rings."""
        k = self.ink(night)
        lit = self.lit(night)
        stone = getattr(p, "sheet", "") == "pl"
        Rk = RAMP["rock"]
        if night:
            A.carve(p, x, y, s, scale, Rk[3] if stone else TAR[5], TAR[0])
            if not stone:
                w = p.measure(s, "57", scale)
                A.glow(p, x + w / 2, y + 3.5 * scale, w / 2 + 4 * scale, 5 * scale, RAMP["flame"][4],
                       (0.04, 0.08, 0.13))
        else:
            A.carve(p, x, y, s, scale, Rk[6] if stone else OAK[6], Rk[1] if stone else OAK[1],
                    shadow=X["shade_ink"] + ":0.35")
        w = A.letters(p, x, y, s, k["title"], scale, **lit)
        if not night and scale >= 3:
            A.facets(p, x, y, s, scale, RED[4])
        if night and scale >= 2:
            A.glints(p, x, y, s, scale)
        return w

    # ---- the headers' scenes
    def section_mark(self, p, x, y, night):
        """The round shield over crossed axes beside SECTION A-A, from a row above the words to four under
        them: two clear of the title's foot above and of the tagline below."""
        A.section_mark(p, x, y, night)

    def strip_mark(self, p, x, y, night):
        """A raven perched beside a strip's title."""
        A.raven(p, x, y - 5, night)

    @staticmethod
    def _room(p, x0, x1, g, most, least):
        """The rows free of words above the water's surface at row g between x0 and x1, `most` at the most,
        keeping three rows of margin above and two beside; None when fewer than `least` are free."""
        for room in range(most, least - 1, -1):
            if p.clear_of_words(x0 - 2, g - room - 3, x1 + 2, g + 3):
                return room
        return None

    @staticmethod
    def _skyline(p, x0, x1, g, margin=4):
        """For each column from x0 to x1, the highest row a scene may reach above the water at row g: `margin`
        rows under the lowest word over that column or the two beside it, and never into the gunwale."""
        out = []
        for x in range(x0, x1):
            low = 16
            for b in p.words:
                if b[0] - 3 <= x < b[2] + 3 and b[1] < g:
                    low = max(low, b[3] + margin)
            out.append(low)
        return out

    def _sky_life(self, p, night, motion, moon, path_g, gull, box):
        """What lives in the sky over a scene where no word stands: by day gulls wheeling; by night the moon,
        with its path on the water under it."""
        if not p.clear_of_words(*box):
            return
        if night:
            if moon:
                A.moon(p, *moon)
                A.moonpath(p, moon[0], path_g, motion)
        elif gull:
            cx, cy, rx, ry, seed = gull
            A.birds(p, cx, cy, rx, ry, "gull", motion, seed)

    def scene(self, design, p, rule, night, motion):
        """A wide header's fjord, its water at the rule: on H1 a wall of the fjord at each side, the
        longship sailing before the left one and the shore with its longhouse under the right one; on H2
        the longship rowing in beside the section's title, before the fjord's wall; on H3 the lookout on his
        headland. Each is built to the rows its words leave free over it."""
        g = rule - 1
        if design == "H1":
            spans = []
            room = self._room(p, 4, 54, g, g - 18, 16)
            if room:
                A.sea(p, 4, 56, g, night, seed=3, motion=motion)
                A.fjord_wall(p, 4, 56, g - 2, 70, night, high_left=True, seed=4, sky=self._skyline(p, 4, 56, g))
                spans.append(A.hero_ship(p, 4, g, night, motion, room=room, phase=0))
                if not night and room >= 52 and p.clear_of_words(22, 18, 42, 36):
                    A.sun(p, 31, 24, 3)
            self._sky_life(p, night, motion, None, g, (28, g - room - 2 if room else 40, 12, 3, 4),
                           (6, max(16, (g - room - 8) if room else 30), 54, (g - room + 4) if room else 46))
            room = self._room(p, 360, 411, g, g - 18, 14)
            if room:
                spans.append(self._shore(p, 360, 411, g, night, motion, room, phase=1))
        elif design == "H2":
            spans = [self._prow(p, 408, g, night, motion)]
        else:
            room = self._room(p, 354, 411, g, g - 18, 14)
            spans = [self._lookout(p, 356, 411, g, night, motion, room)] if room else []
        self._lighter(p, night)
        return [s for s in spans if s]

    def _lighter(self, p, night):
        """The last pass of light on a drawing made lighter, which the kit draws without `finish`: laid by the
        scene as it ends, the inner ring of each fire's pool and the aurora's brighter flecks on the water."""
        if p.lite and night:
            A.firelight(p)
            A.northlight(p)

    def _shore(self, p, x0, x1, g, night, motion, room, phase=0):
        """The shore across the fjord: the strand rising from the water with the longhouse on it, its smoke
        rising, the raven on its ridge and the brazier before it, burning by night; the fjord's wall of
        crags behind, its snow green under the aurora, and by night the moon over the house with its path
        on the water. Built to the `room` of rows free above the water."""
        A.sea(p, x0, x1, g, night, seed=11, motion=motion, glitter=not night)
        if room >= 30:
            A.fjord_wall(p, x0 - 4, x1, g - 2, 72, night, high_left=False, seed=6, sky=self._skyline(p, x0 - 4, x1, g))
        h = 6
        A.strand(p, x0 + 2, x1, g, h, night, seed=5, rock_from=x1 - 6)
        base = g - 2 - h
        if room >= 28:
            ridge = A.longhouse(p, x0 + 18, base + 1, night, phase=phase, motion=motion, ceiling=g - room)
            if room >= 40:
                A.raven(p, x0 + 28, ridge - 9, night)
        A.brazier(p, x0 + 4, base + 1, night, phase=phase + 1, reach=14, big=room >= 28)
        if night:
            A.glimmer(p, x0 + 6, g, phase + 1)
        if night and room >= 50 and p.clear_of_words(x0, g - room - 2, x0 + 16, g - room + 12):
            A.moon(p, x0 + 8, g - room + 5, 5)
            A.moonpath(p, x0 + 8, g, motion)
        elif not night and room >= 40:
            A.birds(p, x0 + 24, g - room + 8, 10, 3, "gull", motion, 7)
        return (x0 - 1, x1 + 1)

    def _head_spot(self, p, xb, ws, top=16, most=64, least=24, reach=26):
        """Where the great head of a dragon ship's stem goes, rising from her forefoot at column xb on the water at
        row ws: (L, x, y, sweep), its length, its snout's tip and how full its stem's curve is, the largest head
        that fits from `most` units down to `least`, set as high as the room allows under row `top` and as far
        forward over the sheet as `reach` columns before the forefoot, on the fullest curve that fits, its box, its
        stem and the lantern hung from it two units clear of every word, and its box of the month's mark and of the
        prow beast at the sheet's top right corner. None where no head fits."""
        lo, hi = self.top_centre(p)
        mark = (lo, 0, hi, self.hand.mark_size + 4)
        beast = (p.w - len(A.PROW[0]) - 2, 0, p.w, len(A.PROW) + 2)
        bl, bt, br, bf = A.DRAGON_BOX
        nx, ny = A.DRAGON_NECK
        for L in range(most, least - 1, -4):
            f = L / 100
            for hy in range(top + round(-bt * f), ws - round(bf * f) - 8):
                for joint in range(xb - reach, xb + 4):
                    hx = joint - round(nx * f)
                    box = (hx + round(bl * f) - 2, hy + round(bt * f) - 2,
                           hx + round(br * f) + 3, hy + round(bf * f) + 3)
                    if not self._kept_clear(p, box, (mark, beast)):
                        continue
                    for sweep in (1.0, 0.6, 0.3, 0.0):
                        path = A.stem_path(*A.stem_of(xb, ws, L, hx, hy, sweep))
                        lx, ly, mid = A.lantern_of(xb, ws, L, hx, hy, sweep)
                        if all(p.clear_of_words(xc - r - 3, y - 2, xc + r + 6, y + 3)
                               for y, (xc, r) in path.items()) and \
                                p.clear_of_words(lx - 2, ly - 4, mid, ly + 8):
                            return L, hx, hy, sweep
        return None

    def _prow(self, p, x1, g, night, motion):
        """The dragon ship rowing in beside a section's words, its hero: her bow coming in from the right before the
        fjord's wall, her shields along her gunwale and her oars biting, and her stem swept up to the great carved
        head with its jaws open over the sheet, as large as the room the words leave allows (see `art.prow_hero`),
        her lantern burning by night; by night the moon over her where the room allows, and gulls by day. Where the
        words leave no room for her head, the small rowing ship of the kit's own make rows in instead, under 18
        rows nothing."""
        ws = g - 2
        xb = next((x for x in range(300, x1 - 40) if p.clear_of_words(x - 17, ws - 12, x1 + 2, g + 3)
                   and p.clear_of_words(x - 8, ws - 38, x + 50, g + 3)), None)
        spot = self._head_spot(p, xb, ws) if xb is not None else None
        if not spot:
            room = self._room(p, 310, 410, g, g - 18, 16)
            if not room:
                return None
            A.sea(p, 310, x1, g, night, seed=7, motion=motion, glitter=not night)
            return A.rowing_ship(p, 312, g, night, motion, room=room)
        L, hx, hy, sweep = spot
        A.sea(p, xb - 14, x1, g, night, seed=7, motion=motion, glitter=not night)
        A.fjord_wall(p, xb - 6, x1 + 1, g - 2, ws - hy, night, high_left=False, seed=12,
                     sky=self._skyline(p, xb - 6, x1 + 1, g))
        span = A.prow_hero(p, xb, x1, g, night, motion, L, hx, hy, sweep)
        sky = round(hx + A.DRAGON_BOX[2] * L / 100) + 8
        for x in range(sky, x1 - 50, 4):
            if p.clear_of_words(x - 4, 28, x + 18, 50):
                if night:
                    A.moon(p, x + 6, 38, 5)
                else:
                    A.birds(p, x + 8, 40, 10, 3, "gull", motion, 5)
                break
        return span

    def _lookout(self, p, x0, x1, g, night, motion, room):
        """The lookout on his headland beside a strip, its hero rising the strip's full height: the crag rising
        from the water before the fjord's wall, the warrior standing watch at the edge of its cliff leaning on his
        spear, and beside him the beacon on its tall pole, its basket near the top of the room, cold by day and
        burning by night with its light on the water; a gull over the water by day. Built to `room`, the rows free
        of words above the water: the crag as tall as the room leaves over the warrior and his spear, lower as it
        shrinks; under 34 rows the warrior goes and the beacon stands alone on the crag, and under 14 nothing
        stands."""
        ws = g - 2
        A.sea(p, x0, x1, g, night, seed=9, motion=motion, glitter=not night)
        A.fjord_wall(p, x0 - 6, x1 + 1, g - 2, room + 4, night, high_left=False, seed=9,
                     sky=self._skyline(p, x0 - 6, x1 + 1, g))
        top = ws - max(4, min(26, room - 30))
        A.crag(p, x0 + 2, x1, g, top, night)
        A.beacon(p, x1 - 12, top + 1, max(g - room + 4, top - 30), night, phase=2, motion=motion)
        if room >= 34:
            A.lookout(p, x0 + 10, top + 1, night)
        if night:
            A.glimmer(p, x0 + 4, g, 2)
        elif room >= 26:
            A.birds(p, x0 + 14, g - room + 6, 8, 3, "gull", motion, 3)
        return (x0 - 1, x1 + 1)

    # ---- a phone's scenes
    # The rows the dragon ship's bow and the lookout on his crag take under a phone's words: each stands at least 40
    # rows tall there. Beside the words a phone has no such room, its top corner taken by the prow beast and its top
    # centre kept for the month's mark, so each always stands under them.
    PHONE_ROWS = {"H2": 50, "H3": 48}
    _under = None                       # the header being laid out with those rows
    _notes = 0                          # the notes of the phone H1 being drawn

    @property
    def phone_scene_rows(self):
        """The rows a phone's H1 leaves under its words for its fjord: 56, and ten more for each note, which are set
        under the words before it."""
        return 56 + 10 * self._notes

    def h1_narrow(self, h, night):
        """A phone's H1, the rows for its fjord counting its notes (see `phone_scene_rows`)."""
        self._notes = len(self.said(h))
        try:
            return super().h1_narrow(h, night)
        finally:
            self._notes = 0

    def h2_narrow(self, h, night):
        """A phone's H2, laid out with rows under its words for the dragon ship's bow (see `PHONE_ROWS`)."""
        return self._laid_under("H2", super().h2_narrow, h, night)

    def h3_narrow(self, h, night):
        """A phone's H3, laid out with rows under its words for the lookout on his crag (see `PHONE_ROWS`)."""
        return self._laid_under("H3", super().h3_narrow, h, night)

    def _laid_under(self, design, draw, h, night):
        self._under = design
        try:
            return draw(h, night)
        finally:
            self._under = None

    def phone_rows(self, design, title_w):
        """The rows a phone's H2 or H3 leaves under its words for its hero (see `PHONE_ROWS`)."""
        return self.PHONE_ROWS[design] if self._under == design else 0

    def scene_narrow(self, design, p, y, night):
        """A phone's H1 scene: the fjord across the rows under its words (see `phone_scene_rows`). An H2's and an
        H3's heroes stand under their words (see `PHONE_ROWS`)."""
        if design == "H1":
            self._fjord_narrow(p, y - 1, night)

    def scene_under(self, design, p, y0, y1, night):
        """A phone's hero under its words, from its last words at row y0 to its rule at y1, across the phone: on H2
        the dragon ship's bow rowing in; on H3 the lookout on his crag by his beacon."""
        g = y1 - 1
        if design == "H2":
            self._bow_narrow(p, g, y0 + 3, night)
        else:
            room = self._room(p, 6, 174, g, g - y0 - 3, 14)
            if room:
                self._watch_narrow(p, g, night, room)
        self._lighter(p, night)

    def _fjord_narrow(self, p, g, night):
        """A phone H1's fjord across the rows under its words, its water at row g: the longship sailing under her
        striped sail before the fjord's wall at the left, the shore under the other wall at the right with its
        longhouse, its smoke, the raven on its ridge and the brazier before it, and the open fjord between them,
        gulls over it by day; by night the moon over the house. Built to the rows the words leave free, under the
        month's mark."""
        room = self._room(p, 5, 175, g, g - 22, 18)
        if not room:
            return
        A.sea(p, 5, 120, g, night, seed=4, motion=False)
        A.fjord_wall(p, 4, 72, g - 2, room + 4, night, high_left=True, seed=5, sky=self._skyline(p, 4, 72, g))
        A.hero_ship(p, 9, g, night, False, room=room, phase=0)
        self._shore(p, 122, 175, g, night, False, room, phase=1)
        if not night and room >= 30:
            A.birds(p, 96, g - room + 9, 12, 3, "gull", False, 6)
        self._lighter(p, night)

    def _bow_narrow(self, p, g, top, night):
        """The dragon ship's bow under a phone's words, her water at row g: her forefoot left of the middle, her hull
        running off the sheet at the right before the fjord's wall, and her stem swept up to the great head as large
        as fits under row `top` (see `_head_spot`); by night the moon over her where the sky is clear, and gulls by
        day."""
        ws, x1, xb = g - 2, p.w - 5, 96
        spot = self._head_spot(p, xb, ws, top=top, most=52, least=24, reach=30)
        if not spot:
            return
        L, hx, hy, sweep = spot
        A.sea(p, 5, xb - 12, g, night, seed=13, motion=False, glitter=not night)
        A.fjord_wall(p, xb - 6, p.w - 3, g - 2, ws - hy, night, high_left=False, seed=12,
                     sky=self._skyline(p, xb - 6, p.w - 3, g))
        A.prow_hero(p, xb, x1, g, night, False, L, hx, hy, sweep)
        sky = round(hx + A.DRAGON_BOX[2] * L / 100) + 6
        for x in range(sky, x1 - 14, 3):
            if p.clear_of_words(x - 2, top, x + 16, top + 14):
                if night:
                    A.moon(p, x + 7, top + 7, 4)
                else:
                    A.birds(p, x + 7, top + 8, 6, 2, "gull", False, 5)
                break

    @staticmethod
    def _kept_clear(p, box, keep=()):
        """Whether a box (x0, y0, x1, y1) is clear of every word and of every box in `keep`."""
        x0, y0, x1, y1 = box
        return p.clear_of_words(*box) and not any(x0 < c and a < x1 and y0 < d and b < y1 for a, b, c, d in keep)

    def _watch_narrow(self, p, g, night, room):
        """A phone H3's scene under its words, its water at row g: at the right the lookout on his crag before the
        fjord's wall, keeping watch by his beacon on its tall pole, which burns by night with its light on the
        water (see `_lookout`); at the left the raven on its mooring post; and between them a longship under sail
        coming home up the fjord."""
        A.sea(p, 5, 104, g, night, seed=9, motion=False, glitter=not night)
        self._lookout(p, 102, 176, g, night, False, room)
        A.bollard(p, 22, g - 3, night)
        if room >= 21:
            A.raven(p, 16, g - 20, night, flip=False)
        A.ship_small(p, 44, g, night, room=min(room, 34), phase=2)

    def rule_decor(self, p, x0, x1, y, seed, night):
        """Clinker rivets along a rule, sparser on a sheet's own rule under its tag and title, and a third as
        many on a drawing made lighter."""
        every = (30, 48) if y <= SHEET_RULE else (16, 30)
        A.rivets(p, x0, x1, y, seed=seed, night=night, every=tuple(e * (3 if p.lite else 1) for e in every))

    def finish(self, p, night):
        """The last pass: by night the light of the braziers, the lantern and the beacon on what stands near
        them and the aurora's green on the water; and on an instruments sheet the dial's hand forged into a
        sword."""
        if night:
            A.firelight(p)
            A.northlight(p)
        if getattr(p, "dial", None):
            self._sword(p, night)

    def _sword(self, p, night):
        """The dial's hand as a sword laid from the boss: a leather grip, a bronze crossguard and a steel
        blade with a lit edge, in place of the plain line the layout drew."""
        cx, cy, r = p.dial
        reach = r - 11
        accent = self.ink(night)["accent"]
        hand = [(x, y) for (x, y), c in p.layers["base"].items() if c == accent
                and (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= reach ** 2]
        if not hand:
            return
        far = max(hand, key=lambda q: (q[0] - cx) ** 2 + (q[1] - cy) ** 2)
        ang = math.atan2(far[1] - cy, far[0] - cx)
        nx, ny = -math.sin(ang), math.cos(ang)
        k = -1 if night else 0
        for (x, y) in hand:
            d = math.hypot(x - cx, y - cy) / max(1, reach)
            if d < 0.3:
                c = ROPE[1 + k]
            elif d < 0.4:
                c = BRONZE[4 + k]
            else:
                c = IRON[6 + k] if (x + y) % 2 else IRON[5 + k]
            p.px(x, y, c)
        gx, gy = cx + 0.35 * reach * math.cos(ang), cy + 0.35 * reach * math.sin(ang)
        for s in (-2, -1, 1, 2):
            p.px(round(gx + nx * s), round(gy + ny * s), BRONZE[4 + k] if abs(s) == 1 else BRONZE[2 + k])
        p.px(far[0], far[1], IRON[6])

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        """A brazier at the corner of the closing notes, burning by night with its light on the planks."""
        A.brazier(p, x - 1, y + 10, night, phase=1, reach=10)

    def _footed(self, p, night):
        """A footer once its words are set, standing on the fjord's water with the design's mark on it, the
        longship under sail where the words leave her room (see `art.footing`)."""
        A.footing(p, night)
        return p

    def f1(self, ft, night):
        return self._footed(super().f1(ft, night), night)

    def f2(self, ft, night):
        return self._footed(super().f2(ft, night), night)

    def f1_narrow(self, ft, night):
        return self._footed(super().f1_narrow(ft, night), night)

    def f2_narrow(self, ft, night):
        return self._footed(super().f2_narrow(ft, night), night)

    def heart(self, p, x, y):
        A.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        """The sail's stripes, red and cream, lit along the top and shaded along the foot."""
        A.stripes(p, x0, y0, w, h, period)

    def link_colours(self, night):
        """An oak tag in an iron rim, dark letters by day; tarred oak with cream letters by night."""
        if night:
            return TAR[3], IRON[4], C["body_night"], TAR[1]
        return OAK[3], IRON[2], C["ink"], OAK[1]

    def link_top(self, p, x0, x1, y, seed, night):
        """The button finished as an oak tag: its upper edge lit, a streak of grain along it, and an iron
        rivet at each end with its shadow."""
        k = -1 if night else 0
        lit = TAR[4] if night else OAK[5]
        p.hline(x0 - 1, x1 + 1, y + 1, lit)
        for xx in range(x0 + 12, x1 - 3):
            if (xx * 5 + seed) % 9 < 5:
                p.px(xx, y + 7, TAR[2] if night else OAK[2])
        for rx in (x0, x1 - 3):
            p.px(rx, y + 2, IRON[6 + k])
            p.px(rx + 1, y + 2, IRON[4 + k])
            p.px(rx, y + 3, IRON[3 + k])
            p.px(rx + 1, y + 3, IRON[1])

    def link_icon(self, index, night, ink):
        return A.ICONS[LINK_SPRITES[index % len(LINK_SPRITES)]], A.icon_pal(night, ink)

    # ---- the elements
    def card_bevel(self, night):
        return (TAR[5], TAR[0]) if night else (CREAM[6], OAK[3])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A card as a plank panel: grain along its face, an iron band riveted down its icon cell's edge,
        and a nail at each corner."""
        A.plank_card(p, x, y, w, h, night)

    def wire_ink(self, night):
        return ROPE[2] if night else ROPE[3]

    def wire_lights(self, p, cells, night, seed):
        """The wire as a mooring rope, with a lashing round it every twelfth pixel."""
        A.rope_over(p, cells, night)
        for i, (x, y, d) in enumerate(cells[5:-7]):
            if i % 12 == (seed * 5) % 12:
                A.lashing(p, x, y, d, night)

    def dashes(self, night):
        return [RED[3], CREAM[3 if night else 4]]

    def ornament(self, kind, p, x, y, night):
        """A round shield over crossed axes in a free corner of the schematic."""
        if kind == "schematic":
            if p is not None:
                A.axes(p, x + 14, y + 15, 12, night)
                A.shield(p, x + 14, y + 15, 3, 9.5, night)
            return (29, 31)
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as a stack of round shields laid one on another, seen a little from above: the
        top one's painted face round its iron boss and the rims of those under it in their paints by turns,
        stood up from the base line. The drawing keeps the last bar, which `peak_mark` bosses in bronze when
        it is the busiest week's."""
        n = getattr(p, "bars", 0)
        p.bars = n + 1
        A.shield_stack(p, bx, base - v, bw, v, night, base, i=n)
        p.last_bar = (bx, base - v, bw, v, base, n)

    def peak_mark(self, p, x, y, night):
        """The busiest week's bar (the one just drawn) drawn again with its top shield's boss in bronze, and a
        small raven perched beside its count."""
        if getattr(p, "last_bar", None):
            bx, top, bw, v, base, n = p.last_bar
            A.shield_stack(p, bx, top, bw, v, night, base, i=n, bronze=True)
        Rv = RAMP["raven"]
        for (dx, dy, c) in ((2, 0, Rv[3]), (3, 0, Rv[3]), (1, 1, Rv[1]), (2, 1, Rv[1]), (3, 1, Rv[1]), (4, 1, Rv[1]),
                            (0, 1, IRON[3]), (2, 2, Rv[1]), (3, 2, Rv[1]), (4, 2, Rv[2]), (5, 2, Rv[2]), (3, 3, Rv[1]),
                            (2, 4, IRON[2]), (4, 4, IRON[2])):
            p.px(x + dx, y + dy, c)
        p.px(x + 2, y + 0, BRONZE[5])

    def dial_ring(self, p, arc, night):
        """The rim of a round shield bent over the dial: painted red and cream by quarters inside an iron
        rim, lit from the upper left."""
        cx = (arc[0][0] + arc[-1][0]) / 2
        cy = arc[0][1]
        r = (arc[-1][0] - arc[0][0]) / 2 + 1.5
        p.dial = (cx, cy, r)
        k = -1 if night else 0

        def colour(s, o, lam, x, y):
            rho = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if rho > r + 0.6:
                return IRON[2 + k] if lam < 0.5 else IRON[4 + k]
            a = math.degrees(math.atan2(y + 0.5 - cy, x + 0.5 - cx)) % 360
            ramp = RED if int(a // 45) % 2 else CREAM
            base = 3 if ramp is RED else 5
            return ramp[max(0, min(6, base + (1 if lam > 0.75 else -1 if lam < 0.3 else 0) + k))]
        tube(p, arc, 2.8, colour, outline=IRON[0])

    def dial_tick(self, p, x, y, night):
        p.px(x, y, BRONZE[5])
        p.px(x + 1, y + 1, BRONZE[1])

    def dial_hub(self, p, cx, cy, night):
        """The shield's boss: a bronze dome."""
        sphere(p, cx + 0.5, cy - 0.5, 3.2, BRONZE, lo=1, hi=6)

    def material(self, i, xx, yy, y0, y1, lift, night):
        """The ship's materials by turns: the striped sail, tarred strakes, a quartered shield's paint, dyed
        wool, riveted iron and the turf of the roof."""
        T, B, G = RAMP["tar"], RAMP["blue"], RAMP["turf"]
        kind = i % 6
        if kind == 0:
            c = RED[3] if ((xx // 3) % 2 == 0) else CREAM[5]
        elif kind == 1:
            c = T[1] if (yy - y0) % 4 == 3 else T[3] if (xx * 3 + yy) % 11 else T[4]
        elif kind == 2:
            c = OCHRE[4] if ((xx // 4) + (yy // 4)) % 2 == 0 else T[2]
        elif kind == 3:
            c = B[3] if (xx + yy) % 7 else B[5]
        elif kind == 4:
            c = IRON[6] if (xx % 5 == 2 and yy % 4 == 1) else IRON[4]
        else:
            c = G[4] if (xx * 5 + yy * 3) % 7 else G[2]
        return step(c, lift)

    def counter_cell(self, q, ox, oy, night):
        A.tally(q, ox, oy, night)

    def counter_ink(self, night, dim):
        """A numeral cut into the tally plank, inlaid with bronze by night; a leading nought cut shallower."""
        if night:
            return TAR[6] if dim else BRONZE[4]
        return OAK[2] if dim else OAK[0]

    def timeline_line(self, p, x0, x1, y, night):
        """The mooring rope the releases hang from, up to today, with a knot every so often."""
        if x1 - x0 >= 3:
            tube(p, [(x0, y + 1.5), (x1, y + 1.5)], 1.6, A.rope_colour(night), outline=ROPE[0])
            for x in range(x0 + 13, x1 - 4, 26):
                A.knot(p, x, y + 1, night)

    def release(self, p, x, gy, kind, night, i=0):
        """A painted shield hung from the rope for a release, a bigger one with a bronze boss for a big one,
        a small one for a patch, a bare rim for a release still to come, and a mooring post for the
        repository's founding."""
        if kind == "made":
            A.bollard(p, x, gy, night)
            return
        A.hanging_shield(p, x, gy, (i * 3 + 1) % 8, night, size=kind)

    def today_mark(self, p, x, y, night):
        """A raven perched at the rope's end, today."""
        A.raven(p, x - 5, y - 8, night)

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor as a warrior in a nasal helm with a braided beard, his cloak pinned with a bronze
        brooch, the beard and the cloak by turns; a bot wears a masked helm over mail."""
        A.warrior(p, cx, cy, i, night, bot=not person.get("initials"))

    def commit_bar(self, p, x, y, w, fill, night):
        """A contributor's share as red paint along an oak plank."""
        W = A.wood(night)
        p.box(x, y, w + 2, 4, W[0])
        p.hline(x + 1, x + w + 1, y + 1, W[4])
        p.hline(x + 1, x + w + 1, y + 2, W[3])
        p.hline(x + 1, x + 1 + fill, y + 1, RED[4])
        p.hline(x + 1, x + 1 + fill, y + 2, RED[2])

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """A bronze brooch round the seal's pressed centre."""
        A.brooch(p, cx, cy, r0, r1, night)

    def seal_mark(self, p, x, y, night):
        A.hammer(p, x + 2, y - 1, night)

    def placard_board(self, p, night):
        """A runestone over the whole card, its serpent painted round the words; the drawing keeps that it
        is the stone, so the title is cut into the granite."""
        p.sheet = "pl"
        A.runestone(p, night)

    def placard_mark(self, p, x, y, night):
        A.hammer(p, x, y - 6, night)

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """The set's touch over a badge, kept inside its shape and off its letters: the plank's upper edge
        lit, a streak of grain under it, the foot in shadow, a dark seam where the tarred label meets the
        painted value, and an iron nail at each end of the top edge and every tenth pixel along it."""
        h = s["h"]
        ty = self._text_y(s)
        text_rows = range(ty - 1, ty + (7 if s["font"] == "57" else 5) + 1)

        def ins(x, y):
            return 0 <= x < w and 0 <= y < h and inside(x, y, w, h, s["corner"])
        # Where the label's block ends: the first change of colour along two rows under the letters at once
        # (a plate's dots change one row at a time, and its frame is the first pixel of a row alone).
        row = h - 2 if (h - 2) % 4 != 2 else h - 3
        first = next((x for x in range(w) if ins(x, row) and ins(x, row - 1)), 0)
        edge = next((x for x in range(first + 2, w) if ins(x, row) and p.get(x, row) != p.get(x - 1, row)
                     and p.get(x, row - 1) != p.get(x - 1, row - 1)), w)
        if edge == w and p.get(first + 1, row) not in (self.badge_label()[0], self.badge_gold()[0],
                                                       self.plate_colours("day")["paper"],
                                                       self.plate_colours("night")["paper"],
                                                       self.plate_colours("live")["paper"]):
            edge = 0
        for y in range(h):
            for x in range(w):
                if not ins(x, y):
                    continue
                c = p.get(x, y)
                try:
                    if y == 0:
                        p.px(x, y, step(c, 1))
                    elif y == 1 and y not in text_rows and (x * 5 + seed) % 7 < 3:
                        p.px(x, y, step(c, -1))
                    elif y == h - 1:
                        p.px(x, y, step(c, -1))
                    elif x == edge:
                        p.px(x, y, step(c, -1))
                    elif not ins(x - 1, y):
                        p.px(x, y, step(c, 1))
                    elif not ins(x + 1, y):
                        p.px(x, y, step(c, -1))
                except KeyError:
                    pass
        ends = [x for x in range(w) if ins(x, 0) and ins(x, 1)]
        for x in [ends[0], ends[-1]] + list(range(10, w - 4, 10)) if ends else []:
            if ins(x, 0) and ins(x, 1) and not (edge - 1 <= x <= edge + 1):
                p.px(x, 0, IRON[6])
                p.px(x, 1, IRON[2])

    def badge_label(self):
        return (TAR[1], CREAM[5])

    def badge_gold(self):
        return (BRONZE[4], TAR[0])

    def badge_states(self):
        return {"green": (RAMP["green"][3], C["white"]), "yellow": (OCHRE[4], TAR[0]),
                "red": (RED[3], C["white"]), "slate": (IRON[4], C["white"])}

    def badge_swatches(self):
        G, B, V, F, S = RAMP["green"], RAMP["blue"], RAMP["violet"], RAMP["flame"], RAMP["sea"]
        return {"red": (RED[3], C["white"], None), "tenne": (F[3], TAR[0], None), "ochre": (OCHRE[4], TAR[0], None),
                "green": (G[3], C["white"], None), "blue": (B[3], C["white"], None), "sea": (S[2], C["white"], None),
                "violet": (V[3], C["white"], None), "cream": (CREAM[6], TAR[1], "grain"),
                "tar": (TAR[1], CREAM[5], None), "iron": (IRON[4], C["white"], None), "oak": (OAK[2], C["white"], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        if pattern == "grain" and y not in text_rows and (x * 3 + y * 5) % 11 == 0:
            return CREAM[3]
        return c

    def badge_outline(self, pattern):
        return CREAM[2] if pattern == "grain" else None

    def badge_shine(self, c, y, h):
        try:
            return step(c, 1) if y == 2 else step(c, -1) if y == h - 1 else c
        except KeyError:
            return c

    def plate_colours(self, mode):
        """A plate is a plank: weathered oak by day and tarred by night, nailed, the value painted red on it
        with cream letters; a live plate is a bronze plaque."""
        if mode == "day":
            return dict(paper=OAK[4], dot=OAK[3], frame=IRON[2], block=RED[2], ink=C["ink"], letters=CREAM[5])
        if mode == "night":
            return dict(paper=TAR[2], dot=TAR[3], frame=IRON[4], block=RED[2], ink=C["body_night"], letters=CREAM[5])
        return dict(paper=BRONZE[4], dot=BRONZE[3], frame=IRON[1], edge=BRONZE[1], ink=TAR[0])

    def plate_edge(self, block):
        return step(block, -1)


SET = Longship()
