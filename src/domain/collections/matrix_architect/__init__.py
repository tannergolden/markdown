# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Architect set: the room of screens where the year is reviewed, December's design in the Matrix collection,
drawn in the collection's hand.

Every sheet is a wall of the white room, warm white by day and by night grey-black, lit only by its screens, laid in
large panels with fine joints between them; its frame is a stack of small televisions in pale grey down its sides and
along its foot, and along a header's top a row of larger sets, switched off but for a dim test card in every third,
parting either side of the month's mark, which sits among them as one more screen, a cable slung under them between
grey ties with a tally light under each. Across a header's sky, behind the title, the room's far wall is a wall of
screens, their glass a warm grey by day and dark by night, a light sweeping slowly across them and a few of them left
on, flickering with pictures of the year, the wall ending above the words under the title. Titles are a video wall,
every unit of a letter a little television, charcoal cases round green screens by day casting their shadow on the wall
and by night the screens themselves burning in the dark; in a moving header a few of them flicker on their own and the
terminal's beam passes down them on the hand's period. Headers open on the year in review: at the left three big sets
rising the height of the wall, showing the code running, the two pills held out and the white rabbit; at the right
four more showing the train, the hovercraft, the pods and the chateau's chandelier over the console, its monitor
showing the room itself, and before it the Architect seated in his tall white wingback, the sets' cables lying along
the floor between. The section header stands the Architect before a tower of sets three across at its right, his pen
held up to the screens and the tower's cables rising from it to the ceiling, a little set glowing beside SECTION A-A;
the strip stands his white wingback empty before a column of sets, his pen on its seat, the column's cables rising
over it so that it stands the strip's full height, a little set with the code running beside the strip's title. On a
phone the whole room stands under the words, the big sets, the console and the Architect in his chair and a tower of
sets; the section header stands him before his tower with his chair waiting behind him, and the strip his empty chair
by its column with a big set showing the code. Every screen burns on the hand's phosphor, and by night their green
light falls on the plastic, the leather, the steel and the Architect, and pools on the floor. A header too heavy for
its budget is drawn lighter by thinning only its texture: the titles' outline, which the screens' own cases already
edge, and by night the titles' bloom and their shadow, black on the dark wall.

