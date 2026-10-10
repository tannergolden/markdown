# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Alchemist set: the laboratory at the autumn equinox, in brass and glass.

Every sheet is the limewashed wall of the laboratory, warm off-white by day with its fine cracks and the old green
and blue stains where something boiled over. By night it is the same room with no light but its own: the flasks lay
pools of green and violet on the wall round them, the furnace's mouth throws its orange up the athanor and along the
floor, the flask of gold the alchemist holds up lights his face, his beard and his sleeve in its gold, the round
window lets a cold shaft of moonlight down across the bench, and between them the shadows stay deep. Dark oak
shelves run along the top and the foot on brass brackets, with an oak upright down each side, and on a header's top
shelf stands a row of glass vessels, flasks, jars, retorts and alembics of coloured elixirs, their glass glinting by
day and by night glowing, with bubbles rising through them, in two runs either side of the top centre the header
keeps for the month's mark. Every title is the work itself: it runs from dull lead at its left to bright gold at its
right, the gold spreading through the lead letter by letter, and in a wide moving header a glint of light sweeps
across it; by night the gold glows. Headers open on the laboratory: the alchemist in his cap and robe at his
workbench holding a flask of gold up to the round window's light, the brass mortar, the open book of symbols and the
green flask on the bench before him and the carboy and the skull under it, the stuffed crocodile hung from the
ceiling over him; the athanor with the alembic on it dripping into its receiver, the retort over its spirit lamp,
and the armillary sphere and the hourglass on a shelf. By day the sun comes down through the window in a shaft
across the wall, the dust drifting in it in a moving header. A section's header has the great alembic on an athanor
as tall as its slot, beside the table of the seven metals pinned to the wall with their signs inked large, herbs
drying and a brass lantern hung from the top shelf, a shelf of books and jars, and the retort and the green flask
under them; a strip's has the great armillary sphere on its turned stand of brass, rising from the bench the
strip's full height, beside the great hourglass on its books and a candle in its candlestick, lit by night, and the
green flask and the violet jar under it. A phone's H1 builds its alchemist at his workbench, its retort and its
still under its words, closing the laboratory in round him at his full size where only forty rows are left; its H2
and H3, whatever their words say, stand their laboratories under the words across the phone: the still on its tall
athanor beside the table of the seven metals, with the retort and a skull on its books under a shelf of books and
jars, or the great armillary sphere between the hourglass and a candle on one side and the green flask, a skull
and the violet jar on the other, shelves of jars and drying herbs on the wall either side of it. A header that says
the most a page can is drawn lighter: it keeps its whole laboratory, its lights and its
motion, and thins only texture: the grain of the wall, the wood and the brass, the old stains and the soot, the
faint outer steps of its lights, and the top shelf's tile of vessels, cut to its first three. The footer is the
bottom shelf: once its words are set the crucible stands at the corner of its notes, cold lead in it by day and
molten gold over its flame by night, and books and jars, the skull, the carboy, candles and the low things stand
along the shelf and on its cells' rules wherever the words leave room, with the crocodile and herbs hung over an
empty stretch of wall. Links are corked phials with paper labels; badges are brass plates with an engraved border;
and the elements are made of brass and glass: graduated cylinders of clear glass, a balance, apothecary jars, a
distillation tube, apothecary labels in brass frames joined by glass tubing, alchemists in their caps, the ouroboros
in red wax and a brass-bound cabinet door.

