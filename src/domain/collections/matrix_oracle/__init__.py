# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Oracle set: cookies in the oven and a spoon that bends, August's design in the Matrix collection, drawn in the
collection's hand.

Every sheet is the wall of a small kitchen in 1999, papered in apricot with pinstripes and sprigs of flowers, tone on
tone, and by night the same paper in a warm dark that deepens under the ceiling. Oak trim runs down its sides and
along its foot, and across a header's top a band of glazed cream tiles, each with a little blue flower, over an oak
rail hung with the kitchen's spoons, ladles and whisks, one spoon among them bent; the band parts either side of the
top centre for the month's mark. Across a header's sky the steam of the baking billows under the rail, soft clouds
of it with curls turning over on top, drifting slowly to the right behind the title. Titles are cookies: each letter
golden dough studded with chocolate chips, its edge baked dark and its rim pale and crumbly where the light catches
it, the cookie's thickness baked brown under each face over its shadow on the wallpaper, a crumb or two fallen under
it; by night the oven's green light catches its edges and glows round it, and in a moving header the beam passes
down it on the hand's period. Headers open on the kitchen, standing on its checked linoleum: the almond range under
its hood, its window glowing phosphor round the cookies inside and its clock lit, a tray of cookies steaming on its
cooktop; the counter beside it with a red mug steaming, the tiles behind it and the window over it hung with gingham,
a hazy city beyond it by day and the code falling past it by night, when the oven's light pools on the floor and
shimmers in its gloss. At the right a tall doorway opens on the room beyond: a jug of sunflowers on a little table
under the clock, toy blocks hanging in the air, a child in a saffron robe sitting cross-legged on a cushion at the
threshold and bending a spoon without touching it, the spoon shining in phosphor by night and lighting his face and
the floor round him, and a black cat that walks past behind him, and then walks past again exactly as it did before,
faint and torn by a glitch. On an H2 the dresser wall stands at the right, risen the full height: an oak dresser with
its rack of plates, a radio on its shelf whose dial glows by night, the cat asleep on its crown, and before it the
kitchen table under its gingham cloth with a plate of cookies and the blue vase rocking at the edge and falling, a
pendant lamp hung over it that throws its cone of light down by night. On an H3 the refrigerator's corner, the strip's
full height: the almond refrigerator with its magnets and its note, its door ajar by night and its light pooling on
the floor, the cat sitting before it. A phone's H1 holds the whole kitchen under its words, the range and the
counter, the table with its vase and the doorway with the child and the cat, and its H2 and H3 stand the dresser
wall and the refrigerator under theirs, whatever they say. The footers stand on the kitchen's linoleum, with the
kitchen's corner after a title block's last cell, a cabinet with the cookie jar and the red mug on it under a night
light that burns and flickers by night and the cat sitting beside it, and a bitten cookie marks the closing notes;
a link button is a long cookie iced in chocolate along its top; a badge wears a jar's gingham cap along its top; the
elements are recipe cards tied with baker's twine, stacks of cookies, an oven's dial, tiles, jars on a shelf, an egg
timer, cookies with initials piped on them, a pie's crust round a seal and a cross-stitch sampler; and the games
stand on boards of the kitchen's glazed tiles, cream and Delft blue, framed in oak, their winners on blocks of
chocolate edged in a paper doily's lace.
"""
from __future__ import annotations

from ...holidays.designs import WIDE
from ...holidays.designs.badges import inside
from ...holidays.designs.materials import Podium, Stuff
from ..hand import CollectionSet
from .. import rain
from . import art as A
from .palette import C, RAMP, TOKENS, X, step

FLAME, OAK, PAPER, UMBER, DOUGH = RAMP["flame"], RAMP["oak"], RAMP["paper"], RAMP["umber"], RAMP["dough"]
CHOC, SUN, LEAF, RED, STEEL = RAMP["choc"], RAMP["sun"], RAMP["leaf"], RAMP["red"], RAMP["steel"]
GLAZE, BLUE, ROBE, CAT = RAMP["glaze"], RAMP["blue"], RAMP["robe"], RAMP["cat"]


class Oracle(CollectionSet):
    key = "matrix-oracle"
    name = "Oracle"
    collection = "matrix"
    tagline = "Cookies in the oven and a spoon that bends, in a 1999 kitchen papered in apricot."
    about = (
        "Every sheet is the wall of a small kitchen in 1999, papered in apricot with pinstripes and sprigs of "
        "flowers, warm and dark by night, trimmed in oak, with a band of glazed tiles across the top over a rail "
        "hung with spoons and ladles, one spoon bent, and the steam of the baking drifting under it. Titles are "
        "cookies, golden dough studded with chocolate chips, baked dark at the edge and standing off the wall; by "
        "night the oven's green light catches them and glows round them. Headers open on the kitchen, the almond "
        "range with its window glowing phosphor and a tray of cookies steaming on top, the counter with a mug under "
        "a gingham window where the code falls past by night; and through a tall doorway on the room beyond, a child "
        "in a saffron robe bending a spoon without touching it, toy blocks floating over him, and a black cat that "
        "walks past, and then walks past again exactly as before. A section stands the oak dresser with its plates "
        "and the table where the blue vase tips and falls under a pendant lamp; a strip, the refrigerator with the "
        "cat sitting before it, its door ajar by night. The footers stand on the linoleum with the cookie jar after "
        "their last cell, links are iced cookies, badges wear a jar's gingham cap, the elements are recipe cards, "
        "cookies, tiles and twine, and the games are played on glazed tiles, their winners standing on chocolate.")
    tokens = frozenset(TOKENS)

    # ---- colour and paper
    def ink(self, night):
        """The words in the hand's two inks; a title's ink the dough's gold by night and its baked brown by day (the
        cookies themselves are lettered in `art.cookie_title`), the rules in oak by day and in the dark of the paper
        by night, and labels in a red-brown by day and phosphor by night."""
        return dict(
            title=DOUGH[4] if night else DOUGH[1], shadow=UMBER[0] if night else PAPER[3],
            body=self.hand.body[night], muted=self.hand.muted[night],
            rule=X["rule_night"] if night else X["rule_day"], accent=FLAME[4] if night else X["accent_day"],
            tag=OAK[5] if not night else FLAME[2], tag_ink=OAK[0] if not night else UMBER[0],
            fill=UMBER[2] if night else PAPER[6], dim=X["dim_night"] if night else X["dim_day"],
        )

    def paper(self, p, night, uid="p"):
        p.sheet = uid
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        return A.bg_at(p, night, y)

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The wallpaper; and on a wide header, whose layout keeps the title's box and the words under it clear
        (`avoid`), the steam of the baking curling across the kitchen under the rail, behind the title, ending above
        the words (see `art.vapour`)."""
        self.paper(p, night)
        if not (p.w == WIDE and len(avoid) > 1):
            return
        (a0, a1), mark = avoid[:2], self.mark_box(p)
        if a1[1] - 1 - (A.TOP + 1) < 12:
            return
        title = (a0[0] + 2, a0[1] + 9, a0[2] - 2, a0[3] - 1)
        A.vapour(p, night, motion, (A.EDGE + 1, A.TOP + 1, p.w - A.EDGE - 1, a1[1] - 1), title, mark)

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        """None: a kitchen has a ceiling, not a sky. Its night is the wallpaper in the dark, deepening under the
        ceiling (see `art.paper`)."""

    def top_centre(self, p) -> tuple:
        """The columns of a header's top kept for the month's mark, its box and two units either side."""
        x0, _, x1, _ = self.mark_box(p)
        return x0, x1

    def frame(self, p, night, webs=False):
        """The oak trim, and across a header's top the band of tiles over its rail, parting for the month's mark
        when the header carries it."""
        A.frame(p, night, header=webs, clear=self.top_centre(p) if (webs and self.marked) else None)

    def _finish(self, p, night):
        """The last pass, which a drawing made lighter keeps too: the kit's last light at full weight only (see
        `finish`), then the file written as lightly as it can be, the same drawing unit for unit, the month's mark
        left as it is drawn (see `Pix.compact`)."""
        if not p.lite:
            self.finish(p, night)
        p.compact(keep=("mark",))

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """The spoons, ladles and whisks hung from the rail across a header's top, a bent spoon among them, none in
        the columns kept for the month's mark (see `art.utensils`)."""
        A.utensils(p, A.EDGE + 88, p.w - A.EDGE - 80, night, clear=self.top_centre(p))

    def section_mark(self, p, x, y, night):
        """The bent spoon beside SECTION A-A, steel by day and phosphor by night (see `art.spoon_mark`)."""
        A.spoon_mark(p, x, y, night)

    def strip_mark(self, p, x, y, night):
        """A red toy block beside a strip's title (see `art.block_mark`)."""
        A.block_mark(p, x, y, night)

    def rule_decor(self, p, x0, x1, y, seed, night):
        """Cookies lying on the rule here and there, crumbs beside them, where no scene stands (see
        `art.crumbs_on_rule`)."""
        A.crumbs_on_rule(p, x0, x1, y, seed, night)

    def tag(self, p, x, y, w, h, night):
        """A block of oak by day, of phosphor by night, a note's number knocked out of it."""
        p.rect(x, y, w, h, FLAME[2] if night else OAK[5])
        p.hline(x, x + w, y, FLAME[3] if night else OAK[6])

    def title_text(self, p, x, y, s, night, scale):
        """Baked as cookies (see `art.cookie_title`). The drawing keeps each line, for the beam that passes down it
        in a moving header."""
        w = A.cookie_title(p, x, y, s, night, scale)
        p.titles = getattr(p, "titles", []) + [(x, y, s, scale, w)]
        return w

    # ---- the headers' scenes
    @staticmethod
    def _reach(p, x0, y0, y1, limit):
        """How far right from x0 a band from row y0 to y1 runs clear of words, two units kept; at most `limit`."""
        x = x0
        while x < limit and p.clear_of_words(x - 2, y0 - 2, x + 3, y1 + 3):
            x += 1
        return x

    @staticmethod
    def _top(p, x0, x1, g, most):
        """The highest row from which the columns x0 to x1 stand clear of words down to the ground at row g, two
        units kept; no higher than `most`."""
        y = most
        while y < g and not p.clear_of_words(x0 - 2, y - 2, x1 + 2, g + 2):
            y += 1
        return y

    def scene(self, design, p, rule, night, motion):
        """On H1 the kitchen at the left, its window running as far right as the words let it, and the room beyond
        at the right; and in a moving header the beam passing down each line of the title on the hand's period."""
        if motion:
            for n, (x, y, s, scale, w) in enumerate(getattr(p, "titles", ())):
                rain.scan(p, x, y, s, scale, w, n, self.hand.glint, C["white"])
        g = rule - 1
        spans = []
        if design == "H1":
            top = A.TOP + 3
            if p.clear_of_words(2, g - 30, 60, g + 2):
                ktop = self._top(p, 5, 33, g, top)
                reach = self._reach(p, 56, top + 2, g - 37, 140)
                spans.append(A.kitchen(p, 5, g, night, motion, reach - 1, ktop, top))
            if p.clear_of_words(359, g - 26, 411, g + 2):
                rtop = self._top(p, 361, 410, g, top)
                spans.append(A.room(p, 361, 410, g, night, motion, rtop))
        elif design == "H2":
            x0 = 308
            while x0 < 330 and not p.clear_of_words(x0 - 2, g - 40, 413, g + 2):
                x0 += 1
            if x0 < 330:
                spans.append(A.dresser_wall(p, x0, 410, g, night, motion, self._top(p, x0 + 34, 410, g, A.TOP + 3)))
        else:
            x0 = 352
            while x0 < 366 and not p.clear_of_words(x0 - 2, A.TOP + 3, 413, g + 2):
                x0 += 1
            if x0 < 366:
                spans.append(A.fridge_corner(p, x0, 410, g, night, motion, A.TOP + 3))
        return spans

    # ---- a phone's scenes
    UNDER = {"H2": 62, "H3": 62}    # the rows a phone's H2 and H3 ask for under their words, whatever they say
    PHONE_KITCHEN = 58              # the rows a phone's H1 gives its kitchen under its words
    _notes = 0                      # the notes of the phone H1 being drawn

    @property
    def phone_scene_rows(self):
        """The rows a phone's H1 leaves under its words for its kitchen: PHONE_KITCHEN, and ten more for each note,
        which are set under the words before it."""
        return self.PHONE_KITCHEN + 4 + 10 * self._notes

    def h1_narrow(self, h, night):
        """A phone's H1, the rows for its kitchen counting its notes (see `phone_scene_rows`)."""
        self._notes = len(self.said(h))
        try:
            return super().h1_narrow(h, night)
        finally:
            self._notes = 0

    def phone_rows(self, design, title_w):
        """The rows a phone's H2 or H3 leaves under its words for its hero, whatever the words say: beside the words
        a hero has no room to stand at its height, so it always stands under them (see `scene_under`)."""
        return self.UNDER[design]

    def scene_narrow(self, design, p, y, night):
        """A phone's H1 scene, standing on the rule at `y` in the rows its words leave over it: the whole kitchen
        across the phone, the range under its hood and the counter at the left, the table with the blue vase tipping
        off it in the middle, and the doorway at the right with the child bending his spoon and the cat walking past
        behind him; where fewer rows are free than the doorway needs, the kitchen alone. A phone's H2 and H3 stand
        their heroes under their words instead (see `scene_under`)."""
        if design != "H1":
            return
        g = y - 1
        top = self._top(p, 5, 60, g, g - self.PHONE_KITCHEN)
        if top > g - 40:
            return
        spans = [A.kitchen(p, 5, g, night, False, 0, top, g)]
        dtop = self._top(p, 120, 172, g, g - self.PHONE_KITCHEN)
        if dtop <= g - 46:
            A.floor(p, 59, 120, g, night)
            A.kitchen_table(p, 66, 98, g - 4, night, False)
            spans.append(A.room(p, 123, 172, g, night, False, dtop))

    def scene_under(self, design, p, y0, y1, night):
        """A phone's hero under its words, from its last words at row y0 to its rule at y1, across the phone: on H2
        the dresser wall, the table with its vase and the lamp over it, the dresser with its plates, its radio and
        the cat asleep on its crown; on H3 the refrigerator, its door ajar by night, the cat sitting before it, and
        the counter beside it with the jug of sunflowers and the mug (see `art.fridge_kitchen`)."""
        g = y1 - 1
        top = max(y0 + 3, self._top(p, 6, 174, g, y0 + 3))
        if design == "H2":
            A.dresser_wall(p, 26, 150, g, night, False, top + 8, ceiling=top)
        else:
            A.fridge_kitchen(p, 8, 172, g, night, top)

    # ---- the footers and links
    def _footed(self, p, night, last=False):
        """A footer as the kitchen's: its linoleum along its foot, under every cell where the words leave it room,
        and on a title block, after its `last` cell, the kitchen's corner, the cabinet with the cookie jar and the
        mug on it, the night light over it and the black cat sitting by it (see `art.footing` and `art.emblem`)."""
        g = A.footing(p, night) - 1
        if last:
            after = max((b[2] for b in p.words), default=0) + 4
            A.emblem(p, after, p.w - A.EDGE, g, night)
        return p

    def f1(self, ft, night):
        return self._footed(super().f1(ft, night), night, last=True)

    def f2(self, ft, night):
        return self._footed(super().f2(ft, night), night)

    def f1_narrow(self, ft, night):
        return self._footed(super().f1_narrow(ft, night), night, last=True)

    def f2_narrow(self, ft, night):
        return self._footed(super().f2_narrow(ft, night), night)

    def footer_mark(self, p, x, y, night):
        """A cookie with a bite out of it in the corner of the closing notes."""
        A.cookie_bitten(p, x + 2, y - 2, night)

    def link_top(self, p, x0, x1, y, seed, night):
        """Chocolate icing along the cookie's top edge over its rim, dripping at each end, its face lit along its
        left and baked darker down its right (see `art.icing`)."""
        fill, _, _, shade = self.link_colours(night)
        p.vline(1, y + 1, y + 9, DOUGH[6] if not night else DOUGH[5])
        p.vline(p.w - 2, y + 2, y + 9, shade)
        A.icing(p, x0 - 1, x1 + 1, y, night, seed)

    def heart(self, p, x, y):
        """A sugar cookie in the shape of a heart, iced red (see `art.heart`)."""
        A.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        """The curtains' gingham, red and cream (see `art.gingham_bar`)."""
        A.gingham_bar(p, x0, y0, w, h, period)

    def link_colours(self, night):
        """A long cookie: golden dough baked brown at its edge and along its foot, lettered in chocolate."""
        if night:
            return DOUGH[4], DOUGH[1], CHOC[0], DOUGH[2]
        return DOUGH[5], DOUGH[1], CHOC[1], DOUGH[3]

    def link_icon(self, index, night, ink):
        """A thing from the kitchen or the room beyond for each link, by turns: the spoon, the cat, the mug and
        a toy block."""
        return A.ICONS[A.LINK_ICONS[index % len(A.LINK_ICONS)]], A.icon_pal(night, ink)

    # ---- the elements
    def card_bevel(self, night):
        return (UMBER[5], UMBER[0]) if night else (GLAZE[6], PAPER[3])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A card as a recipe card: a red rule along its top, gingham down its icon cell's edge, a corner turned
        down and, on a card with a lid, a red pin through its top (see `art.recipe_card`)."""
        A.recipe_card(p, x, y, w, h, night, lid)

    def wire_ink(self, night):
        return RED[4] if night else RED[3]

    def wire_lights(self, p, cells, night, seed):
        """The wire as baker's twine, red and cream twisted (see `art.twine`)."""
        A.twine(p, cells, night)

    def dashes(self, night):
        return [RED[4], DOUGH[4]] if night else [RED[3], OAK[3]]

    def ornament(self, kind, p, x, y, night):
        """The blue jug of sunflowers in a free corner of the schematic."""
        if kind == "schematic":
            if p is not None:
                A.bouquet(p, x + 9, y + 34, night, tall=True)
            return (20, 34)
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as a stack of cookies (see `art.cookie_stack`)."""
        A.cookie_stack(p, bx, base, bw, v, night)

    def peak_mark(self, p, x, y, night):
        A.star_sticker(p, x, y + 1, night)

    def dial_ring(self, p, arc, night):
        """The dial's ring as an oven's temperature ring, red over its hottest third (see `art.oven_dial`)."""
        A.oven_dial(p, arc, night)

    def dial_tick(self, p, x, y, night):
        p.px(x, y, OAK[0])
        p.px(x + 1, y + 1, GLAZE[6] if not night else GLAZE[2])

    def dial_hub(self, p, cx, cy, night):
        """The oven's knob (see `art.knob_hub`)."""
        A.knob_hub(p, cx, cy, night)

    def material(self, i, xx, yy, y0, y1, lift, night):
        """Each file type wrapped in one of the kitchen's stuffs by turns (see `art.wrapper`)."""
        return A.wrapper(i, xx, yy, y0, y1, lift, night)

    def counter_cell(self, q, ox, oy, night):
        """A glazed tile (see `art.tile_cell`)."""
        A.tile_cell(q, ox, oy, night)

    def counter_ink(self, night, dim):
        """A numeral glazed on the tile, dark by day and lit like the oven's clock by night; a leading nought
        fainter."""
        if night:
            return GLAZE[1] if dim else FLAME[5]
        return GLAZE[2] if dim else CHOC[0]

    def timeline_line(self, p, x0, x1, y, night):
        """An oak shelf, the releases standing on it (see `art.shelf`)."""
        A.shelf(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        """A cookie jar, a cookie, a crumb, a cookie's outline or the mixing bowl (see `art.release_jar`)."""
        A.release_jar(p, x, gy, kind, night)

    def today_mark(self, p, x, y, night):
        A.egg_timer(p, x, y, night)

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor as a cookie with their initials piped on it; a bot, a toaster (see `art.cookie_face`)."""
        A.cookie_face(p, cx, cy, i, person, night)

    def commit_bar(self, p, x, y, w, fill, night):
        A.gingham_fill(p, x, y, w, fill, self.wire_ink(night), night)

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """A pie's crimped crust round the seal (see `art.pie_crust`)."""
        A.pie_crust(p, cx, cy, r0, r1, n, night)

    def seal_mark(self, p, x, y, night):
        A.spoon_mark(p, x + 3, y, night)

    def placard_board(self, p, night):
        """A cross-stitch sampler in an oak frame (see `art.sampler`)."""
        A.sampler(p, night)

    def placard_mark(self, p, x, y, night):
        A.sunflower_mark(p, x, y, night)

    # ---- the badges
    def badge_label(self):
        """A label of chocolate, lettered in pale dough."""
        return (CHOC[1], DOUGH[6])

    def badge_gold(self):
        """A live label in the sunflowers' gold, lettered in chocolate."""
        return (SUN[4], CHOC[0])

    def badge_states(self):
        return {"green": (LEAF[2], C["white"]), "yellow": (SUN[4], CHOC[0]), "red": (RED[3], C["white"]),
                "slate": (STEEL[3], C["white"])}

    def badge_swatches(self):
        """The kitchen's colours: the mug's red, the robe's saffron, the sunflowers' gold, the basil's green, the
        tiles' blue, the cat's plum black, the oak, chocolate, steel, the tiles' cream, the apricot paper and the
        far room's sage."""
        return {"tomato": (RED[3], C["white"], None), "saffron": (ROBE[4], CHOC[0], None),
                "sunflower": (SUN[4], CHOC[0], None), "basil": (LEAF[2], C["white"], None),
                "delft": (BLUE[2], C["white"], None), "plum": (CAT[5], C["white"], None),
                "oak": (OAK[2], C["white"], None), "cocoa": (CHOC[1], C["white"], None),
                "steel": (STEEL[5], CHOC[0], None), "cream": (GLAZE[6], OAK[0], "tile"),
                "apricot": (PAPER[3], CHOC[1], None), "sage": (X["far_day"], CHOC[1], None)}

    def plate_colours(self, mode):
        """A plate is a glazed tile: cream dotted with its little blue flowers by day, the glaze in the dark by
        night, framed in oak, its value iced red with cream letters; a live plate is the sunflowers' gold."""
        if mode == "day":
            return dict(paper=GLAZE[5], dot=BLUE[4], frame=OAK[2], block=RED[2], ink=OAK[0], letters=GLAZE[6])
        if mode == "night":
            return dict(paper=UMBER[2], dot=UMBER[4], frame=OAK[3], block=RED[2], ink=GLAZE[5], letters=GLAZE[6])
        return dict(paper=SUN[4], dot=SUN[3], frame=OAK[0], edge=SUN[2], ink=CHOC[0])

    def badge_top(self, p, w, s, seed, night):
        """A jar's gingham cap over a badge, kept inside its shape and off its letters: red checks on cream along
        its top two rows, the cloth's shadow under it where no letter sits, and the label's block and the value's
        each glazed, lit along its left end and in shade along its right and its foot, a seam where they meet."""
        h = s["h"]
        ty = self._text_y(s)
        text_rows = range(ty - 1, ty + (7 if s["font"] == "57" else 5) + 1)
        k = -1 if night else 0

        def ins(x, y):
            return 0 <= x < w and 0 <= y < h and inside(x, y, w, h, s["corner"])
        # Where the label's block ends: the first change of colour along two rows under the letters at once (a
        # plate's dots change one row at a time, and its frame is the first pixel of a row alone).
        row = h - 2 if (h - 2) % 4 != 2 else h - 3
        first = next((x for x in range(w) if ins(x, row) and ins(x, row - 1)), 0)
        edge = next((x for x in range(first + 2, w) if ins(x, row) and p.get(x, row) != p.get(x - 1, row)
                     and p.get(x, row - 1) != p.get(x - 1, row - 1)), w)
        checks = ((RED[3 + k], RED[5 + k]), (RED[5 + k], GLAZE[6 + k]))
        for y in range(h):
            for x in range(w):
                if not ins(x, y):
                    continue
                if y <= 1:
                    p.px(x, y, checks[y][(x // 2) % 2])
                    continue
                c = p.get(x, y)
                try:
                    if (y == 2 and y not in text_rows) or y == h - 1:
                        p.px(x, y, step(c, -1))
                    elif not ins(x - 1, y) or x == edge:
                        p.px(x, y, step(c, 1))
                    elif not ins(x + 1, y) or x == edge - 1:
                        p.px(x, y, step(c, -1))
                except KeyError:
                    pass

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        """A glazed tile's little blue flowers, in the rows its letters leave."""
        if pattern == "tile" and y not in text_rows and x % 6 == 3:
            return BLUE[4]
        return c

    def badge_outline(self, pattern):
        """A tile's grout round it."""
        return GLAZE[3] if pattern == "tile" else None

    def badge_shine(self, c, y, h):
        """Plastic glazed: lit under the cap, in shade along its foot."""
        try:
            return step(c, 1) if y == 2 else step(c, -1) if y == h - 1 else c
        except KeyError:
            return c

    def plate_edge(self, block):
        try:
            return step(block, -1)
        except KeyError:
            return block

    # ---- the games
    def game_squares(self, night):
        """A board of the kitchen's glazed tiles, cream and Delft blue, each with the gleam of its glaze, a tone
        down by night as every board of the year is."""
        return Stuff(GLAZE, 4 if night else 5, "ivory"), Stuff(BLUE, 2 if night else 3, "ivory")

    def game_frame(self, night):
        """A frame of the kitchen's oak trim, mitred at its corners."""
        return Stuff(OAK, 3, "wood"), "wood"

    def game_podium(self, night):
        """A podium of chocolate, its sheen running across each block, edged in a paper doily's lace."""
        return Podium(Stuff(CHOC, 4, "satin"), "lace", Stuff(GLAZE, 6))


SET = Oracle()