Every footer stands on the front edge of the Architect's console, a brass rail over its rows of keys, its meter bridge
of little tubes rising behind it wherever the cells leave the wall free, and a title block stands a set on it after
its last cell, showing the room itself; a little set glows in the corner of its notes, the heart burns on a screen and
the graphic scale's bar is a row of tubes, lit and dark by turns. A link button is a set's charcoal plastic with vents
along its top, its letters green, led by a television, the white wingback, the pen or the white rabbit. A badge wears a
band of charcoal plastic along its top with a green power light, and a plate is the white room's wall in a charcoal
frame. The elements are the room's: monitor cards wired with black cables and tally lights, level meters of little
tubes, a charcoal bezel on a brass knob, the bytes shown as what a screen shows, counters glowing in little tubes, a
cable with a set for every release and the pen at today, contributors on sets, a seal ringed in a test card's rings
over the white rabbit, and a placard of the white room in its frame of little sets. The boards are the white room's
tiles and brushed pale grey plastic in a frame of a set's charcoal, and the Hall of Fame's winners stand on a plain
podium of the wingback's white leather.
"""
from __future__ import annotations

from ...holidays.designs.badges import inside
from ..hand import CollectionSet
from .. import rain
from . import art as A
from . import sheets as E
from . import surfaces as F
from .palette import C, RAMP, TOKENS, X

DUSK, FLAME, GLASS, PLASTIC, WALL = RAMP["dusk"], RAMP["flame"], RAMP["glass"], RAMP["plastic"], RAMP["wall"]
# Where the year's pictures are shown: on the big sets at the left, on the screens the wall across the sky leaves on
# where the title leaves room for them, and on the sets at the right and the console's monitor.
BIG_MONTHS = ("rain", "choice", "rabbit")
SKY_MONTHS = ("exit", "dojo", "rooftop", "oracle")
RIGHT_MONTHS = ("subway", "hovercraft", "harvest", "chateau", "architect")
VIGIL_X = 358     # where an H3's chair and its column of sets begin: two units clear of the furthest its words reach


class Architect(CollectionSet):
    key = "matrix-architect"
    name = "Architect"
    collection = "matrix"
    tagline = "The white room of screens where the year is reviewed, every set showing a picture from a month gone by."
    about = (
        "Every sheet is a wall of the white room, warm white by day and grey-black by night, lit only by its screens, "
        "and its frame is a stack of small televisions in pale grey down its sides and along its foot, with a row of "
        "larger sets along a header's top and a cable slung under them, the month's mark sitting among them as one "
        "more screen. Across the sky, behind the title, the room's far wall is a wall of screens, a light sweeping "
        "slowly across it and a few of them left on, flickering with pictures of the year. Titles are a video wall, "
        "every unit of a letter a little television casting its shadow on the wall by day and burning in the dark by "
        "night. Headers open on the year in review: three big sets at the left showing the code running, the two "
        "pills held out and the white rabbit; four more at the right showing the train, the hovercraft, the pods and "
        "the chateau's chandelier over the console, its monitor showing the room itself; and before it the Architect "
        "seated in his tall white wingback, the cables wiring the sets together lying along the floor. The section "
        "header stands the Architect before a tower of sets with his pen held up to the screens, and the strip his "
        "empty chair before a column of sets rising its full height, the cables of both climbing to the ceiling. On a "
        "phone the whole room lies under the words, and the Architect and his empty chair stand under theirs. Every "
        "screen burns on the hand's phosphor, the code runs down January's tube, a ripple of snow passes through the "
        "year's sets now and then, and by night their green light falls on the plastic, the leather, the steel and "
        "the Architect, and pools on the floor. Footers stand on the edge of the Architect's console with its meter "
        "bridge rising behind it and a set showing the room after the last cell; links are charcoal sets with vents "
        "along their tops, and badges wear a band of charcoal plastic with a green power light. The elements are "
        "built of the room's sets, cables and tubes: level meters, a bezel on a brass knob, a cable with a set for "
        "every release and the pen at today, and a seal ringed in a test card's rings over the white rabbit; the "
        "boards are the white room's tiles and pale grey plastic, and the winners stand on a plain podium of the "
        "wingback's white leather.")
    tokens = frozenset(TOKENS)

    # ---- colour and paper
    def ink(self, night):
        """The words in the hand's two inks; the titles' colour the bezels' dark plastic by day and the phosphor by
        night."""
        return dict(
            title=FLAME[4] if night else PLASTIC[1], shadow=DUSK[0] if night else WALL[3],
            body=self.hand.body[night], muted=self.hand.muted[night],
            rule=X["rule_night"] if night else X["rule_day"], accent=FLAME[4] if night else FLAME[0],
            tag=FLAME[2] if night else GLASS[3], tag_ink=DUSK[0] if night else FLAME[4],
            fill=DUSK[5] if night else WALL[6], dim=X["dim_night"] if night else X["dim_day"],
        )

    def paper(self, p, night, uid="p"):
        p.sheet = uid
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        return A.bg_at(p, night, y)

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The room's wall, and across its top, behind the title, the far wall of screens switched off, the light
        sweeping slowly across it, a few of its screens left on and flickering wherever the title leaves them clear
        (see `art.sky_wall`), ending above the words under the title."""
        self.paper(p, night)
        p.moving = motion
        rects = A.sky_wall(p, night, motion, avoid)
        A.lit_screens(p, night, motion, rects, avoid, SKY_MONTHS)

    def frame(self, p, night, webs=False):
        """The stack of televisions; a header's row of sets parts either side of the month's mark where the header
        carries one, and runs unbroken where it does not."""
        gap = None
        if webs and self.marked:
            x0, _, x1, _ = self.mark_box(p)
            gap = (x0, x1)
        A.frame(p, night, header=webs, gap=gap)

    def tag(self, p, x, y, w, h, night):
        """A dark tube by day and a lit one by night, a note's number knocked out of it."""
        p.rect(x, y, w, h, FLAME[2] if night else GLASS[3])
        p.hline(x, x + w, y, FLAME[3] if night else GLASS[5])

    def title_text(self, p, x, y, s, night, scale):
        """A video wall (see `art.video_title`), a few of its screens flickering on their own in a moving header (see
        `art.title_flicker`). The drawing keeps each line, for the scan that passes down it in a moving header."""
        w = A.video_title(p, x, y, s, scale, night)
        if getattr(p, "moving", False):
            A.title_flicker(p, x, y, s, scale, night, seed=len(getattr(p, "titles", ())))
        p.titles = getattr(p, "titles", []) + [(x, y, s, scale, w)]
        return w

    # ---- the headers' scenes
    def scene(self, design, p, rule, night, motion):
        """On H1 the big sets at the left and the Architect at his console under four more sets at the right, each
        where the words leave it room, a ripple of snow running through the year's sets in a moving header; and in a
        moving header a few of the titles' screens flickering and the beam passing down each line of them on the
        hand's period."""
        if motion:
            for n, (x, y, s, scale, w) in enumerate(getattr(p, "titles", ())):
                rain.scan(p, x, y, s, scale, w, n, self.hand.glint, C["white"])
        g = rule - 1
        spans = []
        if design == "H1":
            if p.clear_of_words(3, 16, 56, g + 2):
                spans.append(A.big_wall(p, 5, g, BIG_MONTHS, night, motion))
            if p.clear_of_words(358, A.TOP, p.w - 2, g + 2):
                spans.append(A.study(p, 360, p.w - 5, g, RIGHT_MONTHS, night, motion))
        elif design == "H2":
            room = self._room(p, 318, p.w - 5, g, g - A.TOP - 2, A.TV_H + A.STAND + 2)
            if room:
                spans.append(A.audience(p, 318, p.w - 5, g, night, motion, room))
        else:
            room = self._room(p, VIGIL_X, p.w - 5, g, g - A.TOP - 2, A.TV_H + A.STAND + 2)
            if room:
                spans.append(A.vigil(p, VIGIL_X, p.w - 5, g, night, motion, room))
        A.snow(p, A.tubes(p), motion)
        return spans

    @staticmethod
    def _room(p, x0, x1, g, most, least):
        """The rows free of words over the floor at row g between x0 and x1, `most` at the most, keeping two rows of
        margin above and two beside; None when fewer than `least` are free."""
        for room in range(most, least - 1, -1):
            if p.clear_of_words(x0 - 2, g - room - 2, x1 + 2, g + 2):
                return room
        return None

    def section_mark(self, p, x, y, night):
        """A little set beside SECTION A-A, its tube glowing."""
        A.section_mark(p, x, y, night)

    def strip_mark(self, p, x, y, night):
        """A little set beside a strip's title, the code running down its tube."""
        A.strip_mark(p, x, y, night)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """A cable slung under the row of sets along the top, sagging between grey ties with a tally light under each
        (see `art.cable_garland`), parting round the month's mark where the header carries one."""
        gap = None
        if self.marked:
            m0, _, m1, _ = self.mark_box(p)
            gap = (m0 - 3, m1 + 3)
        A.cable_garland(p, A.EDGE + 1, p.w - A.EDGE - 1, night, gap=gap, span=66 if p.w > 300 else 52)

    def h1_narrow(self, h, night):
        """A phone's H1, its room given PHONE_SCENE rows under the words and the notes set under them, however many
        notes there are."""
        self.phone_scene_rows = A.PHONE_SCENE + 4 + 10 * len(self.said(h))
        try:
            return super().h1_narrow(h, night)
        finally:
            del self.phone_scene_rows

    def scene_narrow(self, design, p, y, night):
        """A phone's H1 scene, built to the rows its words leave free over it: the whole room across the width under
        the words (see `art.phone_room`); where fewer rows are free than its least, nothing stands. A phone's H2 and H3
        stand their heroes under their words instead (see `scene_under`)."""
        if design == "H1":
            g = y - 1
            room = self._room(p, 5, p.w - 5, g, A.PHONE_SCENE - 2, A.PHONE_LEAST)
            if room:
                A.phone_room(p, g, night, room)

    def phone_rows(self, design, title_w):
        """The rows a phone's H2 or H3 leaves under its words for its hero, whatever the words say."""
        return A.UNDER[design]

    def scene_under(self, design, p, y0, y1, night):
        """A phone's hero under its words, across the phone, standing on the rule at y1 and built to the rows free over
        it: on H2 the Architect standing before a tower of sets, his chair waiting behind him (see
        `art.phone_audience`); on H3 his empty chair turned to a column of sets, a big set with the code running at the
        left (see `art.phone_vigil`)."""
        g = y1 - 1
        room = self._room(p, 5, p.w - 5, g, A.UNDER[design] - 4, A.TV_H + A.STAND + 2)
        if room:
            (A.phone_audience if design == "H2" else A.phone_vigil)(p, g, night, room)

    def rule_decor(self, p, x0, x1, y, seed, night):
        """The cables that wire the sets together, along a header's floor where no scene stands on it and no word
        lies near (see `art.cables`); under an element's tag, a plain rule."""
        if y > 24:
            A.cables(p, x0, x1, y, night)

    def finish(self, p, night):
        """By night every screen's green light laid on what stands near it (see `art.screenlight`)."""
        A.screenlight(p, night)

    def _finish(self, p, night):
        """The last pass, which a drawing made lighter keeps too: by night every screen's light laid on what stands
        near it (see `art.screenlight`), and then the file written as lightly as it can be, the same drawing unit
        for unit (see `Pix.compact`), the month's mark as drawn."""
        self.finish(p, night)
        p.compact(keep=("mark",))

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        """A little set in the corner of the closing notes, its tube glowing."""
        F.footer_mark(p, x, y, night)

    def _footed(self, p, night, last=False):
        """A footer once its cells are laid: the edge of the Architect's console along its foot, its keys lit, rising
        into its meter bridge where the cells leave it room, and a set showing the room itself standing on it where
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
        """A heart burning on a screen in the phosphor (see `surfaces.heart`)."""
        F.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        """A row of little tubes, lit and dark by turns, as the console's level meter lights."""
        F.bar(p, x0, y0, w, h, period)

    def link_colours(self, night):
        return F.link_colours(night)

    def link_top(self, p, x0, x1, y, seed, night):
        F.link_top(p, x0, x1, y, night)

    def link_icon(self, index, night, ink):
        """One of the room's things: a television, the white wingback, the pen and the white rabbit, by turns."""
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
        """A band of a set's charcoal case along a badge's top, its vents and its power light, its blocks bevelled as
        panels (see `surfaces.badge_top`)."""
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
        """The white room's tiles and brushed pale grey plastic (see `surfaces.game_squares`)."""
        return F.game_squares(night)

    def game_frame(self, night):
        """A set's charcoal plastic, screwed at its corners."""
        return F.game_frame(night)

    def game_podium(self, night):
        """The wingback's white leather, plain."""
        return F.game_podium(night)


SET = Architect()