The set is September's design of the medieval collection and is drawn in its hand (see `collections.hand`): its
words are set in the hand's inks on a wall within the hand's bands, its furnace, its lamps, its candles and its
lantern burn the hand's flame while its elixirs glow their own green and violet, the moon through its window is the
hand's, and its people are on the hand's skin.
"""
from __future__ import annotations

from ...holidays.designs import NARROW
from ...holidays.designs.badges import inside
from ...holidays.pixel import sphere, tube
from ..hand import CollectionSet
from . import art as A
from .palette import C, ELIXIRS, RAMP, TOKENS, X, step

OAK, BRASS, LEAD, GOLD, GLASS = RAMP["oak"], RAMP["brass"], RAMP["lead"], RAMP["gold"], RAMP["glass"]
GREEN, VIOLET, RED, BLUE, AMBER, BONE = (RAMP[n] for n in ("green", "violet", "red", "blue", "amber", "bone"))
SHEET_RULE = 20   # the row an element's sheet rules off its tag and title at


class Alchemist(CollectionSet):
    collection = "medieval"
    key = "medieval-alchemist"
    name = "Alchemist"
    # What the design is, in words, for the page that shows the collection.
    tagline = (
        "The alchemist's laboratory, lit by its own fires and elixirs, where every title turns from lead to gold.")
    about = (
        "Every sheet is the limewashed wall of an alchemist's laboratory, framed in dark oak shelves on brass "
        "brackets, with a row of glass vessels of coloured elixirs along the top. Every title is the work itself, "
        "running from dull lead at its left to bright gold at its right, and in a moving header a glint sweeps across "
        "it. The alchemist stands at his workbench holding a flask of gold up to the round window, the stuffed "
        "crocodile hung over him, while the great alembic distils on its furnace at the other end of the room. By day "
        "the sun comes down through the window in a shaft across the wall, with dust drifting in it. By night the "
        "room has no light but its own: the flasks lay pools of green and violet on the wall, the furnace throws "
        "orange up its front, the gold flask lights the alchemist's beard, and a cold shaft of moonlight falls across "
        "the bench, with deep shadow between. A section's header pins the table of the seven metals to the wall "
        "beside a lantern and drying herbs, and a strip's stands the great armillary sphere on its brass stand the "
        "strip's full height beside the great hourglass and a candle. Phones close the laboratory in round their "
        "words, keeping the alchemist at his full size, and stand the still beside the table of metals or the great "
        "sphere between its shelves under the words, whatever the title. The footer "
        "is the bottom shelf, with the crucible of cold lead by day and molten gold by night, and books, jars and a "
        "skull wherever the words leave room. Links are corked phials, badges are engraved brass plates, and the "
        "elements are made of brass and glass, from graduated cylinders to apothecary labels joined by glass tubing.")
    tokens = frozenset(TOKENS)
    # A phone's laboratory: the alchemist at his workbench, its notes set over it, and ten rows more for each
    # note past the second, so a page that says the most still leaves him forty rows (see `h1_narrow`).
    _scene_rows = 64

    @property
    def phone_scene_rows(self):
        return self._scene_rows

    # ---- colour and paper
    def ink(self, night):
        """The colours its words take: its body and muted words in the hand's two inks, and its titles, rules and
        accents in the laboratory's own lead, gold, oak and cinnabar."""
        return dict(
            title=GOLD[4] if night else LEAD[1], shadow=RAMP["dusk"][0] if night else RAMP["lime"][3],
            body=self.hand.body[night], muted=self.hand.muted[night],
            rule=X["rule_night"] if night else OAK[2], accent=GOLD[5] if night else X["accent_day"],
            tag=BRASS[4], tag_ink=OAK[0],
            fill=C["fill_n"] if night else C["fill"], dim=X["dim_night"] if night else X["dim_day"],
        )

    def paper(self, p, night, uid="p"):
        """The limewashed wall; the drawing keeps which sheet it is (`uid`: "p" for a header or a footer) and
        whether it is night, for the hooks the layout calls without saying."""
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        return A.bg_at(p, night, y)

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        """A wall has no stars: by night they show only through the round window."""

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The wall: by night dark but where the room's own lights fall on it, which each scene lays with its
        lights (see `scene`)."""
        self.paper(p, night)

    def frame(self, p, night, webs=False):
        """The oak shelves and uprights: on a header (the sheet the layout frames with webs) the top shelf stands
        lower, on its brass brackets, for the vessels; a footer (the sheet framed without webs on the banner
        paper, wide or on a phone) stands on a deeper bottom shelf."""
        A.frame(p, night, header=webs, footer=not webs and getattr(p, "sheet", "") == "p")

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """The row of glass vessels standing on the top shelf from upright to upright, in two runs either side of
        the top centre the header keeps for the month's mark (see `art.vessels`)."""
        A.vessels(p, A.POST + 2, p.w - A.POST - 2, night)

    def tag(self, p, x, y, w, h, night):
        """An engraved brass plate a tag's letters sit on: lit along its top, dark along its foot, a screw at each
        end where it is long enough. The ribbon under a certificate's seal, the one tag set low on its sheet, is
        green silk with its ends falling either side."""
        if y >= 30 and h >= 9 and getattr(p, "seal_at", None):
            A.silk(p, x, y, w, h, night)
            return
        p.rect(x, y, w, h, BRASS[4])
        p.hline(x, x + w, y, BRASS[6])
        p.hline(x, x + w, y + h - 1, BRASS[2])
        if w >= 16:
            p.px(x + 1, y + h // 2, BRASS[1])
            p.px(x + w - 2, y + h // 2, BRASS[1])

    def title_text(self, p, x, y, s, night, scale):
        """Lead turning to gold along the line (see `art.transmuted_title`)."""
        return A.transmuted_title(p, x, y, s, night, scale)

    # ---- the headers' scenes
    def section_mark(self, p, x, y, night):
        """The sign for gold beside SECTION A-A, from a row above the words to three under them."""
        A.sun_sign(p, x, y - 1, night)

    def strip_mark(self, p, x, y, night):
        """A phial of green elixir beside a strip's title, glowing by night."""
        A.phial(p, x, y - 7, night)

    @staticmethod
    def _room(p, x0, x1, g, most, least):
        """The rows free of words above the bench's top at row g between x0 and x1, `most` at the most, keeping
        three rows of margin above and two beside; None when fewer than `least` are free."""
        for room in range(most, least - 1, -1):
            if p.clear_of_words(x0 - 2, g - room - 3, x1 + 2, g + 3):
                return room
        return None

    def scene(self, design, p, rule, night, motion):
        """A wide header's laboratory, on the bench along the rule: on H1 the alchemist's corner at the left and
        the still at the right; on H2 the great alembic beside the section's title; on H3 the great armillary
        sphere rising the strip's full height beside the hourglass. Each is built to the rows its words leave free
        over it, and by night lit by its own lights alone, their pools kept to its own room so the wall between
        them and the words stays dark."""
        lite = p.lite
        foot = rule - 2

        def lit(x0, x1, room, build, *args):
            A.open_pools(p)
            span = build(p, *args, rule, night, motion, lite, room)
            A.lay_pools(p, x0, foot - room, x1, rule)
            return span
        if design == "H1":
            spans = []
            room = self._room(p, 5, 53, foot, foot - 15, 16)
            if room:
                spans.append(lit(5, 410, room, A.lab_left, 5))
            room = self._room(p, 362, 409, foot, foot - 15, 26)
            if room:
                spans.append(lit(5, 410, room, A.lab_right, 362))
            return [s for s in spans if s]
        if design == "H2":
            room = self._room(p, 311, 409, foot, foot - 15, 30)
            span = lit(5, 410, room, A.lab_section, 311) if room else None
            return [span] if span else []
        room = self._room(p, 359, 409, foot, foot - 15, 22)
        span = lit(5, 410, room, A.lab_strip, 359) if room else None
        return [span] if span else []

    def scene_narrow(self, design, p, y, night):
        """A phone's H1 laboratory, built to the rows its words leave free: the alchemist at his workbench at the
        left of the rule, the retort and his books in the middle and the still at the right; where fewer rows are
        free than a piece's smallest build needs, it does not stand. By night each is lit by its own lights, their
        pools kept to the rows the words leave. A phone's H2 and H3 stand their laboratories under their words
        instead (see `scene_under`)."""
        if design != "H1":
            return
        A.open_pools(p)
        foot = y - 2
        rooms = [self._room(p, 4, 54, foot, 58, 12), self._room(p, 60, 120, foot, 58, 24),
                 self._room(p, 150, 175, foot, 58, 16)]
        if rooms[0]:
            A.phone_lab(p, 4, y, night, rooms[0])
        if rooms[1]:
            A.phone_middle(p, 60, 120, y, night, rooms[1])
        if rooms[2]:
            A.phone_still(p, 175, y, night, rooms[2])
        free = [r for r in rooms if r]
        A.lay_pools(p, 5, foot - min(free) if free else y, NARROW - 5, y)

    def h1_narrow(self, h, night):
        """A phone's H1, its laboratory given ten rows more for each note it sets past the second, so the
        alchemist keeps his full size under the most a page can say."""
        self._scene_rows = 64 + 10 * max(0, len(self.said(h)) - 2)
        try:
            return super().h1_narrow(h, night)
        finally:
            self._scene_rows = 64

    def phone_rows(self, design, title_w):
        """The rows a phone's section or strip header leaves under its words for its laboratory, whatever the words
        say: its hero at its full height would reach into the top shelf beside the words, so it always stands under
        them (see `scene_under`)."""
        return A.UNDER[design]

    def scene_under(self, design, p, y0, y1, night):
        """A phone's laboratory under its words, across the phone on the bench along the rule at `y1` and as tall as
        the rows the words leave free over it: on H2 the still on its tall athanor beside the table of the seven
        metals, the retort and a skull on its books at its right (`art.phone_section`); on H3 the great armillary
        sphere on its stand between the hourglass and a candle, and the green flask, a skull and the violet jar
        (`art.phone_strip_under`). By night each is lit by its own lights, their pools kept to its rows."""
        A.open_pools(p)
        foot = y1 - 2
        room = self._room(p, 6, NARROW - 6, foot, A.UNDER[design] + 2, 12) or 12
        if design == "H2":
            A.phone_section(p, 6, NARROW - 6, y1, night, room)
        else:
            A.phone_strip_under(p, 6, NARROW - 6, y1, night, room)
        A.lay_pools(p, 5, foot - room, NARROW - 5, y1)

    def rule_decor(self, p, x0, x1, y, seed, night):
        """The front of the bench along a header's rule; along a sheet's rule under its tag, the lip of a shelf."""
        if y > SHEET_RULE:
            A.bench_edge(p, x0, x1, y, night)
        else:
            A.shelf_lip(p, x0, x1, y, night)

    def finish(self, p, night):
        """The last pass: on an instruments sheet the balance's beam and pans hung on the dial; by night each
        flask's and flame's light on what stands near it, and on a sheet that is not a header the flasks' glow
        in its corners."""
        if getattr(p, "dial", None):
            A.balance(p, *p.dial, night)
        if night:
            A.lights(p)
            if getattr(p, "sheet", "") != "p":
                A.night_glows(p)

    # ---- the footers' own last pass, which their layouts give no hook for
    def _stocked(self, p, night):
        """A footer as the laboratory's bottom shelf: once its words are set, the shelf along its foot, four rows
        deep or three where the words come down to it, and the crucible and the goods standing on it and on its
        cells' rules wherever the words leave room (see `art.stock`)."""
        A.stock(p, night, self.ink(night)["rule"], getattr(p, "mark", None))
        return p

    def f1(self, ft, night):
        return self._stocked(super().f1(ft, night), night)

    def f2(self, ft, night):
        return self._stocked(super().f2(ft, night), night)

    def f1_narrow(self, ft, night):
        return self._stocked(super().f1_narrow(ft, night), night)

    def f2_narrow(self, ft, night):
        return self._stocked(super().f2_narrow(ft, night), night)

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        """The crucible over its flame, the footer's mark: the corner of the closing notes the layout keeps for
        it is kept, and the crucible stands nearest it once the words are all set (see `_stocked`), cold lead
        in it by day and molten gold over its flame by night."""
        p.mark = (x + 8, y)

    def heart(self, p, x, y):
        A.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        """The graphic scale's bar in lead and gold by turns, the lead dull and the gold lit along its top."""
        A.scale_bar(p, x0, y0, w, h, period, night=getattr(p, "night", False))

    def link_colours(self, night):
        """A phial's paper label with dark letters on it, in glass."""
        return (BONE[5] if not night else BONE[4], GLASS[2], C["ink"], BONE[3])

    def link_top(self, p, x0, x1, y, seed, night):
        """The button finished as a corked phial lying on its side, its elixir chosen by its label (see
        `art.phial_link`)."""
        A.phial_link(p, x0, x1, y, seed, night)

    def link_icon(self, index, night, ink):
        return A.link_icon(index, night, ink)

    # ---- the elements
    def card_bevel(self, night):
        return (C["fill_n"], C["fill_n"]) if night else (C["fill"], C["fill"])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A card as an apothecary's label in a frame of brass with a rivet at each corner, its words on parchment
        and its icon engraved in a round brass medallion (see `art.brass_card`)."""
        A.brass_card(p, x, y, w, h, night, self.ink(night)["body"], seed)

    def wire_ink(self, night):
        """A wire is a tube of glass with the green elixir running in it: the elixir."""
        return GREEN[5] if night else GREEN[4]

    def wire_lights(self, p, cells, night, seed):
        """The wire as tubing of clear glass two units wide with the elixir in it and a line of light along it, a
        brass collar where it leaves its card and at each bend (see `art.tube_over`)."""
        A.tube_over(p, cells, night)

    def dashes(self, night):
        return [BRASS[4 if night else 3], GLASS[3 if night else 2]]

    def ornament(self, kind, p, x, y, night):
        """A skull on three books with the hourglass beside them, in a free corner of the schematic."""
        if kind == "schematic":
            if p is not None:
                A.books(p, x, y + 21, night)
                A.skull(p, x + 3, y + 21 - len(A.BOOKS), night)
                A.hourglass(p, x + 16, y + 21, night, motion=False)
            return (26, 22)
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as a graduated cylinder of clear glass filled to its height with an elixir, each week its
        own by turns, glowing and with bubbles caught in it by night (see `art.cylinder_bar`). The drawing keeps
        the last cylinder, for the busiest week's stopper."""
        n = getattr(p, "bars", 0)
        p.bars = n + 1
        p.last_bar = (bx, base, bw, v)
        A.cylinder_bar(p, bx, base, bw, v, night, ELIXIRS[n % len(ELIXIRS)])

    def peak_mark(self, p, x, y, night):
        """A glint of gold beside the busiest week's count, and a cork in its cylinder, glowing gold by night (the
        layout marks the busiest week straight after drawing its cylinder)."""
        A.glint_mark(p, x + 1, y + 1, night)
        if getattr(p, "last_bar", None):
            A.stopper(p, *p.last_bar, night)

    def dial_ring(self, p, arc, night):
        """The balance's graduated arc of brass, lit along its upper left; the drawing keeps the dial, so the beam
        and the pans can be hung on it once the words are set (see `finish`)."""
        cx = (arc[0][0] + arc[-1][0]) / 2
        cy = arc[0][1]
        r = (arc[-1][0] - arc[0][0]) / 2 + 1.5
        p.dial = (cx, cy, r)
        p.hand_ink = self.ink(night)["accent"]
        k = -1 if night else 0

        def colour(s, o, lam, x, y):
            if o > 0.5:
                return BRASS[1]
            return BRASS[max(0, min(6, round(2.5 + 3 * lam) + k))]
        tube(p, arc, 2.2, colour, outline=OAK[0])

    def dial_tick(self, p, x, y, night):
        p.px(x, y, OAK[0])
        p.px(x + 1, y + 1, BRASS[6 if not night else 5])

    def dial_hub(self, p, cx, cy, night):
        """The balance's pivot: a brass knob."""
        sphere(p, cx + 0.5, cy - 0.5, 3.2, BRASS, lo=1, hi=6)

    def material(self, i, xx, yy, y0, y1, lift, night):
        """The alchemical matters by turns: gold, quicksilver, cinnabar, verdigris, azure, sulphur, salt and
        lead (see `art.matter`)."""
        return A.matter(i, xx, yy, y0, y1, lift, night)

    def counter_cell(self, q, ox, oy, night):
        A.jar_cell(q, ox, oy, night)

    def counter_ink(self, night, dim):
        """A numeral written on the jar's paper label in iron-gall ink, a brown no word before it on the sheet is
        lettered in, so its letters are set after the jars; a leading nought in a paler hand."""
        return BONE[2] if dim else RED[0]

    def timeline_line(self, p, x0, x1, y, night):
        """The glass distillation tube the releases hang from, up to today."""
        if x1 - x0 >= 2:
            A.glass_tube(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        """A flask hung from the tube for a release (see `art.hanging_flask`)."""
        A.hanging_flask(p, x, gy, kind, night, i)

    def today_mark(self, p, x, y, night):
        """The bubbling flask sitting on the tube at today's end."""
        A.today_flask(p, x, y, night)

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor as an alchemist in robe and cap, his looks drawn from his name; a bot as a homunculus in
        its flask."""
        if person.get("initials"):
            A.alchemist_head(p, cx, cy, person, i, night)
        else:
            A.homunculus(p, cx, cy, night)

    def commit_bar(self, p, x, y, w, fill, night):
        """A contributor's share as gold filling a tube of glass."""
        k = -1 if night else 0
        p.box(x, y, w + 2, 4, GLASS[2 + k])
        p.hline(x + 1, x + w + 1, y + 1, GLASS[5 + k])
        p.hline(x + 1, x + w + 1, y + 2, GLASS[4 + k])
        p.hline(x + 1, x + 1 + fill, y + 1, GOLD[5])
        p.hline(x + 1, x + 1 + fill, y + 2, GOLD[3])

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """The ouroboros in red wax round the seal (see `art.ouroboros`); the drawing keeps where the seal is, so
        its ribbon knows itself."""
        p.seal_at = (cx, cy)
        A.ouroboros(p, cx, cy, r0, r1, night)

    def seal_mark(self, p, x, y, night):
        A.sun_sign(p, x + 3, y - 1, night)

    def placard_board(self, p, night):
        """A brass-bound cabinet door over the whole card (see `art.door`)."""
        p.sheet, p.night = "pl", night
        A.door(p, night)

    def placard_mark(self, p, x, y, night):
        A.sun_sign(p, x, y - 4, night)

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """The set's touch over a badge, kept inside its shape and off its letters: a rim of brass round it, lit
        along its top and left and dark along its foot and right, a seam of brass where the label meets the
        value, an engraved line inside the rim along the top where the letters leave room, and a screw at each
        end of it."""
        h = s["h"]
        ty = self._text_y(s)
        text_rows = range(ty - 1, ty + (7 if s["font"] == "57" else 5) + 1)

        def ins(x, y):
            return 0 <= x < w and 0 <= y < h and inside(x, y, w, h, s["corner"])
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
                if y == 0 or not ins(x - 1, y):
                    p.px(x, y, BRASS[5])
                elif y == h - 1 or not ins(x + 1, y):
                    p.px(x, y, BRASS[2])
                elif x == edge:
                    p.px(x, y, BRASS[3])
                elif y == 1 and y not in text_rows:
                    try:
                        p.px(x, y, step(p.get(x, y), -1))
                    except KeyError:
                        pass
        for x in (2, w - 3):
            if w > 8 and ins(x, 1) and 1 not in text_rows:
                p.px(x, 1, BRASS[0])

    def badge_label(self):
        """Blackened brass, its letters bright brass."""
        return (BRASS[0], BRASS[6])

    def badge_gold(self):
        return (GOLD[4], OAK[0])

    def badge_states(self):
        """The elixirs a live badge shows its state in."""
        return {"green": (GREEN[3], C["white"]), "yellow": (GOLD[4], OAK[0]),
                "red": (RED[3], C["white"]), "slate": (LEAD[4], C["white"])}

    def badge_swatches(self):
        """The elixirs and matters a written colour takes the nearest of."""
        return {"cinnabar": (RED[3], C["white"], None), "amber": (AMBER[3], OAK[0], None),
                "gold": (GOLD[4], OAK[0], "sheen"), "green": (GREEN[3], C["white"], None),
                "ultramarine": (RAMP["lapis"][3], C["white"], None), "violet": (VIOLET[3], C["white"], None),
                "salt": (BONE[6], OAK[0], "grain"), "oak": (OAK[1], BONE[6], None),
                "lead": (LEAD[4], C["white"], None), "clay": (RAMP["clay"][3], C["white"], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        if y in text_rows:
            return c
        if pattern == "sheen" and (x - y) % 7 == 0:
            return GOLD[6]
        if pattern == "grain" and (x * 3 + y * 5) % 11 == 0:
            return BONE[4]
        return c

    def badge_outline(self, pattern):
        return BONE[3] if pattern == "grain" else None

    def badge_shine(self, c, y, h):
        try:
            return step(c, 1) if y == 2 else step(c, -1) if y == h - 2 else c
        except KeyError:
            return c

    def plate_colours(self, mode):
        """A plate is a brass plate by day, blackened brass by night, its value in green elixir by day and violet
        by night with white letters; a live plate is gold."""
        if mode == "day":
            return dict(paper=BRASS[5], dot=BRASS[4], frame=BRASS[2], block=GREEN[3], ink=OAK[0],
                        letters=C["white"])
        if mode == "night":
            return dict(paper=BRASS[0], dot=BRASS[1], frame=BRASS[3], block=VIOLET[3], ink=BRASS[6],
                        letters=C["white"])
        return dict(paper=GOLD[4], dot=GOLD[3], frame=OAK[0], edge=GOLD[1], ink=OAK[0])

    def plate_edge(self, block):
        return step(block, -1)


SET = Alchemist()
