# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Mappa Mundi set: the medieval world map and the sea chart, in ink on parchment.

Every sheet is aged map parchment, grained and foxed and folded, in the chart's ruled border: a double rule round
all four sides with the graduated scale of degrees between, dark and light by turns. A header opens on the chart
itself: the sea washed in faded verdigris with fine wave lines drawn in ink, drifting in a moving header, the known
land in ochre with its coast inked and water-lined, the unknown land left bare with its coast dotted, and under the
rule the parchment margin the figures are written on. Across its top runs a band of graduated scales with a gilded
compass star at every station, twinkling, the stars standing either side of the top centre the header keeps for the
month's mark, and at each top corner a wind head, a cherub with its cheeks blown round, blows a stream of wind lines
in toward the map. Titles are engraved as on a copper plate, solid ink cut with an engraver's shadow of fine lines,
on a banderole whose tails fold back and are notched; by night they are gilt and catch the lantern. The wide H1 is
the map: the walled city at its river mouth among hills and trees, the compass rose with its rhumb lines raking the
sea, the cog on its dotted route, the sea serpent looping out of the waves, the whale spouting and the dragon in the
unknown land, and islands washed in ochre, vermilion and gilt wherever the words leave the sea open; by night the
chart lies on the navigator's table, the lantern standing on it with its light pooled warm over the chart and
everything on it, the edges falling dark, and a pair of brass dividers lying across it. The section header's hero
is the great compass rose, its needle swinging and settling; the strip's is the great sea serpent rearing up out of
the waves the strip's whole height, its coils rising and sinking while a cog sails her dotted route, and by night
the lantern standing beside it. A phone's H1 builds its map to the rows its words leave free, and a phone's section
and strip stand their heroes under their words at their full height: the great compass rose over the sea between
the cog, the whale and the cape with its watch tower, and the great serpent beside the coast where the walled city
stands. The footer stands on the chart's scale bar with the brass dividers at its corner and the lantern lit by
night; links are small cartouches; badges are map legend boxes; and the elements are made of the map: towers for
bars, a compass with its rose for the dial, a graduated scale for the counters, a voyage for the time line, wind
heads for the contributors, a compass rose in red wax for the seal and a cartouche for the placard.

