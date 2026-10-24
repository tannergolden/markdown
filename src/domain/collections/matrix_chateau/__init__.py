# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Chateau set: a banquet by candlelight, November's design in the Matrix collection, drawn in the collection's
hand.

Every sheet is a wall of the chateau hung with silk damask, champagne gold by day and wine-dark by night, woven in an
ogee lattice with a lily in every cell, and held in a gilded frame strung with beads, which deepens along a header's
top into a frieze of egg and dart between corner blocks carved with rosettes, parting either side of the month's mark,
where two acanthus scrolls hang from it and frame the mark as a cartouche would; under the frieze hangs a valance of
red velvet swags caught up with gold tassels, parting round the mark and its scrolls. Across a header's sky, behind the
title, the chandeliers' crystal throws a shimmer of light over the silk, glints of gold by day and of the candles'
green by night twinkling down to just above the words under the title. Titles are gold leaf on carved letters,
chiselled to a ridge so that one face of every stroke takes the light and the other falls into shade, edged in the
gilt's darkest over the shadow they cast on the silk; in a moving header the candles glint on their corners and the
terminal's beam passes down them on the hand's period. Headers open on the hall, two marble columns framing a grand
staircase whose red carpet runs down its marble steps under brass rods to a lamp on each newel post, climbing between
its balustrades to a tall arched window, the moon and the code's glyph stars in it by night, with a crystal chandelier
hung over it from the frieze and more of them wherever the title leaves them room; the carpet runs on along the floor
to the banquet, the end of a long table in white linen with a candelabrum, a tiered chocolate cake and goblets of wine
on it, two swords crossed behind a gilded shield between a pair of sconces on the wall above, and before it a guest in
a long dark coat and dark glasses with a sword drawn. The section header stands the salon's fireplace at its right, a
hearth of white marble between fluted pilasters under a carved gilt shell, three green flames leaping from the logs in
its brick firebox, a clock and two candelabra on its mantel, a pier glass in a gilt frame over it as tall as the words
leave it and a torchere of five candles burning at either side, with a goblet of red wine beside SECTION A-A; the
strip's suit of armour stands on its marble plinth with its halberd, a red banner hung over it from the frieze so that
it rises the strip's full height and a torchere burning beside it, a little candelabrum beside the strip's title. On a
phone the whole chateau stands under the words, the hall at the left and the banquet at the right; the section header
stands the fireplace with the guest warming himself at it and a side table with a candelabrum and a goblet, and the
strip two suits of armour guarding the trophy of swords between two sconces. Every candle in the chateau burns on the
hand's phosphor, for in the Matrix every flame is code, and by night its green light is the only light the hall has,
pooling on the stair, the linen, the hearth and the floor. A header too heavy for its budget is drawn lighter by
thinning only its texture: half the crystal's shimmer and the titles' glints, the damask's lilies, the outer ring of
every glow and pool of light, and the faint edge of every candle's light.

