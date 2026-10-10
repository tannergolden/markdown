# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Cathedral set: April's design in the medieval collection, stained glass in stone tracery.

Every sheet is a leaded window, grisaille quarries warm with the daylight behind them by day and lit from inside
by candles at night, in a frame of gothic stone: an arcade of pointed arches along the top, a mullion down each
side and a sill carved as a string course of small quatrefoils along the foot. Across a header's top hangs a
frieze of tracery, quatrefoils of stone glazed in cobalt round roundels of ruby whose glints twinkle, laid out
from the top centre so the month's mark covers its middle bay whole; on each top corner a winged gargoyle crouches
on its corbel with its jaws open over the glass, its eyes glowing by night. Every rule is the same string course.
Every letter of a title is a pane of coloured glass leaded in black, glowing by night, and in a moving header a
gleam crosses it on the hand's period. The words are in the collection's hand's inks, and the candles burn on its
flame. H1 stands the east end: the altar with its candles under the great rose window, a shaft of sun coming down
from the upper left through the rose onto the altar by day and an owl perching on the rose by night, and the
saints in the east window's lancets, a king, a bishop, a knight and an angel, each on its own glass, laying ruby,
cobalt, emerald and amber on the sill by day, with votive candles burning at their feet by night. H2 stands the
great window, the angel, the knight and the king in three stepped lancets under one moulded arch with a rose in its
head, and H3 the bishop in his tall lancet between two candles. A phone stands the same scenes under its words:
the east end the full width of the sheet, the great window drawn smaller and the bishop's lancet. A footer stands
on its sill and ends in the design's mark: at the right end of F1 a rose between two lancets with a candle at each
end, in the corner of F2's scale the knight in his lancet, and on a phone's the rose between two candles; the
closing notes keep a small window and a candle in an iron sconce at their corner. Links are small leaded panels;
badges are leaded panels of stone and glass; and the elements are made of glass, lead, stone, candles and the
saints' heads with their gold halos: a schematic's cards are leaded panels and its wires cames of lead soldered
where they bend.
"""
from __future__ import annotations

from ...holidays.designs import WIDE
from ...holidays.designs.badges import inside
from ...holidays.designs.banners import MARK_Y
from ...holidays.pixel import tube
from ..hand import CollectionSet
from . import art as A
from .palette import C, GLAZES, RAMP, TOKENS, X, step

LINK_SPRITES = ("rose", "fleur", "mitre", "chalice")
# The column a wide section's great window, its hero, is centred on: its sill clear of the words, and its arch
# clear of the gargoyle on the corner.
HERO_X = 356
# The column a wide strip's hero, the bishop's tall lancet, is centred on: its sill clear of the words.
STRIP_X = 376


class Cathedral(CollectionSet):
    collection = "medieval"
    key = "medieval-cathedral"
    name = "Cathedral"
    # What the design is, in words, for the page that shows the collection.
    tagline = (
        "Stained glass in stone tracery: a cathedral's east end, sunlit by day and candlelit by night.")
    about = (
        "Every sheet is a leaded window in a frame of gothic stone: pale grisaille quarries warm with the daylight "
        "behind them, lit from inside by candles at night, with an arcade along the top, mullions down the sides and "
        "a sill carved with small quatrefoils. Across a header's top hangs a frieze of tracery, quatrefoils glazed "
        "in cobalt round ruby roundels whose glints twinkle, and a winged gargoyle crouches on each corner, its eyes "
        "glowing by night. Every letter of the title is a pane of coloured glass leaded in black, and in a moving "
        "header a gleam of light crosses it every twelve seconds. The title page stands at the east end: by day a "
        "shaft of sun comes down through the great rose onto the altar, motes drifting in it, while the king, "
        "bishop, knight and angel in their lancets lay their colours on the sill; by night the candles burn and an "
        "owl comes to perch on the rose. A section stands the great window, three saints in stepped lancets under "
        "one arch with a rose in its head, and a strip the bishop in his tall lancet between two candles. Phones "
        "stand the same scenes under their words, the east end the full width of the sheet. Footers stand on their "
        "sill, their links small leaded panels, and end in the design's mark, a rose between two lancets with a "
        "candle at each end or the knight in his lancet beside the scale. Badges are leaded panels of stone and "
        "coloured glass, with live states in glass colours. The elements are made of the same glass, lead and "
        "stone: lancet histograms, a rose dial, numerals leaded into panes, a lead timeline with glass roundels and "
        "a candle at today, saints' heads with gold halos, a bishop's seal on violet silk, and schematics of leaded "
        "panels joined by soldered lead.")
    tokens = frozenset(TOKENS)
    # On a phone the notes are set under the words, and H1's east end gets the rows a full scene under them needs.
    phone_scene_rows = 70

    # ---- colour and paper
    def ink(self, night):
        R, A_, V, G, S, Du = (RAMP[n] for n in ("ruby", "amber", "violet", "gold", "stone", "dusk"))
        return dict(
            title=A_[4] if night else R[2], shadow=Du[1] if night else S[3],
            body=self.hand.body[night], muted=self.hand.muted[night],
            rule=X["rule_night"] if night else X["rule_day"], accent=A_[4] if night else X["accent_day"],
            tag=V[2], tag_ink=G[4],
            fill=C["fill_n"] if night else C["fill"], dim=X["dim_night"] if night else X["dim_day"],
        )

    def paper(self, p, night, uid="p"):
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        return A.bg_at(p, night, y)

    def clear_of_mark(self, p, x0, y0, x1, y1) -> bool:
        """Whether the box from (x0, y0) to (x1, y1), ends excluded, keeps two units clear of the box the month's
        mark takes at the top centre: every scene keeps clear of it, whether the mark is drawn there or not."""
        n = self.mark_size
        mx0, my0 = p.w // 2 - n // 2 - 2, MARK_Y - n // 2 - 2
        return not (x0 < mx0 + n + 4 and mx0 < x1 and y0 < my0 + n + 4 and my0 < y1)

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        """Fewer stars than the kit asks for: only the clear quarries show them."""
        A.stars(p, x0, y0, x1, y1, max(4, round(n * 0.5)), seed=seed, twinkling=twinkling, faint=faint, avoid=avoid)

    def frame(self, p, night, webs=False):
        """The tracery border."""
        A.frame(p, night)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """The frieze of quatrefoils glazed in cobalt and ruby hung from the coping, and a gargoyle crouched on
        each top corner (see `art.frieze`)."""
        A.frieze(p, night, seed=seed)

    def tag(self, p, x, y, w, h, night):
        """A band of violet silk a tag's gold letters sit on, lit along its top and shaded along its foot. The
        ribbon under a certificate's seal, the one tag set low on its sheet, has its ends falling either side."""
        V = RAMP["violet"]
        p.rect(x, y, w, h, V[2])
        p.hline(x, x + w, y, V[4])
        p.hline(x, x + w, y + h - 1, V[0])
        if y >= 30 and h >= 9:
            tail = min(4, x - 6, (100 if p.w == WIDE else 88) - 2 - (x + w))
            if tail >= 3:
                A.silk_tails(p, x, y, w, h, night, tail=tail)

    def title_text(self, p, x, y, s, night, scale):
        """Every letter a pane of coloured glass leaded in black (see `art.glass_title`). The drawing keeps where
        each line of the title is set, (x, y, width), for the scenes that stand beside it."""
        w = A.glass_title(p, x, y, s, night, scale)
        p.titles = getattr(p, "titles", []) + [(x, y, w)]
        p.glass = getattr(p, "glass", []) + [(x, y, s, scale, w)]
        return w

    # ---- the headers' scenes
    def section_mark(self, p, x, y, night):
        """A trefoil in glass beside SECTION A-A, from a row above the words to three under them: two rows clear
        of the title's foot above and of the tagline below."""
        A.trefoil(p, x, y, night)

    def strip_mark(self, p, x, y, night):
        """A roundel of cobalt glass with a fleur-de-lis beside a strip's title."""
        A.fleur_roundel(p, x + 6.5, y + 0.5, night)

    @staticmethod
    def _room(p, x0, x1, g, most, least):
        """The rows free of words above the floor at row g between x0 and x1, `most` at the most, keeping three
        rows of margin above and two beside; None when fewer than `least` are free."""
        for room in range(most, least - 1, -1):
            if p.clear_of_words(x0 - 2, g - room - 3, x1 + 2, g + 3):
                return room
        return None

    def scene(self, design, p, rule, night, motion):
        """The scene a wide header stands on (see `_scene`), and in a moving header the gleam that crosses each line
        of its title's glass on the hand's period. A drawing made lighter to fit its budget has no last pass (see
        `Holiday._fitted`), so here its candles lay their light on the stone, nearest the flames."""
        if motion:
            for n, line in enumerate(getattr(p, "glass", ())):
                A.title_glint(p, *line, n)
        spans = self._scene(design, p, rule, night, motion)
        if night and p.lite:
            A.candlelight(p)
        return spans

    def _scene(self, design, p, rule, night, motion):
        """The altar under its rose and the east window's lancets on H1, the great window on H2, its hero, and
        the bishop in his tall lancet on H3, each built to the rows the words leave free; where they leave the
        great window too few, H2 stands the knight in his lancet. A drawing made lighter keeps every one of them,
        and its motion; it thins only texture (see `art.pool` and `art.rose_window`)."""
        g = rule - 1
        if design == "H1":
            spans, most = [], min(78, g - 16)
            # Beside a title that runs nearly to either side, each scene draws in to rise beside it: the owl's
            # flight keeps short of the title, and the east window's lancets are eleven wide in place of thirteen
            # and further right. Each does where that lets it rise eight rows higher, or the lancets their saints.
            room = self._room(p, 4, 58, g, most, 20)
            near = self._room(p, 4, 51, g, most, 20)
            if near and near >= (room or 0) + 8:
                spans.append(A.east_end(p, 5, g, night, motion, phase=0, room=near, reach=46))
            elif room:
                spans.append(A.east_end(p, 5, g, night, motion, phase=0, room=room))
            room = self._room(p, 356, 409, g, most, 18)
            narrow = self._room(p, 364, 409, g, most, 18)
            if narrow and (narrow >= (room or 0) + 8 or (room or 0) < 38 and narrow > (room or 0)):
                spans.append(A.east_window(p, 366, g, night, motion, phase=2, room=narrow, w=11))
            elif room:
                spans.append(A.east_window(p, 358, g, night, motion, phase=2, room=room))
            return [s for s in spans if s]
        if design == "H2":
            room = self._room(p, 312, 400, g, min(90, g - 16), 60)
            if room:
                return [A.great_window(p, HERO_X, g, night, motion, phase=0, room=room)]
            room = self._room(p, 335, 382, g, min(70, g - 16), 20)
            span = A.section_window(p, 358, g, night, motion, phase=0, room=room) if room else None
            return [span] if span else []
        room = self._room(p, 355, 397, g, min(72, g - 16), 16)
        span = A.strip_scene(p, STRIP_X, g, night, motion, phase=1, room=room) if room else None
        return [span] if span else []

    def scene_narrow(self, design, p, y, night):
        """A phone's scenes beside its words: on H1 the east end under them, the full width of the sheet and
        built to the rows they leave free (see `art.phone_nave`); on H3 a roundel of cobalt glass with a
        fleur-de-lis beside the title. The heroes of H2 and H3 stand under the words (see `scene_under`)."""
        if design == "H1":
            g = y - 1
            room = self._room(p, 6, 174, g, 66, 18)
            if room:
                A.phone_nave(p, g, night, room=room)
        elif design == "H3" and p.clear_of_words(149, y - 15, 172, y + 3):
            A.fleur_roundel(p, 160.5, y - 6.5, night)

    # The rows a phone's H2 and H3 ask for under their words, where their heroes stand: on H2 enough for the great
    # window with its three saints, on H3 for the bishop in his lancet.
    UNDER = {"H2": 58, "H3": 42}
    # The column a phone's great window is centred on, and the most rows it rises.
    PHONE_HERO = (136, 64)

    def phone_rows(self, design, title_w):
        """Rows under a phone's words for its hero, whatever its title: the great window on H2 and the bishop's
        lancet on H3 stand taller than the room a title and the lines under it leave beside them."""
        return self.UNDER[design]

    def scene_under(self, design, p, y0, y1, night):
        """The hero a phone's H2 or H3 stands under its words (see `phone_rows`), at the right, on a sill over the
        rule at `y1` and built to the rows the words leave free above it, rising beside a short last line: on H2
        the great window of the wide H2 drawn smaller, the angel, the knight and the king in its three lights
        under a rose, between two candles; on H3 the bishop in his tall lancet of emerald between two candles.
        Both stand in the window's light: the glass lays its colours on the sill by day, and by night the candles
        burn and light the glass."""
        g = y1 - 1
        if design == "H2":
            cx, most = self.PHONE_HERO
            room = self._room(p, cx - 34, cx + 35, g, most, 50)
            if room:
                A.great_window(p, cx, g, night, motion=False, room=room, lw=13)
        else:
            room = self._room(p, 130, 176, g, 46, 18)
            if room:
                A.strip_scene(p, 152, g, night, motion=False, phase=1, room=room)

    def rule_decor(self, p, x0, x1, y, seed, night):
        """A string course of stone carved with small quatrefoils, standing on the rule (see
        `art.string_course`)."""
        A.string_course(p, x0, x1, y, night)

    def finish(self, p, night):
        """The last pass by night: the candles' light on the stone near them."""
        if night:
            A.candlelight(p)

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        """A small lancet window and a candle in its iron sconce beside it at the corner of the closing notes,
        the candle burning by night with its light on the window's glass (see `art.footer_mark`). The design's
        mark at a footer's end is drawn once its words are set (see `_footed`)."""
        A.footer_mark(p, x, y, night, wide=p.w == WIDE)

    # The columns the design's mark takes at the right end of a wide footer, and the most a line of its words may
    # reach and leave it standing there.
    EAST = (WIDE - 63, WIDE - 63 - 6)

    def _footed(self, p, night):
        """A footer once its words are set, standing on its step over the sill: the design's mark, the rose
        between its two lancets and a candle at each end, at the right end after the way back up wherever the
        cells leave it the room (see `art.footer_east`)."""
        x, reach = self.EAST
        if p.w == WIDE and max((b[2] for b in p.words), default=0) <= reach:
            A.footer_east(p, x, p.h - A.FOOT - 1, night)
        return p

    def f1(self, ft, night):
        return self._footed(super().f1(ft, night), night)

    def f2(self, ft, night):
        return self._footed(super().f2(ft, night), night)

    def heart(self, p, x, y):
        A.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        """A rule of lead and glass: panes of ruby and cobalt by turns, leaded between, lit from inside by night
        (the paper records which it is, as the hook is not told). Beside a footer's scale stands the design's
        mark: in the corner of a wide footer's scale cell the knight in his lancet, and on a phone's, between the
        scale and the way back up, the rose with a candle to each side (see `art.footer_knight` and
        `art.footer_rose`)."""
        night = getattr(p, "night", False)
        A.glass_bar(p, x0, y0, w, h, period, night=night)
        if p.w == WIDE:
            A.footer_knight(p, 80, p.h - A.FOOT - 1, night)
        else:
            A.footer_rose(p, 90, 34, night)

    def link_colours(self, night):
        """A cobalt pane in a rim of lead, white letters, and the glass dark along the foot."""
        B, Ld = RAMP["cobalt"], RAMP["lead"]
        return B[3], Ld[5] if night else Ld[1], C["white"], B[1]

    def link_top(self, p, x0, x1, y, seed, night):
        """The button finished as a leaded panel: the icon on a pane of ruby, a came between it and the label's
        pane of cobalt, and a streak along the top of each where the glass runs thin."""
        R, B, Ld = RAMP["ruby"], RAMP["cobalt"], RAMP["lead"]
        p.rect(1, y + 1, 12, 9, R[3])
        p.hline(1, 13, y + 9, R[1])
        p.hline(2, 12, y + 1, R[5])
        p.hline(14, p.w - 1, y + 1, B[5])
        p.vline(13, y + 1, y + 10, Ld[1])

    def link_icon(self, index, night, ink):
        return A.ICONS[LINK_SPRITES[index % len(LINK_SPRITES)]], A.icon_pal(night, ink)

    # ---- the elements
    def card_bevel(self, night):
        """The inner face of the came round a card (see `node_deco`)."""
        face, _ = A.came_tones(night)
        return (face, face)

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A card as a leaded panel: a came round it, its icon leaded in white glass into a pane of coloured
        glass with diamond quarries in the pane's corners, a came between the pane and the card's pale glass,
        and solder where the cames meet (see `art.leaded_card`)."""
        A.leaded_card(p, x, y, w, h, night, seed, self.ink(night)["body"])

    def wire_ink(self, night):
        """A wire is a came of lead: its face."""
        return A.came_tones(night)[0]

    def wire_lights(self, p, cells, night, seed):
        """The came's shaded side along the wire, and solder where it leaves its card and at every bend."""
        A.came_wire(p, cells, night)

    def dashes(self, night):
        return [RAMP["amber"][4 if night else 3], RAMP["lead"][5 if night else 3]]

    def ornament(self, kind, p, x, y, night):
        """An angel in her lancet in a free corner of the schematic."""
        if kind == "schematic":
            if p is not None:
                S = A.stone_ramp(night)
                p.hline(x, x + 17, y + 36, S[5 if night else 6])
                p.hline(x, x + 17, y + 37, S[2 if night else 3])
                A.lancet(p, x + 2, y + 36, 13, 34, night, glaze="cobalt", figure="angel", motion=False, glow=False)
            return (17, 38)
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as a lancet of coloured glass, in the glazes by turns."""
        p.bars = getattr(p, "bars", 0) + 1
        A.lancet_bar(p, bx, base, bw, v, night, GLAZES[p.bars % len(GLAZES)])

    def peak_mark(self, p, x, y, night):
        A.gold_star(p, x + 2, y + 2, night)

    def dial_ring(self, p, arc, night):
        """A half rose: a ring of stone round petals of ruby and cobalt glass between spokes of lead."""
        S, Ld = A.stone_ramp(night), RAMP["lead"]
        k = -1 if night else 0

        def colour(s, o, lam, x, y):
            if o < -0.5:
                return S[max(0, round(3 + 2.5 * lam) + k)]
            if o > 0.55:
                return Ld[1]
            seg = int(s // 8)
            if s % 8 < 1.0:
                return Ld[1]
            dark, body, thin = A.glaze_tones(("ruby", "cobalt")[seg % 2], night)
            return dark if abs(o) > 0.35 else thin if (x - y) % 5 == 0 else body
        tube(p, arc, 3.0, colour, outline=Ld[1])

    def dial_tick(self, p, x, y, night):
        p.px(x, y, RAMP["gold"][5])

    def dial_hub(self, p, cx, cy, night):
        """A roundel of ruby glass with a pin of gold."""
        A.disc(p, cx + 0.5, cy + 0.5, 3.2, "ruby", night)
        p.px(cx, cy, RAMP["gold"][5])

    def material(self, i, xx, yy, y0, y1, lift, night):
        """Panes of coloured glass by turns, each with its light along its top and its dark foot, and a lattice
        of lead across the whole."""
        glaze = ("ruby", "cobalt", "emerald", "amber", "violet")[i % 5]
        dark, body, thin = A.glaze_tones(glaze, night)
        if (xx + yy) % 8 == 0 or (xx - yy) % 8 == 0:
            return RAMP["lead"][2 if night else 3]
        return thin if lift > 0 else dark if lift < 0 else body

    def counter_cell(self, q, ox, oy, night):
        A.pane_cell(q, ox, oy, night)

    def counter_ink(self, night, dim):
        """A numeral leaded into the pane: lead by day, the candlelight's amber by night; a leading nought dimmer."""
        if night:
            return RAMP["dusk"][6] if dim else RAMP["amber"][4]
        return RAMP["lead"][4] if dim else RAMP["lead"][1]

    def timeline_line(self, p, x0, x1, y, night):
        """The came the releases stand on, up to today."""
        if x1 - x0 >= 1:
            A.came(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        """A roundel of glass for a release (see `art.glass_release`)."""
        A.glass_release(p, x, gy, kind, GLAZES[i % len(GLAZES)], night)

    def today_mark(self, p, x, y, night):
        """A candle standing on the came at today, burning by night."""
        A.today_candle(p, x, y, night)

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor as a saint's head in glass with a gold halo; a bot as a hooded brother in grey glass."""
        A.halo_head(p, cx, cy, i, night, bot=not person.get("initials"))

    def commit_bar(self, p, x, y, w, fill, night):
        """A contributor's share as a pane of amber glass in a came."""
        _, body, thin = A.glaze_tones("amber", night)
        p.box(x, y, w + 2, 4, RAMP["lead"][2 if night else 1])
        p.hline(x + 1, x + 1 + fill, y + 1, thin)
        p.hline(x + 1, x + 1 + fill, y + 2, body)

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """The tracery round the bishop's seal, petals of glass between spokes of lead."""
        A.tracery_ring(p, cx, cy, r0, r1, n, night)

    def seal_mark(self, p, x, y, night):
        A.mitre(p, x + 4, y, night)

    def placard_board(self, p, night):
        """A lancet in its stone frame: the window, the tracery, and a border of coloured panes."""
        A.paper(p, night, uid="pl")
        A.window_frame(p, night)

    def placard_mark(self, p, x, y, night):
        A.trefoil(p, x, y - 4, night)

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """The set's touch over a badge, kept inside its shape and off its letters: a came of lead along the
        top and the foot and down each end, a came at the seam between the label's stone and the value's glass,
        a streak along the top of each block where the glass runs thin, and a dark rim along its foot."""
        Ld = RAMP["lead"]
        h = s["h"]
        ty = self._text_y(s)
        text_rows = range(ty - 1, ty + (7 if s["font"] == "57" else 5) + 1)

        def ins(x, y):
            return 0 <= x < w and 0 <= y < h and inside(x, y, w, h, s["corner"])
        row = h - 2 if (h - 2) % 4 != 2 else h - 3
        first = next((x for x in range(w) if ins(x, row)), 0)
        edge = next((x for x in range(first + 1, w) if ins(x, row) and p.get(x, row) != p.get(first, row)), w)
        if edge == w and p.get(first, row) not in (self.badge_label()[0], self.badge_gold()[0]):
            edge = 0                                    # a value and no label: glass from end to end
        for y in range(h):
            for x in range(w):
                if not ins(x, y):
                    continue
                if y in (0, h - 1) or not ins(x - 1, y) or not ins(x + 1, y) or x == edge:
                    p.px(x, y, Ld[1])
                    continue
                c = p.get(x, y)
                try:
                    if y == 1 and y not in text_rows:
                        p.px(x, y, step(c, 1))
                    elif y == h - 2 and y not in text_rows:
                        p.px(x, y, step(c, -1))
                except KeyError:
                    pass

    def badge_label(self):
        return (RAMP["dusk"][2], RAMP["stone"][6])

    def badge_gold(self):
        return (RAMP["gold"][3], RAMP["lead"][0])

    def badge_states(self):
        return {"green": (RAMP["emerald"][2], C["white"]), "yellow": (RAMP["amber"][4], RAMP["lead"][0]),
                "red": (RAMP["ruby"][3], C["white"]), "slate": (RAMP["lead"][4], C["white"])}

    def badge_swatches(self):
        names = ("ruby", "cobalt", "emerald", "amber", "violet", "grisaille", "lead", "stone", "umber", "candle")
        R, B, E, A_, V, Gr, Ld, S, U, F = (RAMP[n] for n in names)
        return {"ruby": (R[3], C["white"], None), "tenne": (F[3], Ld[0], None), "amber": (A_[4], Ld[0], None),
                "emerald": (E[2], C["white"], None), "cobalt": (B[3], C["white"], None),
                "violet": (V[2], C["white"], None), "grisaille": (Gr[6], Ld[1], "quarry"),
                "lead": (Ld[1], Gr[6], None), "stone": (S[1], C["white"], None), "umber": (U[2], C["white"], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        if pattern == "quarry" and y not in text_rows and ((x + y) % 6 == 0 or (x - y) % 6 == 0):
            return RAMP["grisaille"][4]
        return c

    def badge_outline(self, pattern):
        return RAMP["grisaille"][3] if pattern == "quarry" else None

    def badge_shine(self, c, y, h):
        try:
            return step(c, 1) if y == 2 else step(c, -1) if y == h - 1 else c
        except KeyError:
            return c

    def plate_colours(self, mode):
        """A plate is a leaded panel: the label on pale stone by day and on the stone by candlelight at night,
        the value on cobalt glass by day and ruby by night, with white letters; a live plate is gold glass."""
        S, Du, B, R, G, Ld = (RAMP[n] for n in ("stone", "dusk", "cobalt", "ruby", "gold", "lead"))
        if mode == "day":
            return dict(paper=S[5], dot=S[4], frame=Ld[2], block=B[3], ink=C["ink"], letters=C["white"])
        if mode == "night":
            return dict(paper=Du[2], dot=Du[3], frame=Du[5], block=R[2], ink=C["ink_n"], letters=C["white"])
        return dict(paper=G[3], dot=G[2], frame=Ld[0], edge=G[1], ink=Ld[0])

    def plate_edge(self, block):
        return step(block, -1)


SET = Cathedral()