The set is June's design of the medieval collection and is drawn in its hand (see `collections.hand`): its words are
set in the hand's inks, its lanterns burn the hand's flame, its wind heads' faces are on the hand's skin, and
nothing of its chart but the band across the top is drawn in the top centre a header keeps for the month's mark,
whether the mark is drawn or not.
"""
from __future__ import annotations

from ...holidays.designs import WIDE
from ...holidays.designs.badges import inside
from ..hand import CollectionSet
from . import art as A
from .palette import C, RAMP, TOKENS, X, step

INK, PARCH, SEA, LAND = RAMP["ink"], RAMP["parch"], RAMP["sea"], RAMP["land"]
VERM, GOLD, NIGHT = RAMP["verm"], RAMP["gold"], RAMP["night"]
# The seed each layout hands `sky`, by header: the layout says no more, so the set tells its headers apart by it.
KINDS = {2: "H1", 5: "H2", 7: "H3", 12: "H1", 15: "H2", 17: "H3"}


class MappaMundi(CollectionSet):
    collection = "medieval"
    key = "medieval-mappamundi"
    name = "Mappa Mundi"
    # What the design is, in words, for the page that shows the collection.
    tagline = (
        "Here be dragons: a sea chart in ink and verdigris, its islands inked and its beasts at the edge, read at "
        "night by lantern light.")
    about = (
        "Mappa Mundi turns every banner into a sea chart, flat and cartographic, washed in verdigris and drawn in "
        "iron gall ink on aged parchment. Wind heads blow from the corners of a ruled border with its graduated "
        "scale, and each title is engraved as on a copper plate on an unfurling banderole. Across the chart a walled "
        "city stands on its promontory, a compass rose rakes the sea with its rhumb lines, a cog follows her dotted "
        "route, and the serpent, the whale and a dragon keep to the edge of the known world. The islands are drawn as "
        "a cartographer draws land, their coasts inked and hatched, with little towns, towers, hills and trees on "
        "them, and the swell is cut in rows of short crests with water lines following every coast. Around every word "
        "the sea falls calm, so the text always reads clearly. By night the chart lies on the navigator's table, the "
        "sea gone dark, the coasts and letters gilt, and the lantern's light pooled across it beside a pair of brass "
        "dividers. The section's hero is a great compass rose, and the strip's a great sea serpent rearing out of the "
        "waves as tall as the strip with its coils behind it. On a phone the title page's map is rebuilt in whatever "
        "room the words leave, and the section and the strip stand their heroes under the words at their full "
        "height: the rose between a cog, a whale and a cape with its watch tower, and the serpent beside a coast "
        "with its walled city. The footers carry the chart as well, with a scale of leagues along the foot, open sea "
        "wherever the cells leave room, and a compass rose medallion with brass dividers at the closing corner. Links "
        "are scroll cartouches, badges are map legend boxes, and the elements are made of the map: towers with "
        "coloured roofs for the histogram, a compass for the dial, a voyage past inked islands for the timeline, "
        "cartouches for the cards and placards, wind heads for the contributors and a compass rose in red wax for the "
        "seal.")
    tokens = frozenset(TOKENS)
    # On a phone the notes are set under the words, and H1's map gets the rows its city, its rose, its cog and
    # its beasts need.
    phone_scene_rows = 64

    # ---- colour and paper
    def ink(self, night):
        """The colours its words take: its body and muted words in the hand's two inks, and its titles, rules and
        accents in the chart's own ink, gilt and vermilion."""
        return dict(
            title=GOLD[5] if night else INK[1], shadow=GOLD[2] if night else INK[4],
            body=self.hand.body[night], muted=self.hand.muted[night],
            rule=X["rule_night"] if night else X["rule_day"], accent=GOLD[4] if night else X["accent_day"],
            tag=VERM[2], tag_ink=PARCH[6],
            fill=NIGHT[4] if night else PARCH[6], dim=X["dim_night"] if night else X["dim_day"],
        )

    def paper(self, p, night, uid="p"):
        """The parchment; the drawing keeps which sheet it is (`uid`: "p" for a header or a footer, "pl" for a
        placard, "e" and a number for an element) and whether it is night, for the hooks the layout calls
        without saying."""
        p.sheet = uid
        p.night = night
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        chart = getattr(p, "chart", None)
        if chart and y < chart[1]:
            return C["sea_night"] if night else C["sea"]
        return A.night_band(p, y) if night else C["paper"]

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        """A chart has no stars: by night only the gilt of its border and its compass stars catches the light."""

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The chart a header opens on, down to its rule, and the parchment margin under it; its wave lines drift
        in a wide moving header."""
        kind = KINDS.get(seed, "H1")
        wide = p.w == WIDE
        rule = y1 + ((2 if kind == "H1" else 1) if wide else 0)
        p.sheet = "p"
        p.kind = kind
        p.words_end = max((b[3] for b in avoid), default=0)
        A.chart(p, night, kind, rule, motion=motion and wide)

    def frame(self, p, night, webs=False):
        """The ruled border; a footer (the sheet the layout frames without webs on the paper of a banner) stands
        on the chart's scale bar."""
        footer = not webs and getattr(p, "sheet", "") == "p"
        A.frame(p, night, footer=footer)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """The band of graduated scales and gilded compass stars across the top, the stars either side of the top
        centre the header keeps for the month's mark (see `art.top_band`), and the wind heads blowing at its
        corners."""
        A.garland(p, night, getattr(p, "kind", "H1"))

    def tag(self, p, x, y, w, h, night):
        """A block of vermilion a tag's letters sit on, as a chart's legend rubricates its keys: lit along its top
        and dark along its foot. The ribbon under a certificate's seal, the one tag set low on its sheet, is a
        banderole with its tails folded back."""
        if y >= 30 and h >= 9 and x >= 9 and x + w + 5 <= (100 if p.w == WIDE else 88) - 2:
            A.ribbon(p, x, y, w, h, night)
            return
        p.rect(x, y, w, h, VERM[2])
        p.hline(x, x + w, y, VERM[4])
        p.hline(x, x + w, y + h - 1, VERM[0])

    def lit(self, night):
        """How a title's letters are lit: by night gilt, their upper and left edges catching the lantern; by day
        plain ink."""
        return dict(paint=A.GILT, night=True) if night else dict(night=False)

    def title_text(self, p, x, y, s, night, scale):
        """Letters engraved as on a copper plate on a banderole (see `art.engraved_title`), lit as `lit` says."""
        return A.engraved_title(p, x, y, s, night, scale, colour=self.ink(night)["title"], lit=self.lit(night))

    # ---- the headers' scenes
    def scene(self, design, p, rule, night, motion):
        """A wide header's map, built to the room its words leave (see `art.map_h1`)."""
        return {"H1": A.map_h1, "H2": A.map_h2}.get(design, A.map_h3)(p, rule, night, motion)

    def scene_narrow(self, design, p, y, night):
        """A phone's H1 map, each piece built to the rows its words leave free (see `art.phone_h1`). A phone's H2
        and H3 stand their heroes under their words instead (see `scene_under`)."""
        if design == "H1":
            A.phone_h1(p, y, night)

    # ---- a header drawn lighter keeps its last pass
    def _last(self, p, night):
        """`p` given the last pass the layout lays on a full drawing only (see `finish`), when it is a drawing made
        lighter to fit its budget, once its words and figures are all set as a full drawing's are: a lighter
        header keeps its islands, its rhumb lines and its lantern's light. It leaves out fine texture alone, the
        parchment's grain, foxing and fold (see `art.chart`) and the faintest ring of a light pool (see
        `art.pool`), and its needle swings by turning one drawing of itself (see `art.needle`)."""
        if p.lite:
            self.finish(p, night)
        return p

    def h1(self, h, night, motion):
        return self._last(super().h1(h, night, motion), night)

    def h2(self, h, night, motion):
        return self._last(super().h2(h, night, motion), night)

    def h3(self, h, night, motion):
        return self._last(super().h3(h, night, motion), night)

    def h1_narrow(self, h, night):
        return self._last(super().h1_narrow(h, night), night)

    def h2_narrow(self, h, night):
        return self._last(super().h2_narrow(h, night), night)

    def h3_narrow(self, h, night):
        return self._last(super().h3_narrow(h, night), night)

    # ---- a phone's heroes under its words
    def phone_rows(self, design, title_w):
        """The rows a phone's H2 or H3 leaves under its words for its hero, whatever its title and its words: the
        great compass rose and the great serpent each stand at their full height, which beside the words they
        could not (see `art.PHONE_ROWS`)."""
        return A.PHONE_ROWS[design]

    def scene_under(self, design, p, y0, y1, night):
        """A phone's hero under its words: on an H2 the great compass rose over the sea with the cog, the whale and
        the cape's watch tower (see `art.phone_rose`), on an H3 the great serpent rearing beside the coast with the
        walled city on it and the cog sailing out of its harbour (see `art.phone_serpent`)."""
        {"H2": A.phone_rose, "H3": A.phone_serpent}[design](p, y0, y1, night)

    def section_mark(self, p, x, y, night):
        """A small compass star in gilt after SECTION A-A."""
        A.section_star(p, x, y, night)

    def strip_mark(self, p, x, y, night):
        """A small wind head beside a strip's title, blowing toward its map."""
        A.strip_wind(p, x - 2, y - 6, night)

    def rule_decor(self, p, x0, x1, y, seed, night):
        """The graduation of the chart's lower neatline along a rule, a tick every two pixels and a longer one
        every ten; only the short ticks on an element's rule, which runs close under its title."""
        A.degree_ticks(p, x0, x1, y, night, tall=y > 24)

    def finish(self, p, night):
        """The last pass: a header's islands, its rhumb lines and by night its lantern's light (see
        `art.finish`); and on a dial the rose on its face and the magnetised needle over it."""
        A.finish(p, night)
        if getattr(p, "dial", None):
            cx, cy, r = p.dial
            A.dial_rose(p, cx, cy, r, night)
            A.gauge_needle(p, cx, cy, r, night, self.ink(night)["accent"])

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        """The compass rose in its medallion at the corner of the closing notes with the brass dividers laid
        before it, and by night the lantern lit beside it, set by the footer's last pass once the room the words
        leave is known (see `art.footer_mark`)."""
        A.footer_mark(p, x, y, night)

    # ---- the footers' own last pass, which their layouts give no hook for
    def _footed(self, p, night):
        """A footer finished once its words are all set: the closing piece, the sea and the open chart where its
        cells leave room, and its grain (see `art.footer_finish`)."""
        A.footer_finish(p, night)
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
        """A heart painted in vermilion, 7 by 6, inked round and lit on its upper-left lobe."""
        art = [".kk.kk.", "kVLkVVk", "kVVVVVk", ".kVVVk.", "..kVk..", "...k..."]
        p.sprite(x, y, art, {"k": INK[1], "V": VERM[3], "L": VERM[5]})

    def bar(self, p, x0, y0, w, h, period=5):
        """The graphic scale as a chart's scale of leagues, dark and light by turns (the paper records the night,
        as the hook is not told)."""
        A.leagues(p, x0, y0, w, h, getattr(p, "night", False), period)

    def link_colours(self, night):
        """A cartouche of parchment inked round, dark letters; by night in shadow with a gilt edge and pale
        letters."""
        if night:
            return NIGHT[4], GOLD[2], C["body_night"], NIGHT[2]
        return PARCH[6], INK[1], C["ink"], PARCH[4]

    def link_top(self, p, x0, x1, y, seed, night):
        """The button finished as a small cartouche: rolled ends like a scroll's and a hairline under its top."""
        A.cartouche_ends(p, p.w, night)

    def link_icon(self, index, night, ink):
        return A.ICONS[A.LINK_ICONS[index % len(A.LINK_ICONS)]], A.icon_pal(night, ink)

    # ---- the elements
    def card_bevel(self, night):
        return (PARCH[6], PARCH[4]) if not night else (NIGHT[6], NIGHT[2])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A card as a cartouche, a label on the chart: a fine double rule, rolled ends and its icon inked in a
        roundel at its left (see `art.cartouche_card`)."""
        k = self.ink(night)
        A.cartouche_card(p, x, y, w, h, night, seed, k["body"], k["fill"])

    def wire_ink(self, night):
        return INK[2] if not night else GOLD[3]

    def wire_lights(self, p, cells, night, seed):
        """The wire as a ship's route: dashed, with a gilt compass star at every bend."""
        A.wire_route(p, cells, night)

    def dashes(self, night):
        return [VERM[3] if not night else VERM[4], INK[4] if not night else GOLD[2]]

    def ornament(self, kind, p, x, y, night):
        """A compass rose with its needle in a free corner of the schematic."""
        if kind == "schematic":
            if p is not None:
                A.rose(p, x + 12, y + 16, 10, night)
                A.needle(p, x + 12, y + 16, 10, night, motion=False)
            return (25, 28)
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as a tower drawn as a chart draws a city, its roof in its own colour by turns."""
        n = getattr(p, "bars", 0)
        p.bars = n + 1
        A.tower_bar(p, bx, base, bw, v, night, i=n)

    def peak_mark(self, p, x, y, night):
        """A pennant flown beside the busiest week's count."""
        A.pennant_mark(p, x, y - 1, night)

    def dial_ring(self, p, arc, night):
        """The compass's half bezel of brass with the points of the rose standing in from it."""
        cx = (arc[0][0] + arc[-1][0]) / 2
        cy = arc[0][1]
        r = (arc[-1][0] - arc[0][0]) / 2 + 1.5
        p.dial = (cx, cy, r)
        for q, c in A.bezel_cells(cx, cy, r, night).items():
            p.px(q[0], q[1], c)

    def dial_tick(self, p, x, y, night):
        p.px(x, y, GOLD[6] if not night else GOLD[5])

    def dial_hub(self, p, cx, cy, night):
        """The needle's pivot, a boss of gilt."""
        for (dx, dy, c) in ((-1, -1, GOLD[6]), (0, -1, GOLD[5]), (1, -1, GOLD[4]), (-1, 0, GOLD[5]), (0, 0, GOLD[4]),
                            (1, 0, GOLD[2]), (-1, 1, GOLD[3]), (0, 1, GOLD[2]), (1, 1, GOLD[1])):
            p.px(cx + dx, cy + dy, c)

    def material(self, i, xx, yy, y0, y1, lift, night):
        return A.material_wash(i, xx, yy, y0, y1, lift, night)

    def counter_cell(self, q, ox, oy, night):
        A.scale_cell(q, ox, oy, night)

    def counter_ink(self, night, dim):
        """A numeral engraved on the scale: ink by day and gilt by night; a leading nought cut shallower."""
        if night:
            return GOLD[3] if dim else GOLD[5]
        return INK[5] if dim else INK[1]

    def timeline_line(self, p, x0, x1, y, night):
        """The voyage up to today: a band of sea with the ship's dotted route along it."""
        if x1 - x0 >= 2:
            A.voyage_line(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        """An anchor let go from the route for a release (see `art.anchor`)."""
        A.anchor(p, x, gy, kind, night)

    def today_mark(self, p, x, y, night):
        """The cog at today's end of the voyage."""
        A.today_ship(p, x, y, night)

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor as a wind head blowing, its hair in its own colour; a bot as the north wind, old and
        bearded."""
        A.wind_avatar(p, cx, cy, i, night, bot=not person.get("initials"))

    def commit_bar(self, p, x, y, w, fill, night):
        """A contributor's share as a chart's scale bar ruled in vermilion and ink up to the share and left in
        parchment beyond it."""
        line = INK[1] if not night else GOLD[2]
        p.box(x, y, w + 2, 4, line)
        for xx in range(x + 1, x + w + 1):
            on = xx - x - 1 < fill
            seg = ((xx - x - 1) // 4) % 2 == 0
            top = (VERM[3] if seg else INK[2]) if on else (PARCH[5] if not night else NIGHT[4])
            foot = (INK[2] if seg else VERM[3]) if on else (PARCH[4] if not night else NIGHT[3])
            p.px(xx, y + 1, top)
            p.px(xx, y + 2, foot)

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """A compass rose pressed in red wax round the seal (see `art.wax_rose`)."""
        A.wax_rose(p, cx, cy, r0, r1, night)

    def seal_mark(self, p, x, y, night):
        A.fleur(p, x + 5, y, night)

    def placard_board(self, p, night):
        """A cartouche with its ends rolled like a scroll's (see `art.cartouche`)."""
        p.sheet = "pl"
        p.night = night
        A.cartouche(p, night)

    def placard_mark(self, p, x, y, night):
        """A small gilt compass star beside the placard's title."""
        A.section_star(p, x + 2, y - 2, night)

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """A badge as a box of a chart's legend: ruled round in ink, its top rule graduated with a light tick every
        fourth pixel, a lit hairline under it, a rule of ink at the seam between the label's block and the
        value's wash, and its foot a shade darker; all kept inside its shape and off its letters."""
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
        line = INK[1]
        for y in range(h):
            for x in range(w):
                if not ins(x, y):
                    continue
                c = p.get(x, y)
                if y == 0:
                    p.px(x, y, line if x % 4 != 2 else self._lift(c, 1))
                elif y == h - 1 or not ins(x - 1, y) or not ins(x + 1, y) or x == edge:
                    p.px(x, y, line)
                elif y == 1 and y not in text_rows:
                    p.px(x, y, self._lift(c, 1))
                elif y == h - 2 and y not in text_rows:
                    p.px(x, y, self._lift(c, -1))

    @staticmethod
    def _lift(c, k):
        try:
            return step(c, k)
        except KeyError:
            return c

    def badge_label(self):
        return (INK[1], PARCH[6])

    def badge_gold(self):
        return (GOLD[4], INK[1])

    def badge_states(self):
        return {"green": (SEA[1], C["white"]), "yellow": (GOLD[4], INK[1]), "red": (VERM[2], C["white"]),
                "slate": (RAMP["slate"][3], C["white"])}

    def badge_swatches(self):
        """The map's washes a written colour takes the nearest of: vermilion, the flame's orange, ochre and gilt, the
        verdigris of the sea and the green of its woods, azure, violet, bare parchment hatched, ink, slate and the
        umber of its hills."""
        G, B, V, F, S, Gr, L = (RAMP[n] for n in ("gold", "blue", "violet", "flame", "slate", "green", "land"))
        return {"vermilion": (VERM[2], C["white"], None), "orange": (F[3], INK[1], None),
                "ochre": (L[3], INK[1], None), "gilt": (G[4], INK[1], None), "verdigris": (SEA[1], C["white"], "waves"),
                "green": (Gr[3], C["white"], None), "azure": (B[3], C["white"], None),
                "violet": (V[3], C["white"], None), "parchment": (PARCH[6], INK[1], "hatch"),
                "ink": (INK[1], PARCH[6], None), "slate": (S[3], C["white"], None),
                "umber": (PARCH[0], C["white"], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        if y in text_rows:
            return c
        if pattern == "waves" and (x + (y % 4) * 3) % 8 in (0, 1) and y % 4 == 1:
            return SEA[2]
        if pattern == "hatch" and (x - y) % 4 == 0:
            return PARCH[4]
        return c

    def badge_outline(self, pattern):
        return INK[1] if pattern else None

    def badge_shine(self, c, y, h):
        return self._lift(c, 1) if y == 2 else self._lift(c, -1) if y == h - 1 else c

    def plate_colours(self, mode):
        """A plate is a legend box on the chart: the label on the parchment by day and by lantern light at night,
        the value on a wash of verdigris by day and vermilion by night with white letters; a live plate is gilt."""
        if mode == "day":
            return dict(paper=PARCH[5], dot=PARCH[3], frame=INK[1], block=SEA[1], ink=C["ink"], letters=C["white"])
        if mode == "night":
            return dict(paper=NIGHT[3], dot=NIGHT[6], frame=GOLD[2], block=VERM[2], ink=C["body_night"],
                        letters=C["white"])
        return dict(paper=GOLD[4], dot=GOLD[3], frame=INK[1], edge=GOLD[1], ink=INK[1])

    def plate_edge(self, block):
        return self._lift(block, -1)


SET = MappaMundi()