Every footer stands on the red carpet's border under a gilt rod along its foot, a balustrade of marble balusters under
a gilt-capped rail rising behind it wherever the cells leave the wall free, and a title block hangs the chateau's
emblem, the gilded shield charged with the gold lily between two sconces, after its last cell; a gilt candlestick burns
in the corner of its notes, the heart is a ruby set in gold and the graphic scale's bar is gilt and red velvet by
turns. A link button is red velvet in a rim of gilt beads, led by the chandelier, a goblet, the candelabrum or two
crossed swords. A badge wears a string of gilt beads along its top, its label wine-dark velvet lettered in gold, a live
badge's label gilt, and a plate is the silk in a gilded frame. The elements are cut from the chateau's materials:
menu cards tied with velvet ribbons and gold cords hung with crystal drops, marble columns crowned in gold, a beaded
gilt dial on a gilt boss, the chateau's fabrics, counters cut into marble tiles in gilt, a velvet rope on gilt posts
with a candle in a gilt candlestick for every release and the mantel clock at today, cameos in oval gilt frames, a seal
ringed with gilt petals over the gold lily, and a placard of silk with carved rosettes at its corners. The boards are
polished white marble and mahogany parquet in a frame of gilt beads, and the Hall of Fame's winners stand on a
crenellated podium of veined white marble.
"""
from __future__ import annotations

from ...holidays.designs.badges import inside
from ...holidays.pixel import Pix
from ..hand import CollectionSet
from .. import rain
from . import art as A
from . import sheets as E
from . import surfaces as F
from .palette import C, RAMP, TOKENS, X

CARPET, GOLD, SILK, WINE = RAMP["carpet"], RAMP["gold"], RAMP["silk"], RAMP["wine"]
ARMOUR_X = 372    # the column an H3's suit of armour stands on: its halberd two units clear of its farthest words


class Chateau(CollectionSet):
    key = "matrix-chateau"
    name = "Chateau"
    collection = "matrix"
    tagline = "A banquet by candlelight in a chateau hung with silk and gilt, where every candle burns code green."
    about = (
        "Every sheet is a wall of the chateau hung with silk damask, champagne gold by day and wine-dark by night, "
        "woven in an ogee lattice with a lily in each cell and held in a gilded frame strung with beads, which deepens "
        "along a header's top into a frieze of egg and dart between corner blocks carved with rosettes, two acanthus "
        "scrolls framing the month's mark as a cartouche would and a valance of red velvet swags hung under it, and "
        "across the sky behind the title the chandeliers' crystal throws a shimmer of light over the silk. Titles are "
        "gold leaf on carved letters, chiselled so one face of every stroke takes the light and the other falls into "
        "shade, and in a moving header the candles glint on them. Headers open on the hall, where two marble columns "
        "frame a grand staircase, its red carpet running down the marble steps under brass rods to a lamp on each "
        "newel post and climbing to a tall arched window with the moon in it by night, crystal chandeliers hung over "
        "it all; the carpet runs on along the floor to the banquet, the end of a long table in white linen set with a "
        "candelabrum, a tiered chocolate cake and goblets of wine, two swords crossed behind a gilded shield on the "
        "wall above, and a guest in a long dark coat and dark glasses standing before it with a sword drawn. The "
        "section header is the salon's fireplace, three green flames leaping in its hearth of white marble under a "
        "pier glass in a gilt frame, a torchere burning at either side, and the strip's suit of armour stands its full "
        "height under a red banner with its halberd. On a phone the whole chateau lies under the words, the guest "
        "warms himself at the fireplace, and two suits of armour guard the trophy of swords. Every candle burns on the "
        "hand's phosphor, for in the Matrix every flame is code, and by night its green light is the only light the "
        "hall has, pooling on the stair, the linen, the hearth and the floor and glinting in the guest's glasses. "
        "Footers stand on the red carpet under a gilt rod, a marble balustrade rising behind it and the gilded shield "
        "between two sconces hung after the last cell; links are red velvet buttons in gilt beads, and badges wear a "
        "string of gilt beads along their top. The elements are cut from the same marble, gilt, velvet and crystal: "
        "marble columns crowned in gold, a beaded gilt dial, a velvet rope with a candle for every release, cameos in "
        "oval gilt frames and a seal ringed with gilt petals; the boards are white marble and mahogany parquet, and "
        "the winners stand on a crenellated podium of veined white marble.")
    tokens = frozenset(TOKENS)

    # ---- colour and paper
    def ink(self, night):
        """The words in the hand's two inks; the titles' colour the gilt's, deep by day and bright by night."""
        return dict(
            title=GOLD[5] if night else GOLD[1], shadow=WINE[0] if night else SILK[3],
            body=self.hand.body[night], muted=self.hand.muted[night],
            rule=X["rule_night"] if night else X["rule_day"], accent=GOLD[5] if night else CARPET[2],
            tag=GOLD[3] if night else CARPET[2], tag_ink=WINE[1] if night else GOLD[6],
            fill=WINE[4] if night else SILK[6], dim=X["dim_night"] if night else X["dim_day"],
        )

    def paper(self, p, night, uid="p"):
        p.sheet = uid
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        return A.bg_at(p, night, y)

    def canvas(self, w, h):
        """A new drawing. One made lighter to fit its budget thins only texture a reader does not miss at 1x (see
        `art.THIN`), so the canvas itself stays at full weight: the last pass still lays every candle's light."""
        p = Pix(w, h)
        if self._lite:
            A.THIN.add(p)
        return p

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The silk, and across it behind the title the shimmer the chandeliers' crystal throws (see `art.shimmer`),
        ending above the words under the title; the hall and the banquet light it themselves, once the words are set.
        The drawing keeps whether it moves, for the glints its titles' gold catches."""
        self.paper(p, night)
        p.moving = motion
        A.shimmer(p, night, motion, avoid, keep=self.mark_box(p))

    def frame(self, p, night, webs=False):
        """The gilded frame; a header's frieze parts either side of the month's mark where the header carries one,
        and runs unbroken where it does not."""
        gap = None
        if webs and self.marked:
            x0, _, x1, _ = self.mark_box(p)
            gap = (x0, x1)
        A.frame(p, night, header=webs, gap=gap)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """A valance of red velvet swags hung from the frieze, gold-fringed, a tassel where two meet (see
        `art.valance`), parting round the month's mark and its scrolls where the header carries one."""
        gap = None
        if self.marked:
            m0, _, m1, _ = self.mark_box(p)
            gap = (m0 - 15, m1 + 15)
        A.valance(p, A.TOP, p.w - A.TOP, night, gap=gap, span=span)

    def tag(self, p, x, y, w, h, night):
        """A block of red velvet by day and of gilt by night, a note's number knocked out of it, lit along its top."""
        p.rect(x, y, w, h, GOLD[3] if night else CARPET[2])
        p.hline(x, x + w, y, GOLD[4] if night else CARPET[3])

    def title_text(self, p, x, y, s, night, scale):
        """Gold leaf on carved letters (see `art.gilt_title`), the candles glinting on its gold in a moving header (see
        `art.sparkles`). The drawing keeps each line, for the scan that passes down it in a moving header."""
        w = A.gilt_title(p, x, y, s, scale, night)
        if getattr(p, "moving", False):
            A.sparkles(p, x, y, s, scale, night, seed=len(getattr(p, "titles", ())))
        p.titles = getattr(p, "titles", []) + [(x, y, s, scale, w)]
        return w

    # ---- the headers' scenes
    def scene(self, design, p, rule, night, motion):
        """On H1 the hall at the left and the banquet at the right, each where the words leave it room, and more of the
        hall's chandeliers hung from the frieze wherever the title leaves them theirs; and in a moving header the
        candles glinting on the titles' gold and the beam passing down each line of them on the hand's period."""
        if motion:
            for n, (x, y, s, scale, w) in enumerate(getattr(p, "titles", ())):
                rain.scan(p, x, y, s, scale, w, n, self.hand.glint, C["white"])
        g = rule - 1
        spans = []
        if design == "H1":
            if p.clear_of_words(3, A.TOP, 56, g + 2):
                spans.append(A.hall(p, 5, 53, g, night, motion))
            if p.clear_of_words(358, A.TOP, p.w - 2, g + 2):
                spans.append(A.banquet(p, 360, p.w - 5, g, night, motion))
            for cx in (90, p.w - 90):
                if p.clear_of_words(cx - 17, A.TOP, cx + 18, A.TOP + 38):
                    A.chandelier(p, cx, A.TOP, night, motion, drop=4)
        elif design == "H2":
            room = self._room(p, 362 - A.FIRE_HALF - 13, 362 + A.FIRE_HALF + 13, g, g - A.TOP - 2, A.FIRE_TALL + 6)
            if room:
                spans.append(A.fireplace(p, 362, g, night, motion, room))
        else:
            room = self._room(p, ARMOUR_X - 11, p.w - 5, g, g - A.TOP - 2, A.ARMOUR_LEAST)
            if room:
                spans.append(A.armour(p, ARMOUR_X, g, night, motion, room))
        return spans

    def h1_narrow(self, h, night):
        """A phone's H1, its chateau given PHONE_SCENE rows under the words and the notes set under them, however many
        notes there are."""
        self.phone_scene_rows = A.PHONE_SCENE + 4 + 10 * len(self.said(h))
        try:
            return super().h1_narrow(h, night)
        finally:
            del self.phone_scene_rows

    def scene_narrow(self, design, p, y, night):
        """A phone's H1 scene, built to the rows its words leave free over it: the whole chateau across the width under
        the words (see `art.phone_chateau`); where fewer rows are free than its least, nothing stands. A phone's H2
        and H3 stand their heroes under their words instead (see `scene_under`)."""
        if design == "H1":
            g = y - 1
            room = self._room(p, 5, p.w - 5, g, A.PHONE_SCENE - 2, A.PHONE_LEAST)
            if room:
                A.phone_chateau(p, g, night, room)

    def phone_rows(self, design, title_w):
        """The rows a phone's H2 or H3 leaves under its words for its hero, whatever the words say (see
        `scene_under`)."""
        return A.UNDER[design]

    def scene_under(self, design, p, y0, y1, night):
        """A phone's hero under its words, across the phone, standing on the rule at y1 and built to the rows free over
        it: on H2 the fireplace with its glass and its torcheres, the guest warming himself at its side (see
        `art.phone_salon`); on H3 two suits of armour guarding the trophy of swords (see `art.phone_armoury`)."""
        g = y1 - 1
        if design == "H2":
            room = self._room(p, 5, p.w - 5, g, A.UNDER["H2"] - 4, A.FIRE_TALL + 6)
            if room:
                A.phone_salon(p, g, night, room)
        else:
            room = self._room(p, 5, p.w - 5, g, A.UNDER["H3"] - 4, A.ARMOUR_LEAST)
            if room:
                A.phone_armoury(p, g, night, room)

    @staticmethod
    def _room(p, x0, x1, g, most, least):
        """The rows free of words over the floor at row g between x0 and x1, `most` at the most, keeping two rows of
        margin above and two beside; None when fewer than `least` are free."""
        for room in range(most, least - 1, -1):
            if p.clear_of_words(x0 - 2, g - room - 2, x1 + 2, g + 2):
                return room
        return None

    def section_mark(self, p, x, y, night):
        """A goblet of red wine beside SECTION A-A."""
        A.section_mark(p, x, y, night)

    def strip_mark(self, p, x, y, night):
        """A small candelabrum beside a strip's title, its candles burning green."""
        A.strip_mark(p, x, y, night)

    def rule_decor(self, p, x0, x1, y, seed, night):
        """The red carpet along a header's floor where no scene stands on it and no word lies near (see
        `art.runner`); under an element's tag, a plain rule."""
        if y > 24:
            A.runner(p, x0, x1, y, night)

    def finish(self, p, night):
        """By night every candle's green light laid on what stands near it (see `art.candlelight`)."""
        A.candlelight(p, night)

    def _finish(self, p, night):
        """The last pass, which a drawing made lighter keeps too: by night every candle's light laid on what stands
        near it (see `art.candlelight`), and then the file written as lightly as it can be, the same drawing unit
        for unit (see `Pix.compact`), the month's mark as drawn."""
        self.finish(p, night)
        p.compact(keep=("mark",))

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        """A gilt candlestick in the corner of the closing notes, its candle burning green."""
        F.footer_mark(p, x, y, night)

    def _footed(self, p, night, last=False):
        """A footer once its cells are laid: the foot of the chateau's wall along its foot, its carpet on the marble
        rising to a plinth where the cells leave it room, and the emblem hung on the wall between its sconces where
        they leave it free (see `surfaces.footing`): on a title block only after its `last` cell, the way back up."""
        after = max((b[2] for b in p.words), default=0) + 4 if last else 0
        F.footing(p, night, after=after)
        return p

    def f1(self, ft, night):
        return self._footed(super().f1(ft, night), night, last=True)

    def f2(self, ft, night):
        return self._footed(super().f2(ft, night), night)

    def f1_narrow(self, ft, night):
        return self._footed(super().f1_narrow(ft, night), night, last=True)

    def f2_narrow(self, ft, night):
        return self._footed(super().f2_narrow(ft, night), night)

    def heart(self, p, x, y):
        """A ruby of red velvet set in gold (see `surfaces.heart`)."""
        F.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        """Gilt and red velvet by turns, lit along the top and shaded along the foot."""
        F.bar(p, x0, y0, w, h, period)

    def link_colours(self, night):
        return F.link_colours(night)

    def link_top(self, p, x0, x1, y, seed, night):
        F.link_top(p, x0, x1, y, night)

    def link_icon(self, index, night, ink):
        """One of the banquet's things: the chandelier, a goblet, the candelabrum and the swords crossed, by turns."""
        return F.ICONS[F.LINK_SPRITES[index % len(F.LINK_SPRITES)]], F.icon_pal(night, ink)

    # ---- the elements (see `sheets`)
    def card_bevel(self, night):
        return E.card_bevel(night)

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        E.node_deco(p, night, x, y, w, h, seed, lid)

    def wire_ink(self, night):
        return E.wire_ink(night)

    def wire_lights(self, p, cells, night, seed):
        E.wire_lights(p, cells, night, seed)

    def dashes(self, night):
        return E.dashes(night)

    def ornament(self, kind, p, x, y, night):
        return E.ornament(kind, p, x, y, night)

    def hist_bar(self, p, bx, base, bw, v, night):
        E.hist_bar(p, bx, base, bw, v, night)

    def peak_mark(self, p, x, y, night):
        E.peak_mark(p, x, y, night)

    def dial_ring(self, p, arc, night):
        E.dial_ring(p, arc, night)

    def dial_tick(self, p, x, y, night):
        E.dial_tick(p, x, y, night)

    def dial_hub(self, p, cx, cy, night):
        E.dial_hub(p, cx, cy, night)

    def material(self, i, xx, yy, y0, y1, lift, night):
        return E.material(i, xx, yy, y0, y1, lift, night)

    def counter_cell(self, q, ox, oy, night):
        E.counter_cell(q, ox, oy, night)

    def counter_ink(self, night, dim):
        return E.counter_ink(night, dim)

    def timeline_line(self, p, x0, x1, y, night):
        E.timeline_line(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        E.release(p, x, gy, kind, night, i)

    def today_mark(self, p, x, y, night):
        E.today_mark(p, x, y, night)

    def avatar(self, p, cx, cy, i, person, night):
        E.avatar(p, cx, cy, i, person, night)

    def commit_bar(self, p, x, y, w, fill, night):
        E.commit_bar(p, x, y, w, fill, night)

    def rosette(self, p, cx, cy, r0, r1, n, night):
        E.rosette(p, cx, cy, r0, r1, n, night)

    def seal_mark(self, p, x, y, night):
        E.seal_mark(p, x, y, night)

    def placard_board(self, p, night):
        E.placard_board(p, night, self)

    def placard_mark(self, p, x, y, night):
        E.placard_mark(p, x, y, night)

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """A string of gilt beads along a badge's top, its blocks bevelled as panels (see `surfaces.badge_top`)."""
        F.badge_top(p, w, s, night, inside, self._text_y(s), (self.badge_label()[0], self.badge_gold()[0]))

    def badge_shine(self, c, y, h):
        return F.badge_shine(c, y, h)

    def plate_edge(self, block):
        return F.step(block, -1)

    def badge_label(self):
        return F.badge_label()

    def badge_gold(self):
        return F.badge_gold()

    def badge_states(self):
        return F.badge_states()

    def badge_swatches(self):
        return F.badge_swatches()

    def plate_colours(self, mode):
        return F.plate_colours(mode)

    # ---- the games
    def game_squares(self, night):
        """Polished white marble and mahogany parquet (see `surfaces.game_squares`)."""
        return F.game_squares(night)

    def game_frame(self, night):
        """Gilt with a row of beads."""
        return F.game_frame(night)

    def game_podium(self, night):
        """Veined white marble, crenellated."""
        return F.game_podium(night)


SET = Chateau()
