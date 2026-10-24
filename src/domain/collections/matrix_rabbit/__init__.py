# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Rabbit set: follow the white rabbit, April's design in the Matrix collection, drawn in the collection's hand.

Every sheet is a page of a storybook in spring, pale yellow-green and sprigged with small printed flowers by day and
by night a deep indigo garden under stars that are the code showing through the sky, held in a frame of clipped
hedge, and across a header's top a deeper hedge set with roses, some white roses half painted red, parting either side
of the month's mark; across the sky behind the title a pack of playing cards tumbles on the wind, every card turning
over and over, ending above the words. Every letter of a title is printed on a playing card, red or black by its suit
with a pip in its corner, the cards dealt a little askew and lying a tone down in the garden's dusk by night; in a
moving header the terminal's beam passes down them on the hand's period. The H1 opens on Wonderland after Tenniel: at
the left the White Rabbit in his tweed jacket and blue waistcoat, bounding along and looking at his gold watch under
an arch of roses, among tulips and Easter eggs in the grass, a butterfly fluttering round the arch by day and the moon
in it by night; at the right an old tree, the Cheshire Cat grinning on its bough by day and by night only his grin,
the cat coming and going round it, its roots arching over the rabbit hole, the code rising up out of it a glyph at a
time, faint by day and by night bright, its light lying on the roots, the grass and everything by the hole, with
toadstools beside it, a little bottle with a tag on its neck and a trail of fallen cards leading to it, fireflies over
the grass by night. An H2 stands the Caterpillar at the right, sitting up on the giant mushroom with his arms folded
and the hookah's mouthpiece at his lips, the smoke rising from them in rings of the code up to the hedge, foxgloves at
the mushroom's foot and the hookah's coal burning by night; an H3 the rose tree in its tub rising the strip's full
height, trained in more heads the taller the strip, the Two of Spades painting its white roses red, his brush dabbing,
and by night a lantern burning in the tree. SECTION A-A carries the little golden key from the glass table, a strip's
title the White Rabbit's pocket watch, and the rule where no scene stands tufts of the spring grass, a daisy or a
bluebell in some. A phone's H1 holds the whole of Wonderland under its words; its H2 the Caterpillar on his mushroom
and its H3 the Five of Spades at a rose bush and the Two at the rose tree, under theirs whatever they say. The footer
stands on the hedge's top, the clipped hedge rising where its cells leave it room, with the rabbit hole in its mound
after a title block's last cell, the code glowing up out of it and flickering by night, and a playing card dropped in
the corner of its notes; BUILT WITH carries a heart pip, and the scale's bar is painted white and red by turns. Link
buttons are playing cards under a sprig of hedge, each with its own sprite of Wonderland; the elements are built of
playing cards, the hedge and its briar, roses painted red, the rabbit's gold watch and the golden key; badges carry a
band of the hedge set with roses; and the games are played on the Looking-Glass country's squares of meadow and hedge
in a frame painted in stripes of red and white, their winners standing on a podium of clipped hedge hung with a
garland of roses.
"""
from __future__ import annotations

from ...holidays.designs.materials import Podium, Stuff
from ..hand import CollectionSet
from .. import rain
from . import art as A
from .palette import C, RAMP, TOKENS, X, step

ROSE, CARD, PAGE, GARDEN = RAMP["rose"], RAMP["card"], RAMP["page"], RAMP["garden"]


class Rabbit(CollectionSet):
    key = "matrix-rabbit"
    name = "Rabbit"
    collection = "matrix"
    tagline = (
        "Follow the white rabbit into Wonderland: titles on playing cards, the roses painted red, the code rising.")
    about = (
        "Every sheet is a page of a storybook in spring, pale yellow-green and sprigged with small printed flowers by "
        "day and by night a deep indigo garden under stars that are the code showing through the sky, framed in a "
        "clipped hedge set with roses along its top, some of them white roses half painted red, and across the sky a "
        "pack of playing cards tumbling on the wind. Every letter of the title is printed on a playing card, red or "
        "black by its suit with a pip in its corner, the cards dealt a little askew. The headers open on Wonderland "
        "after Tenniel: the White Rabbit in his tweed jacket and blue waistcoat bounding along and looking at his gold "
        "watch under an arch of roses, among tulips and Easter eggs in the grass, the moon in the arch by night; and "
        "an old tree, the Cheshire Cat grinning on its bough by day and only his grin left by night, its roots arching "
        "over the rabbit hole, the code rising up out of it and lighting the roots and the grass. A section's header "
        "stands the Caterpillar on his mushroom, the smoke of his hookah rising in rings of the code, and a strip's "
        "the rose tree at its full height, the Two of Spades painting its roses red. The golden key lies beside "
        "SECTION A-A, the rabbit's watch beside a strip's title, and spring grass grows along the rule. On a phone the "
        "whole of Wonderland stands under the words, and a section's and a strip's heroes under theirs. The footer "
        "stands on the hedge with the rabbit hole on it, glowing by night; links are playing cards under a sprig of "
        "hedge; the elements are playing cards, the hedge's briar, roses painted red and the rabbit's gold watch; "
        "badges wear a band of the hedge; and the games are played on squares of meadow and hedge in a frame painted "
        "red and white, their winners standing on a podium of clipped hedge hung with a garland of roses.")
    tokens = frozenset(TOKENS)

    # ---- colour and paper
    def ink(self, night):
        """The words in the hand's two inks; the labels in the roses' red, a lighter red by night."""
        return dict(
            title=ROSE[5] if night else ROSE[3], shadow=X["shade"],
            body=self.hand.body[night], muted=self.hand.muted[night],
            rule=X["rule_night"] if night else X["rule_day"], accent=ROSE[5] if night else ROSE[2],
            tag=ROSE[3] if not night else ROSE[2], tag_ink=CARD[6],
            fill=GARDEN[4] if night else CARD[5], dim=X["dim_night"] if night else X["dim_day"],
        )

    def paper(self, p, night, uid="p"):
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        return A.bg_at(p, night, y)

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The page, and by night the garden's sky, the code showing through it as stars wherever no word will
        stand, and none where the month's mark stands; and across the sky above the words a pack of cards tumbling
        on the wind, behind the title, ending above the text the layout sets under it (its second box in `avoid`)
        and keeping out of the month's mark (see `art.pack_of_cards`)."""
        self.paper(p, night)
        if night:
            A.night_sky(p, (6, A.TOP + 2, p.w - 6, int(y1 * 0.7)), motion, avoid=list(avoid) + [self.mark_box(p)])
        if len(avoid) > 1:
            A.pack_of_cards(p, (A.EDGE, A.TOP + 2, p.w - A.EDGE, avoid[1][1] - 2), night, motion,
                            holes=[self.mark_box(p)])

    def frame(self, p, night, webs=False):
        """The clipped hedge down the sides and along the foot; on a sheet with no hedge of roses across its top,
        along its top as well."""
        A.frame(p, night)
        if not webs:
            uid = f"{getattr(p, 'sheet', 'p')}h"
            p.shapes["base"].append(f'<rect width="{p.w}" height="{A.EDGE}" fill="url(#{uid})"/>')

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """The hedge set with roses across a header's top, parting either side of the month's mark when the header
        carries it (see `art.hedge_top`)."""
        box = self.mark_box(p)
        A.hedge_top(p, night, gap=(box[0], box[2]) if self.marked else None)

    def tag(self, p, x, y, w, h, night):
        """A block of the roses' red, a note's number in white card on it."""
        p.rect(x, y, w, h, ROSE[3] if not night else ROSE[2])
        p.hline(x, x + w, y, ROSE[5] if not night else ROSE[4])
        p.hline(x, x + w, y + h - 1, ROSE[1])

    def title_text(self, p, x, y, s, night, scale):
        """Every letter on a playing card (see `art.card_title`). The drawing keeps each line, for the beam that
        passes down it in a moving header."""
        w = A.card_title(p, x, y, s, night, scale)
        p.titles = getattr(p, "titles", []) + [(x, y, s, scale, w)]
        return w

    # ---- the headers' scenes
    def scene(self, design, p, rule, night, motion):
        """On H1 Wonderland: the grass along the foot wherever the words leave it, the White Rabbit with his watch at
        the left, the old tree and its rabbit hole glowing with the code at the right, and by night the moon and the
        fireflies, each where the words leave it room; on H2 the Caterpillar on his mushroom at the right, his smoke
        rising to the hedge (see `art.caterpillar_scene`), and on H3 the rose tree and its gardener at the right,
        rising the strip's full height (see `art.rose_garden`), each on the grass, along the whole foot where the words
        leave it free; and in a moving header the beam passing down each line of the title on the hand's period."""
        if motion:
            for n, (x, y, s, scale, w) in enumerate(getattr(p, "titles", ())):
                rain.scan(p, x, y, s, scale, w, n, self.hand.glint, C["white"])
        g = rule - 1
        spans = []
        if design == "H1":
            top = A.TOP + 1
            if p.clear_of_words(4, g - 5, p.w - 4, g + 2):
                A.meadow(p, A.EDGE, p.w - A.EDGE, g, night)
            # The rose arch as wide as the words leave it room over the rabbit, and the tree's crown reaching as far
            # over the page as they leave it.
            width = next((w for w in (40, 38, 36) if p.clear_of_words(4, g - 76, 9 + w, g + 2)), None)
            if width and p.clear_of_words(4, g - 32, 60, g + 2):
                spans.append(A.warren(p, 6, g, night, motion, width=width))
                if night:
                    A.fireflies(p, (8, g - 26, 56, g - 6), motion)
            if p.clear_of_words(363, top, 411, g + 2) and p.clear_of_words(354, g - 14, 411, g + 2):
                reach = next(x for x in range(356, 366) if p.clear_of_words(x - 2, top, 411, g - 40))
                spans.append(A.tree(p, 356, 410, g, night, motion, reach=reach))
            if len(spans) > 1 and p.clear_of_words(300, g - 11, 356, g + 2):
                A.fallen_cards(p, 316, g, night)
        elif design == "H2":
            x0 = next((x for x in range(300, 346) if p.clear_of_words(x - 2, A.TOP, 412, g + 2)), None)
            if x0 is not None:
                A.meadow(p, A.EDGE if p.clear_of_words(4, g - 5, x0, g + 2) else x0, p.w - A.EDGE, g, night)
                spans.append(A.caterpillar_scene(p, x0, p.w - A.EDGE - 1, g, night, motion))
        else:
            x0 = next((x for x in range(340, 362) if p.clear_of_words(x - 2, A.TOP, 412, g + 2)), None)
            if x0 is not None:
                A.meadow(p, A.EDGE if p.clear_of_words(4, g - 5, x0, g + 2) else x0, p.w - A.EDGE, g, night)
                spans.append(A.rose_garden(p, x0, p.w - A.EDGE - 1, g, night, motion, A.TOP + 2))
        return spans

    @staticmethod
    def _room(p, x0, x1, g, most, least):
        """The rows free of words over the grass at row g between x0 and x1, `most` at the most, keeping three rows of
        margin above and two beside; None when fewer than `least` are free."""
        for room in range(most, least - 1, -1):
            if p.clear_of_words(x0 - 2, g - room - 3, x1 + 2, g + 3):
                return room
        return None

    # ---- the phones
    def h1_narrow(self, h, night):
        """A phone's H1, Wonderland given `art.PHONE_SCENE` rows under the words, the notes set under the words
        however many there are."""
        self.phone_scene_rows = A.PHONE_SCENE + 4 + 10 * len(self.said(h))
        try:
            return super().h1_narrow(h, night)
        finally:
            del self.phone_scene_rows

    def scene_narrow(self, design, p, y, night):
        """A phone's H1 scene, built to the rows its words leave free over it: the whole of Wonderland across the
        phone under the words (`art.phone_world`). A phone's H2 and H3 stand their heroes under their words instead
        (see `scene_under`)."""
        if design == "H1":
            g = y - 1
            room = self._room(p, 5, p.w - 5, g, A.PHONE_SCENE - 2, A.PHONE_LEAST)
            if room:
                A.phone_world(p, g, night, room)

    def phone_rows(self, design, title_w):
        """The rows a phone's H2 or H3 leaves under its words for its hero, whatever the words say: the Caterpillar
        on his mushroom with his smoke rising, and the rose tree with its gardeners (see `scene_under`)."""
        return A.UNDER[design]

    def scene_under(self, design, p, y0, y1, night):
        """A phone's hero under its words, across the phone, standing on the rule at y1 and built to the rows free over
        it: on H2 the Caterpillar on his mushroom (`art.phone_caterpillar`), on H3 the gardeners painting the roses red
        (`art.phone_garden`)."""
        g = y1 - 1
        room = self._room(p, 5, p.w - 5, g, A.UNDER[design] - 3, 44)
        if room:
            (A.phone_caterpillar if design == "H2" else A.phone_garden)(p, g, night, room)

    def section_mark(self, p, x, y, night):
        """The little golden key from the glass table, after SECTION A-A, a row under the title's cards."""
        A.golden_key(p, x, y + 1, night)

    def strip_mark(self, p, x, y, night):
        """The White Rabbit's pocket watch beside a strip's title, level with its cards."""
        A.pocket_watch(p, x, y - 4, night)

    def rule_decor(self, p, x0, x1, y, seed, night):
        """Tufts of the spring grass along a rule where no scene stands on it, a daisy or a bluebell in some, kept two
        rows clear of every word."""
        A.tufts(p, x0, x1, y, seed, night)

    def _finish(self, p, night):
        """The last pass, which a drawing made lighter keeps too: the file written as lightly as it can be, the same
        drawing unit for unit (see `Pix.compact`), the month's mark left as the hand draws it."""
        if not p.lite:
            self.finish(p, night)
        p.compact(keep=("mark",))

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        """A playing card dropped in the corner of the closing notes."""
        A.corner_card(p, x + 4, y - 3, night)

    def _footed(self, p, night, last=False):
        """A footer once its cells are laid: the spring grass along its foot and the clipped hedge rising where the
        cells leave it room, and the rabbit hole with the code glowing up out of it where they leave it free (see
        `art.footing`): on a title block only after its `last` cell, the way back up."""
        after = max((b[2] for b in p.words), default=0) + 4 if last else 0
        A.footing(p, night, self.ink(night)["rule"], after=after)
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
        """A playing card's heart pip in the roses' red."""
        A.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        """White rose and red paint by turns, as the gardeners paint the roses."""
        A.painted_bar(p, x0, y0, w, h, period)

    def link_colours(self, night):
        """By day a playing card's white face in a rim of the roses' darkest red, its letters red; by night the
        garden's indigo in a rim of gold, its letters white card."""
        if night:
            return GARDEN[5], RAMP["gold"][2], CARD[5], GARDEN[3]
        return CARD[5], ROSE[1], ROSE[2], CARD[3]

    def link_top(self, p, x0, x1, y, seed, night):
        """The button finished as a playing card in the garden: a sprig of the clipped hedge along its top edge set
        with roses, and its face lit along its top and down its left and shaded down its right."""
        fill, edge, _, shade = self.link_colours(night)
        A.link_hedge(p, x0, x1, y, night, seed)
        p.hline(1, p.w - 1, y + 1, CARD[6] if not night else GARDEN[6])
        p.vline(1, y + 1, y + 9, CARD[6] if not night else GARDEN[6])
        p.vline(p.w - 2, y + 2, y + 9, shade)

    def link_icon(self, index, night, ink):
        """The rabbit's watch, a card of hearts, a painted rose and the rabbit himself, by turns."""
        names = ("watch", "card", "rose", "rabbit")
        return A.ICONS[names[index % len(names)]], A.icon_pal(night, ink)

    # ---- the elements
    def card_bevel(self, night):
        return (GARDEN[6], GARDEN[2]) if night else (C["white"], CARD[3])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A card as a playing card: a rim of the roses' red inside its edge, a suit's pip in its corner, the red
        lattice of a card's back down its icon cell's edge, and on its lid a sprig of the hedge with a rose."""
        A.card_node(p, x, y, w, h, night, seed, lid)

    def wire_ink(self, night):
        return RAMP["hedge"][4] if night else RAMP["hedge"][2]

    def wire_lights(self, p, cells, night, seed):
        """The wire as a briar of the rose, leaves along it and a rosebud now and then."""
        A.briar(p, cells, night, seed)

    def dashes(self, night):
        return [ROSE[4], CARD[4]] if night else [ROSE[3], RAMP["spade"][2]]

    def ornament(self, kind, p, x, y, night):
        """The White Rabbit's pocket watch, open on its chain, in a free corner of the schematic."""
        if kind == "schematic":
            if p is not None:
                A.big_watch(p, x, y, night)
            return (21, 24)
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as a stack of playing cards, the top one face up."""
        A.card_stack(p, bx, base, bw, v, night, i=bx // 7)

    def peak_mark(self, p, x, y, night):
        A.crown(p, x, y, night)

    def dial_ring(self, p, arc, night):
        """The dial as the face of the White Rabbit's watch, in its rim of gold."""
        A.gold_ring(p, arc, night)

    def dial_tick(self, p, x, y, night):
        p.px(x, y, RAMP["gold"][5 if not night else 4])
        p.px(x + 1, y + 1, RAMP["gold"][1])

    def dial_hub(self, p, cx, cy, night):
        """The watch's boss, gold, where its hands turn."""
        from ...holidays.pixel import sphere
        sphere(p, cx + 0.5, cy - 0.5, 2.6, RAMP["gold"], lo=1, hi=6)

    def material(self, i, xx, yy, y0, y1, lift, night):
        """Wonderland's stuffs by turns: a card's red back, the hedge, the waistcoat's blue, the tweed and the white
        card's face."""
        return A.wrapper(i, xx, yy, y0, y1, lift, night)

    def counter_cell(self, q, ox, oy, night):
        A.card_cell(q, ox, oy, night)

    def counter_ink(self, night, dim):
        """A numeral printed on its card in the spades' blackest; a leading nought in the card's grey: inks the
        drawing's other words never take, since a drawing sets all the letters of one ink together where that ink
        is first used, and an ink of their own keeps the numerals over the cards they are printed on."""
        return CARD[2] if dim else RAMP["spade"][0]

    def timeline_line(self, p, x0, x1, y, night):
        """The time line as a low clipped hedge, up to today."""
        if x1 - x0 >= 2:
            A.hedge_line(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        """A red rose for a release, a rose bush for a big one, a bud for a patch, a white rose not yet painted for one
        still to come, and the rabbit hole for the repository's beginning."""
        A.release_rose(p, x, gy, kind, night, i)

    def today_mark(self, p, x, y, night):
        """The White Rabbit's pocket watch at today's end of the hedge: he is late."""
        A.pocket_watch(p, x - 4, y - 11, night)

    def avatar(self, p, cx, cy, i, person, night):
        A.card_avatar(p, cx, cy, i, person, night)

    def commit_bar(self, p, x, y, w, fill, night):
        """A contributor's share as white roses painted red as far as their commits go."""
        A.painted_share(p, x, y, w, fill, night)

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """A wreath of the clipped hedge set with roses round the seal."""
        A.wreath(p, cx, cy, r0, r1, n, night)

    def seal_mark(self, p, x, y, night):
        A.golden_key(p, x + 2, y, night)

    def placard_board(self, p, night):
        A.card_board(p, night)

    def placard_mark(self, p, x, y, night):
        A.pocket_watch(p, x + 2, y - 7, night)

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """A sprig of the clipped hedge along a badge's top two rows, set with a rose every so often and kept inside
        its shape, the letters under it; and under it each block a playing card's face, lit along its top and
        shaded along its foot."""
        from ...holidays.designs.badges import inside
        H = RAMP["hedge"]
        h = s["h"]
        ty = self._text_y(s)
        text_rows = range(ty - 1, ty + (7 if s["font"] == "57" else 5) + 1)
        for y in range(h):
            for x in range(w):
                if not inside(x, y, w, h, s["corner"]):
                    continue
                if y <= 1:
                    rose = (x + seed) % 9 == 4
                    if y == 0:
                        p.px(x, y, ROSE[4] if rose else H[5] if (x * 3 + seed) % 4 else H[4])
                    else:
                        p.px(x, y, ROSE[2] if rose else H[2] if (x + seed) % 3 else H[3])
                    continue
                c = p.get(x, y)
                try:
                    if y == 2 and y not in text_rows:
                        p.px(x, y, step(c, 1))
                    elif y == h - 1:
                        p.px(x, y, step(c, -1))
                except KeyError:
                    pass

    def badge_label(self):
        """A label of the spades' black, its letters white card."""
        return (RAMP["spade"][1], CARD[5])

    def badge_gold(self):
        """A live badge's label in the gold of the rabbit's watch."""
        return (RAMP["gold"][4], RAMP["spade"][0])

    def badge_states(self):
        return {"green": (RAMP["hedge"][3], C["white"]), "yellow": (RAMP["gold"][5], RAMP["spade"][0]),
                "red": (ROSE[3], C["white"]), "slate": (RAMP["spade"][5], C["white"])}

    def badge_swatches(self):
        """The garden's colours a written colour finds its nearest among: the roses, the pinks of the rabbit's
        ears, the watch's gold, the hedge, the little bottle's glass, the waistcoat's blue, the garden's indigo, the
        tweed, the spades' black, the card's white, the rabbit's grey fur and the page's spring green."""
        R = RAMP
        S = R["spade"]
        return {"rose": (ROSE[3], C["white"], None), "pink": (R["pink"][1], C["white"], None),
                "gold": (R["gold"][4], S[0], None), "hedge": (R["hedge"][3], C["white"], None),
                "bottle": (R["bottle"][3], C["white"], None), "blue": (R["blue"][4], C["white"], None),
                "indigo": (GARDEN[5], C["white"], None), "tweed": (R["tweed"][3], C["white"], None),
                "spade": (S[1], CARD[5], "lattice"), "card": (CARD[6], S[1], "rim"), "fur": (R["fur"][3], S[1], None),
                "page": (PAGE[3], S[1], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        """The spades' black latticed faintly, as a card's back is, off the letters' rows."""
        if pattern == "lattice" and y not in text_rows and ((x + y) % 4 == 0 or (x - y) % 4 == 0):
            return RAMP["spade"][3]
        return c

    def badge_outline(self, pattern):
        """A white card's face has its rim."""
        return CARD[2] if pattern == "rim" else None

    def badge_shine(self, c, y, h):
        try:
            return step(c, 1) if y == 2 else step(c, -1) if y == h - 1 else c
        except KeyError:
            return c

    def plate_colours(self, mode):
        """A plate is a playing card: by day its white face, a rim of the roses' red and the value painted red; by
        night the card laid in the dark garden; a live plate is the gold of the watch."""
        S, G = RAMP["spade"], RAMP["gold"]
        if mode == "day":
            return dict(paper=CARD[5], dot=CARD[4], frame=ROSE[2], block=ROSE[3], ink=S[1], letters=CARD[6])
        if mode == "night":
            return dict(paper=GARDEN[4], dot=GARDEN[5], frame=G[3], block=ROSE[2], ink=C["body_night"],
                        letters=CARD[5])
        return dict(paper=G[4], dot=G[3], frame=S[1], edge=G[2], ink=S[0])

    def plate_edge(self, block):
        return step(block, -1)

    # ---- the games
    def game_squares(self, night):
        """The Looking-Glass country, divided into squares by hedges: squares of spring meadow and of clipped hedge,
        each a tone down by night."""
        return (Stuff(PAGE, 4 if night else 5, "sand"), Stuff(RAMP["hedge"], 3 if night else 4, "needles"))

    def game_frame(self, night):
        """A frame painted in stripes of red and white, as the gardeners paint the roses."""
        return Stuff(ROSE, 3, fleck=CARD[6]), "stripes"

    def game_podium(self, night):
        """A podium of clipped hedge, hung with a garland of roses."""
        return Podium(Stuff(RAMP["hedge"], 3, "needles"), "garland", Stuff(ROSE, 3))


SET = Rabbit()
