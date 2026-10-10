# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Hoard set: a dragon asleep on its gold in a barrow through midwinter, in hoard gold and garnet."""
from __future__ import annotations

from ...holidays.designs import WIDE
from ...holidays.designs.badges import inside
from ..hand import CollectionSet
from . import art as A
from .palette import C, NIGHT_SKY, RAMP, TOKENS, X, step

GOLD, GARNET = RAMP["gold"], RAMP["garnet"]


class Hoard(CollectionSet):
    key = "medieval-hoard"
    name = "Hoard"
    collection = "medieval"
    # What the design is, in words, for the page that shows the collection.
    tagline = ("The dragon asleep on its mountain of gold in a snowbound barrow through midwinter, in gold set with "
               "garnets.")
    about = (
        "Every header is the chamber of a barrow walled in chalk laid dry with its flints, every block of its words "
        "cut on a great dressed stone standing like the orthostats of a passage grave and the corbelled roof stones "
        "along its top under a lintel carved with spirals and hung with icicles where a drop gathers and falls, the "
        "chalk lit cold and blue by the snow at the mouth and warm by the gold at the far end. Titles are gold "
        "cloisonne after the Sutton Hoo treasure, every letter cut garnets set in gold walls, and in a moving header a "
        "glint crosses them. The H1 is the dragon asleep, coiled round and over a mountain of gold as large as the "
        "room allows, its wing folded on its back, its horned head resting on its forelegs and its tail swept out "
        "along the gold that pours down before it to the floor, where a sword with a garnet pommel stands driven in "
        "and an open chest spills its coins among a round shield, the helmet, drinking horns, goblets, the crown and "
        "gems in garnet, emerald and sapphire. In a moving header its smoke rises, its eye half opens and closes "
        "again, a coin slides down the pile and a glint wanders over the gold. At the other end the barrow's mouth "
        "stands between the massive stones of a passage grave, spirals carved across its capstone, and just outside it "
        "the thief strides away over the snowy downs with the cup he took held high, his footprints trailing back to "
        "the door; where the words leave the floor clear, the golden standard of the poem stands over its own gold "
        "between them. By night the barrow is dark but for its own lights: the dragon's eye glows amber as it opens, "
        "its ember breath lights its scales and the floor and the gold far out across it, the standard shines, and the "
        "moon lays a cold shaft across the floor in at the mouth. The H2 is the dragon's great head itself, horned and "
        "toothed, its jaw resting on its gold, and the H3 is the great helm of the ship burial drawn large, its face "
        "mask, its brows and the dragon over them in gold and garnet, raised on its gold with the great buckle, the "
        "shoulder clasps, a sword and a drinking horn and the coins spilling along the floor under the words; on a "
        "phone each stands beside its words where they leave it room and under them where they leave none. Footers end "
        "in a drift of coins with the dragon's tail tip curled round a cup, links are gold coins struck with a device "
        "on straps of garnet, and badges are gold and garnet cloisonne whose states are emerald, gold, ruby and onyx. "
        "Every element is the hoard's own gold, from stacks of coins for a histogram, an arm ring with a dragon for "
        "its hand and ingots for counters to a trail of coins set with gems, bracteates for the people who made it, a "
        "brooch for a seal and the iron bound lid of a chest for a placard.")
    tokens = frozenset(TOKENS)

    # ---- colour and paper
    def ink(self, night):
        """The words in the hand's two inks, the titles in garnet by day and gold by night."""
        return dict(
            title=GOLD[4] if night else GARNET[1], shadow=RAMP["earth"][0] if night else RAMP["chalk"][3],
            body=self.hand.body[night], muted=self.hand.muted[night],
            rule=X["rule_night"] if night else X["rule_day"], accent=X["accent_night"] if night else X["accent_day"],
            tag=GARNET[2], tag_ink=GOLD[5],
            fill=C["fill_n"] if night else C["fill"], dim=X["dim_night"] if night else X["dim_day"],
        )

    def paper(self, p, night, uid="p"):
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        return A.bg_at(p, night, y)

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        """The barrow has no sky: by night it is dark but where its own lights fall."""

    def top_centre(self, p) -> tuple:
        """The columns of a header's top kept for the month's mark, two units either side of its box: kept whether
        the mark is drawn or not, so a page that keeps the design all year has the same lintel."""
        n = self.hand.mark_size
        x0 = p.w // 2 - n // 2
        return x0 - 2, x0 + n + 2

    def frame(self, p, night, webs=False):
        """The great stones of a passage grave; a header's lintel is deep enough to hang its icicles from, its
        spirals pausing at its top centre for the month's mark, and a footer leaves its threshold to its drift of
        coins."""
        A.frame(p, night, header=webs, footer=not webs and getattr(p, "sheet", "") == "p",
                clear=self.top_centre(p) if webs else None)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """The icicles hanging from the lintel along the whole header, pausing at its top centre for the month's
        mark (see `art.icicles`)."""
        A.icicles(p, A.SIDE, p.w - A.SIDE, A.HEAD_LINTEL, night, seed=seed, clear=self.top_centre(p))

    def tag(self, p, x, y, w, h, night):
        """A block of garnet a tag's gold letters sit on, its top edged in gold and its foot in shade."""
        p.rect(x, y, w, h, GARNET[2])
        p.hline(x, x + w, y, GOLD[4])
        p.hline(x, x + w, y + h - 1, GARNET[1])

    def title_text(self, p, x, y, s, night, scale):
        """A title in gold cloisonne set with garnets, a glint crossing it in a wide moving header."""
        return A.cloisonne_title(p, x, y, s, night, scale, motion=p.w == WIDE)

    @staticmethod
    def _reach(p, x0, g, step=1, limit=None, rows=8):
        """How far right from x0 (or left, with a negative `step`) a band `rows` tall over the ground at row g runs
        clear of words, two units of margin kept; at most to `limit`."""
        x = x0
        while (limit is None or (x < limit if step > 0 else x > limit)) and \
                p.clear_of_words(x - 2, g - rows - 2, x + 3, g + 3):
            x += step
        return x

    @staticmethod
    def _rows(p, x0, x1, g, most):
        """The rows over the ground at row g between x0 and x1 that are clear of words, up to `most`."""
        n = 0
        while n < most and p.clear_of_words(x0 - 2, g - n - 3, x1 + 2, g + 3):
            n += 1
        return n

    def scene(self, design, p, rule, night, motion):
        p.rule = rule
        g = rule - 1
        if design == "H1":
            return self._barrow(p, g, night, motion)
        if design == "H2":
            return self._section(p, g, night, motion)
        return self._strip(p, g, night, motion)

    def _strip(self, p, g, night, motion):
        """An H3's scene: the great helm of the ship burial on its gold at the right, the showpiece, drawn small
        only where the rows the words leave there are too few for it, with the cup before it where the title left
        the cup no room beside it; and where the words leave the floor before it clear, the hoard spilt along it
        filling the band under them, the great gold buckle, the shoulder clasps, a sword and a drinking horn
        heaped on the coins nearest the helm (see `art.helm_on_gold`)."""
        x1 = p.w - A.SIDE - 2
        cup = not getattr(p, "marked", False)
        for art in (A.GREAT_HELM, A.SMALL_HELM):
            for with_cup in ((True, False) if cup else (False,)):
                span = (x1 - len(art[0]) - 8 - (16 if with_cup else 8) - 2, x1 + 2)
                rows = self._rows(p, span[0], x1, g, 60)
                if rows >= len(art) + 7:
                    left = self._reach(p, span[0] - 1, g, step=-1, limit=A.SIDE + 6, rows=6) + 3
                    return [A.helm_on_gold(p, x1, g, night, motion, cup=with_cup, art=art, left=left, room=rows)]
        return []

    def strip_mark(self, p, x, y, night):
        """The jewelled cup beside a strip's title, cut on the title's stone (see `art.wall`)."""
        A.treasure(p, x, y - 5, A.CUP, night)
        p.marked = True
        p.marks = getattr(p, "marks", []) + [(x - 1, y - 6, x + len(A.CUP[0]) + 1, y - 4 + len(A.CUP))]

    def _section(self, p, g, night, motion):
        """An H2's scene: the dragon's great head resting its jaw on its gold at the right, as large as the room the
        words leave there allows, with as much of its neck rising behind it as the room allows."""
        x1 = p.w - A.SIDE - 1
        spot = A.head_place(p, p.w // 2, x1, g, A.ICE_FOOT + 3, most=88, least=36)
        if not spot:
            return []
        span, _ = A.head_on_gold(p, *spot, x1, g, night, motion)
        return [span]

    # ---- a phone's scenes
    PHONE_ROWS = {"H2": 50, "H3": 46}   # the rows the dragon and the great helm take under a phone's words
    _under = None                       # the header being laid out again with those rows
    _notes = 0                          # the notes of the phone H1 being drawn

    @property
    def phone_scene_rows(self):
        """The rows a phone's H1 leaves under its words for its barrow: the mouth and the dragon at their size,
        and ten more for each note, which are set under the words before them."""
        return 58 + 10 * self._notes

    def h1_narrow(self, h, night):
        """A phone's H1, the rows for its barrow counting its notes (see `phone_scene_rows`)."""
        self._notes = len(self.said(h))
        try:
            return super().h1_narrow(h, night)
        finally:
            self._notes = 0

    def h2_narrow(self, h, night):
        """A phone's H2, laid out as the kit lays it out; where the dragon's head found no room beside its words,
        laid out again with rows under them (see `phone_rows`)."""
        return self._phone("H2", super().h2_narrow, h, night)

    def h3_narrow(self, h, night):
        """A phone's H3, laid out with rows under its words for the great helm on its heap (see `phone_rows`): the
        strip beside a title is lower than the helm stands, so it always stands under the words."""
        self._under = "H3"
        try:
            return super().h3_narrow(h, night)
        finally:
            self._under = None

    def _phone(self, design, draw, h, night):
        """A phone's H2 or H3 as the kit lays it out, and where nothing stood beside its words, laid out again with
        rows under them for its scene."""
        p = draw(h, night)
        if getattr(p, "stood", False):
            return p
        self._under = design
        try:
            return draw(h, night)
        finally:
            self._under = None

    def phone_rows(self, design, title_w):
        """The rows a phone's H2 or H3 leaves under its words for its scene: on H2 none at first, as the kit lays it
        out, and only where nothing could stand beside the words, as many as the dragon needs; on H3 always as
        many as the great helm needs."""
        return self.PHONE_ROWS[design] if self._under == design else 0

    def scene_narrow(self, design, p, y, night):
        """A phone's scenes, built to the rows its words leave: on H1 the barrow across the rows under the words;
        on H2 the dragon's head on a little heap of its gold beside SECTION A-A, where the words leave a column
        free at the right. An H3's great helm stands under its words (see `h3_narrow`)."""
        if design == "H1":
            p.rule = y
            g = y - 1
            rows = self._rows(p, 6, 174, g, 80)
            if rows >= 42:
                A.phone_barrow(p, g, rows, night)
                p.stood = True
            return
        if design == "H2":
            # the tagline is set under SECTION A-A after this, from row y + 12: the head stands no lower than y + 7
            g = y + 7
            if self._rows(p, 150, 175, g, 40) >= 30:
                if A.head_peeking(p, p.w - A.SIDE - 1, g, night):
                    p.stood = True

    def scene_under(self, design, p, y0, y1, night):
        """The scene under a phone's words, from its last words at row y0 to its rule at y1, across the phone: on
        H2 the dragon's great head on its gold with the helmet and the crown spilt before it; on H3 the great helm
        on its heap with its cup, the coins spilt along the floor with the crown and a shield."""
        g = y1 - 1
        p.stood, p.rule = True, y1
        if design == "H2":
            A.phone_section(p, y0, g, night)
        else:
            A.phone_strip(p, y0, g, night)

    def section_mark(self, p, x, y, night):
        """A gold coin struck with a cross beside SECTION A-A, from a row above the words, cut on their stone (see
        `art.wall`)."""
        A.coin_mark(p, x, y - 1, night)
        p.marks = getattr(p, "marks", []) + [(x - 1, y - 2, x + len(A.COIN_MARK[0]) + 1, y + len(A.COIN_MARK))]

    def _barrow(self, p, g, night, motion):
        """An H1's barrow: at the right the dragon asleep coiled round and over its hoard in the column the words
        leave clear there from the icicles to the floor, as large as that room allows, its head on its forelegs on
        the floor with its nose out before the column where the words leave the floor clear and its tail swept out
        along the floor toward the middle; at the left the barrow's mouth as tall as the rows there allow, its snow
        drifted in along the floor and the thief's footprints going out over it; and between them, where the words
        leave the floor clear, the golden standard over its own gold."""
        spans = []
        x1 = p.w - A.SIDE - 1
        top = A.ICE_FOOT + 3
        middle = p.w // 2
        x0c = x1
        while x0c - 1 > middle and p.clear_of_words(x0c - 3, top - 2, x0c + 2, g + 3):
            x0c -= 1
        tall = min(1.15, (g - top) / 74)
        W = min(x1 - x0c, round(52 * tall * 1.3))
        if W >= 30 and g - top >= 40:
            s = max(0.5, min(1.2, W / 52, tall))
            top = max(top, g - round(74 * s * 1.1))
            placed = None
            for L in range(round(40 * s), 19, -2):
                hy = g - A.RESTING - round(A.JAW_FOOT * L / 100)
                placed = next(((nx, L) for nx in range(x1 - W - round(0.35 * L), x1 - W + 3)
                               if A.head_room(p, nx, hy, L)), None)
                if placed:
                    break
            if placed:
                nx, L = placed
                tail = self._reach(p, nx - 2, g, step=-1, limit=middle + 10, rows=6) + 2
                spans.append(A.lair(p, x1 - W, x1, top, g, night, motion, nx, L, tail))
        x0 = 7
        for room in A.MOUTH_ROOMS:
            rows = self._rows(p, x0 - 4, x0 + room, g, 90)
            if rows >= (44 if room >= 48 else 30):
                break
        end = (spans[0][0] - 10) if spans else middle
        # between the mouth and the hoard, where the words leave the floor the room, the golden standard
        cx = 50 + (end - 50) * 9 // 20
        if end - 50 >= 110 and self._rows(p, cx - 26, cx + 28, g, 80) >= 64:
            top = max(A.ICE_FOOT + 3, g - 66)
            spans.append(A.standard(p, cx, g, top, night, motion))
            end = cx - 30
        if rows >= 30:
            reach = self._reach(p, x0 + room - 4, g, step=1, limit=end, rows=8) - 2
            spans.append(A.mouth(p, x0, g, night, motion, rows, max(x0 + room + 2, reach), room=room))
        return spans

    def rule_decor(self, p, x0, x1, y, seed, night):
        """Along a header's rule where no scene stands, the barrow's floor with the coins the thief dropped as he
        fled; under an element's tag, a fillet of gold."""
        if y > 24:
            p.rule = getattr(p, "rule", None) or y
            A.dropped(p, x0, x1, y, night, seed=seed)
        else:
            A.fillet(p, x0, x1, y, night)

    def finish(self, p, night):
        """The last pass: in a header its walls built round its words (see `art.wall`), lit by day from the mouth
        and the gold, and by night every pool of its lights laid over them (see `art.light`); by night the lights'
        colour on what stands near them; in a wide header the drop that gathers on an icicle and falls; on an
        instruments sheet the dial's hand made a dragon; on a phone's milestones the line run down its left made a
        trail of coins; and every label's backing lifted off the wall, so the wall shows through where it was."""
        if getattr(p, "icicles", None):
            rule = self._rule_of(p, night)
            A.wall(p, night, A.SIDE, A.HEAD_LINTEL, p.w - A.SIDE, rule)
            if night:
                A.light(p, A.SIDE, A.HEAD_LINTEL, p.w - A.SIDE, rule)
            else:
                A.goldlight(p)
        if night:
            A.lights(p)
        if p.w == WIDE and getattr(p, "icicles", None):
            A.drip(p, night)
        if getattr(p, "dial", None):
            A.dragon_hand(p, night, self.ink(night)["accent"])
        if getattr(p, "sheet", "") == "e33":         # a phone's milestones, the sheet the layout framed with seed 33
            wire, base = self.wire_ink(night), p.layers["base"]
            line = sorted(y for (x, y), c in base.items() if x == 17 and c == wire)
            if line:
                for y in line:
                    del base[(17, y)]
                A.coin_column(p, 17, line[0], line[-1], night)
        keys = set(NIGHT_SKY) if night else {RAMP["chalk"][5]}
        base = p.layers["base"]
        for xy in [xy for xy, c in base.items() if c in keys]:
            del base[xy]

    def _rule_of(self, p, night) -> int:
        """A header's rule: the row its scene was handed, or failing that the first row the rule's colour runs
        most of the way along."""
        rule = getattr(p, "rule", None)
        if rule is None:
            ink, base = self.ink(night)["rule"], p.layers["base"]
            rule = next((y for y in range(30, p.h) if sum(base.get((x, y)) == ink for x in range(4, p.w - 4))
                         > (p.w - 8) // 2), p.h - 8)
        return rule

    def _finish(self, p, night):
        """The last pass, on a drawing made lighter to fit its budget as on any other: the lighter drawing keeps
        every light, the drop and the dial's dragon, thinning only what the lights lay (see `art.lights`)."""
        self.finish(p, night)

    # ---- the footers
    def footer_mark(self, p, x, y, night):
        """The dragon's tail tip curled round a cup at the corner of the closing notes: its place is kept, and it
        is drawn once the words are all set, standing on the coins (see `_footed`)."""
        A.footer_mark(p, x - 2, y - 5, night)

    def _footed(self, p, night):
        """A footer as the floor of the hoard: its drift of coins along its foot, heaping up where the cells leave
        room, and the mark at the corner of its notes (see `art.footing`)."""
        A.footing(p, night, self.ink(night)["rule"])
        return p

    def f1(self, ft, night):
        return self._footed(super().f1(ft, night), night)

    def f2(self, ft, night):
        return self._footed(super().f2(ft, night), night)

    def f1_narrow(self, ft, night):
        return self._footed(super().f1_narrow(ft, night), night)

    def f2_narrow(self, ft, night):
        return self._footed(super().f2_narrow(ft, night), night)

    # ---- the elements
    def card_bevel(self, night):
        return (GOLD[6], GOLD[3]) if not night else (GOLD[3], GOLD[1])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A card as a plaque of gold with a raised rim, its icon worked in gold on a slab of garnet set in gold
        walls down its left (see `art.plaque`)."""
        A.plaque(p, x, y, w, h, night, self.ink(night)["body"])

    def wire_ink(self, night):
        return GOLD[2] if not night else GOLD[3]

    def wire_lights(self, p, cells, night, seed):
        """The wire as a chain of gold, a garnet at each turn."""
        A.chain(p, cells, night)

    def dashes(self, night):
        return [GOLD[3], GARNET[3 if not night else 4]]

    def ornament(self, kind, p, x, y, night):
        """The helmet of the ship burial on a little heap of coins in a free corner of the schematic."""
        if kind == "schematic":
            if p is not None:
                A.helm_heap(p, x, y, night)
            return (24, 22)
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as a stack of gold coins, set a little askew as a hand stacks them."""
        A.coin_stack(p, bx, base, bw, v, night)

    def peak_mark(self, p, x, y, night):
        """A cut garnet in its gold setting beside the busiest week's count."""
        A.gem_mark(p, x, y - 1, night)

    def dial_ring(self, p, arc, night):
        """The dial as a twisted gold arm-ring, each end a dragon's head."""
        cx = (arc[0][0] + arc[-1][0]) / 2
        cy = arc[0][1]
        r = (arc[-1][0] - arc[0][0]) / 2 + 1.5
        p.dial = (round(cx), round(cy), r)
        A.arm_ring(p, arc, night)

    def dial_tick(self, p, x, y, night):
        A.dial_tick(p, x, y, night)

    def dial_hub(self, p, cx, cy, night):
        A.boss(p, cx, cy, night)

    def material(self, i, xx, yy, y0, y1, lift, night):
        return A.matter(i, xx, yy, y0, y1, lift, night)

    def counter_cell(self, q, ox, oy, night):
        A.ingot(q, ox, oy, night)

    def counter_ink(self, night, dim):
        """A numeral struck on a gold ingot, in the gold's darkest; a leading nought struck shallower."""
        return GOLD[2] if dim else GOLD[0]

    def timeline_line(self, p, x0, x1, y, night):
        """A trail of gold coins up to today."""
        if x1 > x0:
            A.coin_trail(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        A.release_gem(p, x, gy, kind, night)

    def today_mark(self, p, x, y, night):
        """The dragon's eye, open and watching, at today's end of the trail."""
        A.dragon_eye(p, x, y, night)

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor as a gold bracteate enamelled in their own colour and stamped with a head; a bot's
        stamped with its icon."""
        A.bracteate(p, cx, cy, person, night)

    def commit_bar(self, p, x, y, w, fill, night):
        """A contributor's share as gold run into a channel cut in garnet."""
        A.channel_bar(p, x, y, w, fill, night)

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """A disc brooch of gold and garnet round the seal."""
        A.brooch(p, cx, cy, r0, r1, night)

    def seal(self, p, d, cx, cy, night):
        """The kit's seal, its face then laid in gold under the words."""
        super().seal(p, d, cx, cy, night)
        A.gold_face(p, cx, cy, self.SEAL - 2, night, self.ink(night)["fill"])

    def seal_mark(self, p, x, y, night):
        A.keystone(p, x, y, night)

    def placard_board(self, p, night):
        """The lid of a treasure chest bound in iron (see `art.chest_lid`)."""
        A.chest_lid(p, night)

    def placard_mark(self, p, x, y, night):
        A.mount(p, x + 1, y - 5, night)

    def heart(self, p, x, y):
        """The heart in a footer's credit as a cut garnet, lit at its upper left."""
        art = [".54.43.", "5443321", "4433221", ".33221.", "..221..", "...1..."]
        p.sprite(x, y, art, {str(i): GARNET[i] for i in range(7)})

    def bar(self, p, x0, y0, w, h, period=5):
        """The graphic scale's bar as a strip of cloisonne, gold and garnet by turns."""
        for x in range(x0, x0 + w):
            for y in range(y0, y0 + h):
                p.px(x, y, GOLD[4] if ((x - x0) // period) % 2 == 0 else GARNET[3])

    def link_colours(self, night):
        """A strap of garnet with pale gold letters (repainted round its edge and its coin by `link_top`)."""
        return GARNET[2], GOLD[2], GOLD[6], GARNET[1]

    def link_top(self, p, x0, x1, y, seed, night):
        """The button finished as a strap of garnet set in gold with a struck gold coin at its head: see
        `art.link_strap`."""
        A.link_strap(p, p.w, getattr(p, "link_index", seed), night)

    def link_icon(self, index, night, ink):
        """The coin's device is struck in `link_top`; the kit's icon place holds nothing more."""
        return [], {}

    def link_button(self, label, index, night):
        """A link under the footer, its coin struck with the next of the set's devices in the row's order."""
        self._link = index
        try:
            return super().link_button(label, index, night)
        finally:
            self._link = None

    def canvas(self, w, h):
        """A new drawing, a link's knowing which link it is, so its coin is struck with that link's device."""
        p = super().canvas(w, h)
        if getattr(self, "_link", None) is not None:
            p.link_index = self._link
        return p

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """A badge set in gold as a cloisonne mount, kept inside its shape and off its letters: a rim of gold along
        its top over a row of garnets cut in cells between gold walls, gold down each end, lit at the left and in
        shade at the right, a gold wall where the label's garnet meets the value, and gold along its foot."""
        h = s["h"]
        ty = self._text_y(s)
        text_rows = range(ty - 1, ty + (7 if s["font"] == "57" else 5) + 1)

        def ins(x, y):
            return 0 <= x < w and 0 <= y < h and inside(x, y, w, h, s["corner"])
        row = h - 2
        first = next((x for x in range(w) if ins(x, row) and ins(x, row - 1)), 0)
        seam = next((x for x in range(first + 3, w - 2) if ins(x, row) and p.get(x, row) != p.get(x - 1, row)
                     and p.get(x, row - 1) != p.get(x - 1, row - 1) and p.get(x + 1, row) == p.get(x, row)), None)
        for y in range(h):
            xs = [x for x in range(w) if ins(x, y)]
            if not xs:
                continue
            for x in xs:
                if y == 0:
                    p.px(x, y, GOLD[5] if x < w * 0.6 else GOLD[4])
                elif y == 1:
                    p.px(x, y, GOLD[3] if x % 4 == 0 else GARNET[5] if x % 4 == 1 else GARNET[4])
                elif y == h - 1 and y not in text_rows[1:-1]:
                    p.px(x, y, GOLD[2])
            if 1 < y < h - 1:
                p.px(xs[0], y, GOLD[4])
                p.px(xs[-1], y, GOLD[2])
                if seam is not None and seam in xs:
                    p.px(seam, y, GOLD[4])

    def badge_label(self):
        return (GARNET[2], GOLD[5])

    def badge_gold(self):
        return (GOLD[4], RAMP["earth"][0])

    def badge_states(self):
        """A live badge's states as gems: emerald, gold, ruby and onyx."""
        return {"green": (RAMP["emerald"][2], C["white"]), "yellow": (GOLD[4], RAMP["earth"][0]),
                "red": (GARNET[3], C["white"]), "slate": (RAMP["flint"][2], C["white"])}

    def badge_swatches(self):
        """A static badge's value in gold or an enamel, one in each family a written colour comes in; the garnet
        one cut in cells."""
        R = RAMP
        return {"garnet": (GARNET[3], C["white"], "cells"), "amber": (R["amber"][4], R["earth"][0], None),
                "gold": (GOLD[4], R["earth"][0], None), "emerald": (R["emerald"][2], C["white"], None),
                "glass": (R["glass"][2], C["white"], None), "wing": (R["wing"][3], C["white"], None),
                "bone": (R["bone"][6], R["earth"][0], None), "jet": (R["flint"][1], C["white"], None),
                "iron": (R["iron"][4], C["white"], None), "oak": (R["oak"][2], C["white"], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        """Garnet set in a cell: a gold wall along it over the letters and under them, never on their rows, and
        the gold foil glinting through the garnet beyond the walls."""
        if pattern == "cells" and y not in text_rows:
            if y in (text_rows[0] - 1, text_rows[-1] + 1):
                return GOLD[3]
            return GARNET[4] if (x + y) % 4 == 0 else c
        return c

    def badge_outline(self, pattern):
        return GOLD[3] if pattern == "cells" else None

    def badge_shine(self, c, y, h):
        try:
            return step(c, 1) if y == 2 else step(c, -1) if y == h - 1 else c
        except KeyError:
            return c

    def plate_colours(self, mode):
        """A plate is a slab of the barrow's chalk, its value on a garnet set in gold; a live plate is gold."""
        if mode == "day":
            return dict(paper=RAMP["chalk"][5], dot=RAMP["chalk"][3], frame=GOLD[2], block=GARNET[2], ink=C["ink"],
                        letters=GOLD[6])
        if mode == "night":
            return dict(paper=RAMP["earth"][1], dot=RAMP["earth"][3], frame=GOLD[3], block=GARNET[2],
                        ink=C["ink_n"], letters=GOLD[6])
        return dict(paper=GOLD[4], dot=GOLD[3], frame=RAMP["earth"][0], edge=GOLD[1], ink=RAMP["earth"][0])

    def plate_edge(self, block):
        try:
            return step(block, -1)
        except KeyError:
            return block

SET = Hoard()
