# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Illuminated set: a page from the scriptorium, as an illuminator would have painted it, March's design
in the medieval collection, drawn in the collection's hand (`collections.hand`).

Titles are gold leaf on a lapis ground behind a decorated initial, with a vine flourishing from it into
the margin; a border of knotwork in oxblood, lapis and verdigris with beads of gold frames every sheet, and
a vine of gilded leaves hangs across the top, tacked at the top centre under the month's mark. Headers stand
in the margins of the page: a monk at his desk writing under a shelf of books, the tall candle that lights
him, a wyvern coiled in the margin, a snail, a hare blowing a trumpet and birds on the vine; a great book
open on its lectern at the Beatus page and a miniature; a great quill standing in its inkhorn. By day the
vellum is cream, ruled by the scribe; by night the scriptorium is dark but for its candles, each pooling
its light round it, the gold glowing and the flames flickering.
"""
from __future__ import annotations

from ...holidays.designs import NARROW
from ...holidays.designs.badges import inside
from ...holidays.designs.banners import MARK_Y
from ...holidays.pixel import fold, measure, sphere
from ..hand import CollectionSet
from . import art as A
from .palette import C, RAMP, TOKENS, X, step

G, O, L, V = RAMP["gold"], RAMP["oxblood"], RAMP["lapis"], RAMP["verdigris"]
# The link buttons' gilded sprites, down the row: a medallion, a fleur-de-lis, a cross and a codex.
LINK_SPRITES = ("medallion", "lis", "cross", "codex")
ICONS = {
    "medallion": A.MEDALLION,
    "lis": ["...g...", "..gGg..", ".g.G.g.", "gG.G.Gd", ".dgGgd.", "...G...", "..dGd.."],
    "cross": ["..ggg..", "..gGd..", "gg.G.dd", "gGGGGGd", "gg.G.dd", "..gGd..", "..ddd.."],
    "codex": ["ggggggd", "gLLLLGd", "gLgLLGd", "gLLLLGd", "gLLLLGd", "gGGGGGd", "ddddddd"],
}
# Each icon's pigments on the gold roundel it sits on: a lapis medallion with oxblood stones, an oxblood
# fleur-de-lis, a lapis cross and an oxblood codex with cream pages.
ICON_PAL = {
    "medallion": {"g": RAMP["lapis"][4], "G": RAMP["lapis"][3], "d": RAMP["lapis"][2], "L": RAMP["oxblood"][4]},
    "lis": {"g": RAMP["oxblood"][4], "G": RAMP["oxblood"][3], "d": RAMP["oxblood"][2]},
    "cross": {"g": RAMP["lapis"][4], "G": RAMP["lapis"][3], "d": RAMP["lapis"][2]},
    "codex": {"g": RAMP["oxblood"][4], "G": RAMP["oxblood"][3], "d": RAMP["oxblood"][2], "L": RAMP["vellum"][6]},
}
SHEET_RULE = 20     # the row an element's sheet rules off its tag and title at, where the leaves lie sparser
FRAME_IN = A.FRAME + 2   # how far in from a sheet's edge its art keeps, clear of the border
INKSTAND = (24, 29)  # the inkstand with its quill, pounce pot and penknife: its width and its height
# The vine across the top: hung two rows under the garland's row, a span 45 wide on a wide sheet, sagging 3,
# tacked at the top centre under the month's mark (see `art.tacks`).
VINE_DROP, VINE_SPAN, VINE_SAG = 2, 45, 3
# The spans of the vine a bird perches on, across a wide header: the third, the seventh and the ninth.
PERCHES = ((2, False, False), (6, True, True), (8, False, False))
# The great book open on its lectern, the hero of a section (H2), wide and on a phone: how wide and tall the
# book is, and how tall its stand is from the ledge it rests on to its foot.
BOOK = {"H2": (66, 44, 40), "phone": (56, 34, 22)}
# The great quill in its inkhorn, the hero of a strip (H3): the highest row its feather reaches, under the vine
# across the top, and the most rows it rises from the floor it stands on, wide and on a phone.
QUILL_TOP, QUILL_TALL = 19, {"H3": 72, "phone": 50}
# The rows a phone's H2 or H3 asks for under its words for its hero, the great book on its lectern or the great
# quill in its inkhorn, whatever its title and its words: each stands taller than any room a title leaves beside
# it, so it always stands under the words, two units and more clear of the last line.
UNDER = {"H2": 58, "H3": 53}


class Illuminated(CollectionSet):
    collection = "medieval"
    key = "medieval-illuminated"
    name = "Illuminated"
    # What the design is, in words, for the page that shows the collection.
    tagline = (
        "A page from the scriptorium: gold leaf, lapis and a monk at his desk by candlelight.")
    about = (
        "Every sheet is a leaf of a medieval manuscript. Titles are laid in gold leaf, a burnish crossing the "
        "letters every twelve seconds, on a deep lapis panel (oxblood by night) with a gold hairline and a diaper "
        "of dots, the first letter standing on its own square as a decorated initial with an ivy tendril "
        "flourishing from it into the margin. A border of lapis, oxblood and verdigris knotwork beaded with gold "
        "frames every file, and a vine of gilded leaves and flowers swags across the top with birds perched on "
        "it. In the margins a tonsured monk writes at his slanted desk under a shelf of books, a tall candle "
        "beside him, while a wyvern coils with a gilded belly, a hare blows a trumpet and a snail creeps by. The "
        "section's hero is a great book open on its lectern at the Beatus page, its initial in gold on lapis "
        "facing a miniature of a tower on a hill, and the strip's is a great goose quill standing in its inkhorn "
        "as tall as the strip; on a phone they stand under the words at their full height, the book between the "
        "hare and a candle, the quill by its pile of books, each with a vine climbing the margin. By day the vellum "
        "is cream with the scribe's ruling; by night the scriptorium is dark but for its candles, whose flames "
        "flicker and pool warm light round them on the monk, the book and the quill. The footers are the book's "
        "colophon: a twisted cord of oxblood and lapis bound with gold, the rubricator's mark before the notes, a "
        "vine along the foot, and the scribe's corner of books, inkhorn and candle where the cells leave it room. "
        "Badges are painted panels in gold frames, and links are oxblood ribbon bookmarks capped in gold and cut in "
        "a swallowtail. The elements carry stacked gilded panels, an astrolabe limb, vellum tablets with rubric "
        "digits, a vine of painted roundels, the schematic's cards as painted panels on rubric wires, each "
        "contributor as a painted bust in a beaded gold frame (the bot a little automaton), a placard with a bird "
        "perched at its top, and a pendant wax seal on a silk ribbon.")
    tokens = frozenset(TOKENS)
    # On a phone the notes are set under the words, and H1's scene gets the rows the monk at his desk needs.
    phone_scene_rows = 62

    # ---- colour and paper
    def ink(self, night):
        """The set's colours: the hand's iron-gall ink and rubric red on cream vellum by day; the hand's cream
        and gold on the dark scriptorium's vellum by night. `title` stands for the gold leaf (see
        `title_text`); `shadow` is the shade under a check mark."""
        return dict(
            title=X["accent_night"] if night else C["ink"], shadow=O[2] if night else G[2],
            body=self.hand.body[night], muted=self.hand.muted[night],
            rule=X["rule_night"] if night else X["rule_day"], accent=X["accent_night"] if night else X["accent_day"],
            tag=O[3], tag_ink=RAMP["vellum"][6],
            fill=X["node_night"] if night else RAMP["vellum"][6], dim=X["dim_night"] if night else X["dim_day"],
        )

    def lit(self, night):
        """Gold leaf painted over the letters, a tone lighter by night, when it glows in the candlelight."""
        if night:
            return dict(paint=A.LEAF_PAINT, night=True, glow=(G[5], (0.22,)))
        return dict(paint=A.LEAF_PAINT, night=False)

    def paper(self, p, night, uid="p"):
        """The vellum; the drawing keeps which sheet it is (`uid`, "p" for a header or a footer) and
        whether it is night, for the hooks the layout calls without saying."""
        p.sheet, p.night = uid, night
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
        """None: a scriptorium has a ceiling. By night the vellum is lit by candles instead."""

    def frame(self, p, night, webs=False):
        """The knotwork border; and along the top of a footer, inside it, the colophon's twisted cord of
        oxblood and lapis bound with gold. A footer is the sheet the layout frames without webs."""
        A.knot_frame(p, night)
        if not webs and getattr(p, "sheet", "") == "p":
            A.colophon_rule(p, 6, p.w - 6, A.FRAME, night)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """The vine across the top, hung two rows under where a garland hangs so its leaves clear the border:
        a span every 45 units on a wide sheet and every 34 on a phone, each sagging three."""
        A.vine(p, x0, x1, y + VINE_DROP, span=VINE_SPAN if x1 - x0 > NARROW else 34, sag=VINE_SAG, night=night)

    def tag(self, p, x, y, w, h, night):
        """The rubric-red block a tag's cream letters sit on: lit along its top, shaded along its foot. The
        ribbon under a certificate's seal, which the layout sets as a tag centred under the seal, is silk
        of lapis and oxblood with gold ends instead (see `rosette`)."""
        seal = getattr(p, "seal", None)
        if seal and abs(x + w / 2 - seal[0]) <= 1 and y > seal[1]:
            A.words_ribbon(p, x, y, w, h, night)
            return
        p.rect(x, y, w, h, O[3])
        p.hline(x, x + w, y, O[4])
        p.hline(x, x + w, y + h - 1, O[1])

    def title_text(self, p, x, y, s, night, scale):
        """A title in gold leaf: on a panel of lapis (oxblood by night) with a gold hairline and a diaper
        of dots, the first letter of the title on its own square in the other pigment, the decorated
        initial, with a vine flourishing from it into the margin where there is room for one clear of the
        month's mark; every letter edged in dark ink over the shadow its gilding throws, and by night
        glowing. A drawing made lighter to fit its budget keeps all of it, the line set whole as one symbol
        instead of letter by letter (see `title_set`)."""
        k = self.ink(night)
        s = fold(s, "57")
        w = measure(s, "57", scale)
        versal = not getattr(p, "versal", False)
        p.versal = True
        box = A.title_ground(p, x, y, s, w, scale, night, versal=versal)
        edge, shadow = RAMP["ink"][0], O[0] if night else L[0]
        if p.lite:
            w = A.title_set(p, x, y, s, scale, night, edge, shadow, glow=self.lit(night).get("glow"))
        else:
            A.title_edge(p, x, y, s, scale, edge, shadow)
            w = p.text(x, y, s, k["title"], "57", scale, **self.lit(night))
        # Where the gold lies, for the glint that travels across it in a moving header (see `scene`).
        p.gilt = getattr(p, "gilt", []) + [(x, y, s, scale, w)]
        if box and scale >= 2:
            x0, y0, x1, y1 = box
            mid = (y0 + y1) // 2
            if A.room(p, x0 - 9, mid - 7, x0 - 1, mid + 9) and self.clear_of_mark(p, x0 - 12, y0 - 12, x0, y1):
                A.flourish(p, box, night, -1)
            elif (A.room(p, x + w + 4, mid - 7, x + w + 12, mid + 9)
                  and self.clear_of_mark(p, x + w + 3, y0 - 12, x + w + 15, y1)):
                A.flourish(p, (x + w + 3, y0, x + w + 3, y1), night, 1)
        return w

    # ---- the headers' scenes
    def section_mark(self, p, x, y, night):
        """A snail creeping along under the title, the drollery every margin has."""
        A.snail(p, x, y + 6, night, flip=True)

    def strip_mark(self, p, x, y, night):
        A.medallion(p, x, y - 4, night)

    def scene(self, design, p, rule, night, motion):
        """H1: the monk at his desk under a shelf of books, a tall candle beside him, on the left; on the
        right the wyvern coiled in the margin, the hare blowing its trumpet and the snail, with birds on the
        vine. H2, its hero: the great book open on its lectern at the Beatus page and a miniature, a bird on
        its cover, a candle on its pricket, the books put by and the snail. H3, its hero: the great quill
        standing in its inkhorn, as tall as the strip, by a pile of books with a stub of candle on it. A vine
        climbs the right margin of each, birds perched on it. In a moving file the border's gold beads catch
        the light in turn and a glint of burnish crosses each title on the hand's period."""
        if motion:
            A.frame_glints(p, p.w, p.h, seed=rule)
            for n, placed in enumerate(getattr(p, "gilt", [])):
                A.title_glint(p, *placed, n)
        base = rule - 1
        if design == "H1":
            A.candle(p, 9, base, h=48, night=night, phase=0, motion=motion)
            A.book_shelf(p, 18, 54, base - 58, night)
            A.monk_at_desk(p, 12, base, night, motion)
            A.shadow_under(p, 33, base, 20)
            coiled = A.room(p, 366, 14, 410, 64)
            if coiled:
                A.wyvern(p, 370, 22, night, motion)
            A.margin_vine(p, 404, 62 if coiled else 18, base - 1, night, motion, seed=rule)
            A.hare_trumpeter(p, 372, base, night, motion)
            A.snail(p, 396, base, night)
            A.shadow_under(p, 377, base, 5)
            A.shadow_under(p, 400, base, 4)
            for (i, red, flip) in PERCHES:
                bx, off = A.vine_low(5, p.w - 5, VINE_SPAN, VINE_SAG, i)
                if p.clear_of_words(bx - 6, 4, bx + 6, 12) and self.clear_of_mark(p, bx - 6, 4, bx + 6, 12):
                    A.bird(p, bx - 4, 5 + VINE_DROP + off - 5, night, motion, red=red, flip=flip)
            return [(5, 57), (360, 410)]
        if design == "H2":
            w, h, stand = BOOK["H2"]
            x0 = 313
            A.margin_vine(p, 405, 18, base - 1, night, motion, seed=rule + 1)
            gutter = A.book_on_lectern(p, x0, base, w, h, stand, night)
            top = base - stand - h + 2
            A.candle(p, 389, base, h=50, night=night, phase=1, motion=motion)
            for (bx, by, cover, cw) in ((361, base - 3, "oxblood", 14), (362, base - 7, "lapis", 12)):
                A.codex(p, bx, by, cw, cover, night)
            A.bird(p, x0 + 2, top - 5, night, motion, red=True)
            A.snail(p, 395, base, night)
            A.shadow_under(p, gutter, base, 12)
            A.shadow_under(p, 367, base, 7)
            A.shadow_under(p, 389, base, 3)
            A.shadow_under(p, 399, base, 4)
            return [(308, 410)]
        A.margin_vine(p, 405, 18, base - 1, night, motion, seed=rule + 2)
        for (bx, by, cover, cw) in ((355, base - 3, "oxblood", 15), (356, base - 7, "lapis", 13),
                                    (355, base - 11, "verdigris", 14)):
            A.codex(p, bx, by, cw, cover, night)
        A.candle_stub(p, 362, base - 12, night)
        A.great_quill(p, 372, base, max(QUILL_TOP, base - QUILL_TALL["H3"]), night)
        A.snail(p, 396, base, night)
        A.shadow_under(p, 362, base, 9)
        A.shadow_under(p, 383, base, 12)
        A.shadow_under(p, 400, base, 4)
        return [(353, 410)]

    def scene_narrow(self, design, p, y, night, under=False):
        """On a phone: H1's monk at his desk by his candle on the left of the rule, where the words leave
        him the room (the candle and the inkhorn where they do not), the wyvern beside him when there is
        room for it too, and on the right the hare and the snail with the vine climbing the margin from
        the rule up to the words, a bird on it. Beside H3's title a snail creeps under a medallion. The
        heroes of H2 and H3, the great book and the great quill, stand `under` the words on the rule at `y`
        (see `scene_under`, `_under` and `phone_rows`)."""
        if under:
            self._under(design, p, y - 1, night)
            return
        if design == "H1":
            monk = p.clear_of_words(5, y - 50, 56, y)
            A.candle(p, 8 if monk else 10, y - 1, h=30 if monk else 18, night=night, motion=False)
            if monk:
                A.monk_at_desk(p, 10, y - 1, night, motion=False)
                A.shadow_under(p, 31, y - 1, 20)
            elif p.clear_of_words(14, y - 22, 36, y):
                A.inkhorn(p, 16, y - 1, night)
            if A.room(p, 76, y - 41, 118, y):
                A.wyvern(p, 78, y - 35, night, motion=False)
                A.shadow_under(p, 96, y - 1, 14)
            top = y - 2
            while top > 22 and p.clear_of_words(160, top - 3, NARROW - 2, y):
                top -= 1
            if y - top >= 14:
                A.margin_vine(p, 168, top, y - 2, night, False, seed=y)
            if p.clear_of_words(134, y - 24, 164, y):
                A.hare_trumpeter(p, 138, y - 1, night, motion=False)
                A.shadow_under(p, 142, y - 1, 5)
            if p.clear_of_words(162, y - 7, NARROW - 4, y):
                A.snail(p, 164, y - 1, night)
        elif design == "H3" and p.clear_of_words(150, y - 17, NARROW - 6, y + 2):
            A.medallion(p, 158, y - 16, night)
            A.snail(p, 156, y, night, flip=True)

    def _under(self, design, p, base, night):
        """The scene a phone's H2 or H3 stands under its words with its foot on row `base`: for H2 the great book
        open on its lectern at the middle of the phone, at the Beatus page and its miniature, a bird perched on
        its cover and the hare blowing its trumpet to it from the left, and at its right the books put by, a
        candle on its pricket, the snail creeping up and the vine climbing the margin; for H3 at the right the
        great quill standing in its inkhorn, its plume broad, a stub of candle on its dish on a pile of books
        with a bird perched by it, the snail and the vine climbing the margin. By night the candle burns and its
        light falls on them. The drawing keeps the stretch of rule the scene stands on, which the leaves along it
        step round (see `rule_decor`)."""
        if design == "H2":
            w, h, stand = BOOK["phone"]
            x0 = NARROW // 2 - w // 2
            A.hare_trumpeter(p, 28, base, night, motion=False)
            gutter = A.book_on_lectern(p, x0, base, w, h, stand, night)
            A.bird(p, x0 + 3, base - stand - h - 3, night, motion=False, red=True)
            for (bx, by, cover, cw) in ((122, base - 3, "oxblood", 14), (123, base - 7, "lapis", 12)):
                A.codex(p, bx, by, cw, cover, night)
            A.candle(p, 143, base, h=20, night=night, motion=False)
            A.snail(p, 150, base, night)
            A.margin_vine(p, 167, base - stand - h + 4, base - 1, night, False, seed=base)
            for (cx, rx) in ((32, 5), (gutter, 12), (129, 7), (143, 3), (154, 4)):
                A.shadow_under(p, cx, base, rx)
            span = (20, 176)
        else:
            for (bx, by, cover, cw) in ((102, base - 3, "oxblood", 15), (103, base - 7, "lapis", 13),
                                        (102, base - 11, "verdigris", 14)):
                A.codex(p, bx, by, cw, cover, night)
            A.candle_stub(p, 109, base - 12, night)
            A.bird(p, 93, base - 5, night, motion=False)
            A.great_quill(p, 120, base, base - QUILL_TALL["phone"], night, wide=10.0)
            A.snail(p, 146, base, night)
            A.margin_vine(p, 167, base - QUILL_TALL["phone"] + 4, base - 1, night, False, seed=base + 2)
            for (cx, rx) in ((109, 9), (131, 12), (150, 4)):
                A.shadow_under(p, cx, base, rx)
            span = (90, 176)
        p.standing = {base + 1: span}

    def scene_under(self, design, p, y0, y1, night):
        """The phone's hero for an H2 or an H3, stood on the rule at `y1` under the words that end at `y0`, two
        units and more clear of them in the rows asked for its height (see `phone_rows`): drawn by
        `scene_narrow`, which draws every scene a phone has."""
        self.scene_narrow(design, p, y1, night, under=True)

    def phone_rows(self, design, title_w):
        """The rows a phone's H2 or H3 leaves under its words for its hero, whatever its title (`title_w` wide at
        its widest line) and its words: the great book on its lectern and the great quill in its inkhorn each
        stand taller than the room a title leaves beside it (see `UNDER`)."""
        return UNDER[design]

    def rule_decor(self, p, x0, x1, y, seed, night):
        """Gilded ivy leaves resting along a rule, further apart under an element sheet's title, and none
        where a phone's scene stands on the rule (see `_under`)."""
        gap = (30, 60) if y == SHEET_RULE else (22, 40)
        s0, s1 = getattr(p, "standing", {}).get(y, (x1, x1))
        for a, b in ((x0, min(x1, s0)), (max(x0, s1), x1)):
            if a < b:
                A.leaves_on(p, a, b, y, seed=seed, night=night, gap=gap)

    def finish(self, p, night):
        A.candlelight(p, night)

    def _finish(self, p, night):
        """The last pass, the candles' light, on every drawing: the shared layout leaves it off a drawing made
        lighter to fit its budget, and a light is never left off here; such a drawing thins only its outermost
        ring (see `candlelight`)."""
        self.finish(p, night)

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        """The scribe's corner at the end of the notes: on a wide block the inkhorn with its quill standing
        on the frame's rule and a candle beside it, lit by night with its light pooled on the cell; on a
        phone's the inkhorn, the quill laid down beside it and a stub of candle on a dish, up by the notes'
        label. The rubricator's mark in red stands in the gutter before the notes' first line. A footer
        has no finishing pass, so the candle's light is laid once its words are set (see `_footed`)."""
        if p.w > NARROW:
            A.inkhorn(p, x, p.h - 5, night, knife=False)
            A.candle(p, x + 14, p.h - 5, h=16, night=night, motion=False)
        else:
            A.inkhorn(p, x - 10, y + 3, night, pen=False, knife=False)
            A.quill_flat(p, x - 2, y, night)
            A.candle_stub(p, x + 14, y + 8, night)
        A.rubric_mark(p, 4, 14, night)

    def _footed(self, p, night):
        """A footer once its words are set, the book's colophon finished: the scribe's corner, the design's
        mark, at the right end after the way back up wherever the cells leave it the room, and along the foot
        the vine its floor is, wherever the words leave it room; then the candles' light, which a footer has
        no finishing pass to lay."""
        if p.w > NARROW:
            end = max((b[2] for b in p.words), default=0)
            if p.w - FRAME_IN - 40 >= end + 4:
                A.scribe_corner(p, p.w - FRAME_IN - 40, p.h - A.FRAME - 1, night)
        A.foot_vine(p, A.FRAME + 2, p.w - A.FRAME - 2, p.h - A.FRAME - 2, night)
        A.candlelight(p, night)
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
        """The graphic scale's bar in gold leaf and lapis by turns; and at the end of the scale's cell the
        scribe's corner, the inkhorn with its quill and a candle, lit by night with its light pooled on
        the cell (see `_footed`). The layout says nothing of the night here; the paper remembered it."""
        A.gilt_bar(p, x0, y0, w, h, period)
        night = getattr(p, "night", False)
        if p.w > NARROW:
            A.inkhorn(p, 77, p.h - 6, night, knife=False)
            A.candle(p, 91, p.h - 6, h=20, night=night, motion=False)
        else:
            A.inkhorn(p, 74, 32, night, knife=False)
            A.candle(p, 90, 32, h=18, night=night, motion=False)

    def link_colours(self, night):
        """A ribbon bookmark: oxblood silk, edged in gold, lettered in cream (gold by night)."""
        if night:
            return O[2], G[4], G[6], O[0]
        return O[3], G[3], RAMP["vellum"][6], O[1]

    def link_top(self, p, x0, x1, y, seed, night):
        """A braid of gold along the ribbon's top edge with the silk lit just under it; the ribbon's left
        end capped in gold, with the roundel its icon sits on against the cap; its right end cut in a
        swallowtail the ribbon's whole height and five deep, the cut edged in bright gold."""
        k = -1 if night else 0
        for xx in range(x0 - 1, x1 + 1):
            p.px(xx, y, G[5] if (xx + seed) % 3 == 1 else G[3 + (1 if night else 0)])
            p.px(xx, y + 1, O[4 + k] if (xx + seed) % 3 != 2 else O[3 + k])
        for yy in range(y + 1, y + 10):                           # the cap at the left end
            p.px(x0 - 1, yy, G[5])
            p.px(x0, yy, G[4])
            p.px(x0 + 1, yy, G[3])
        A.gold_roundel(p, x0 + 6, y + 5)
        w, mid = x1 + 2, y + 5
        base = p.layers["base"]
        for i in range(5):                                        # the notch, cut out of the ribbon
            for yy in range(mid - 4 + i, mid + 5 - i):
                base.pop((w - 1 - i, yy), None)
        for i in range(5):                                        # the cut's gilded edge
            p.px(w - 1 - i, mid - 5 + i, G[5])
            p.px(w - 1 - i, mid + 5 - i, G[5])
        p.px(w - 6, mid, G[6])

    def link_icon(self, index, night, ink):
        """The link's icon, painted dark on its gold roundel: lapis, oxblood and the cream of a codex's
        pages."""
        name = LINK_SPRITES[index % len(LINK_SPRITES)]
        return ICONS[name], ICON_PAL[name]

    # ---- the elements
    def card_bevel(self, night):
        return (RAMP["ink"][4], RAMP["ink"][1]) if night else (C["white"], RAMP["vellum"][3])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A schematic card as a painted panel: a frame of gold leaf with a hairline of oxblood inside it,
        the icon's cell a square of lapis (oxblood by night) with the icon turned to gold leaf, a band of
        gold leaf with beads of lapis and oxblood between the cell and the words, and a gilded fleuron on
        the lid."""
        A.panel_frame(p, x, y, w, h, night)
        A.icon_cell(p, x, y, w, h, night, self.ink(night)["body"])
        for yy in range(y + 2, y + h - 2):
            bead = (yy - y) % 6 == 3
            p.px(x + 10, yy, G[5])
            p.px(x + 11, yy, (L[4] if (yy - y) % 12 == 3 else O[4]) if bead else G[4])
            p.px(x + 12, yy, G[2])
        if lid:
            A.fleuron(p, x + 9, y - 5)

    def wire_ink(self, night):
        """A wire is a rule of rubric red."""
        return O[4] if night else O[3]

    def wire_lights(self, p, cells, night, seed):
        """A boss of gold at every join of a wire, and gilded leaves along it as if it were a vine: one
        every ninth pixel, above and below by turns."""
        k = -1 if night else 0
        A.wire_bosses(p, cells, night)
        for i, (x, y, d) in enumerate(cells[5:-7]):
            if i % 9 or d != "h":
                continue
            up = (i // 9 + seed) % 2 == 0
            p.px(x, y - 1 if up else y + 1, V[3 + k])
            A.gilt_leaf(p, x - 1, y - 4 if up else y + 2, night, flip=not up)

    def dashes(self, night):
        return [O[4] if night else O[3], G[4] if night else G[3]]

    def ornament(self, kind, p, x, y, night):
        """The scribe's inkstand, its quill standing in it, in a free corner of the schematic."""
        if kind != "schematic":
            return (0, 0)
        if p is not None:
            A.inkstand(p, x, y + INKSTAND[1] - 1, night)
        return INKSTAND

    def hist_bar(self, p, bx, base, bw, v, night):
        A.gilt_panel(p, bx, base, bw, v, self.wire_ink(night))

    def peak_mark(self, p, x, y, night):
        A.gilt_star(p, x - 1, y - 1)

    def dial_ring(self, p, arc, night):
        """The limb of an astrolabe, four pixels deep inside the ring the kit's arc runs along."""
        (xa, ya), (xb, _) = arc[0], arc[-1]
        r = round((xb - xa) / 2 + 1.5)
        A.astrolabe_ring(p, round((xa + xb) / 2), round(ya), r, night)

    def dial_tick(self, p, x, y, night):
        """An hour engraved into the limb."""
        p.px(x, y, RAMP["ink"][1])

    def dial_hub(self, p, cx, cy, night):
        """A boss of gold the alidade turns on, pinned at its heart."""
        sphere(p, cx + 0.5, cy - 0.5, 2.6, G, lo=2)
        p.px(cx, cy - 1, RAMP["ink"][1])

    def material(self, i, xx, yy, y0, y1, lift, night):
        """The illuminator's pigments by turns: lapis, gold leaf, oxblood, verdigris and plain vellum."""
        Ve = RAMP["vellum"]
        kind = i % 5
        if kind == 0:
            c = L[4] if (xx * 7 + yy * 3) % 11 == 0 else L[3]
        elif kind == 1:
            c = G[5] if (xx - yy) % 6 < 2 else G[4]
        elif kind == 2:
            c = O[4] if (xx * 5 + yy * 7) % 13 == 0 else O[3]
        elif kind == 3:
            c = V[4] if (xx + yy) % 3 == 0 else V[3]
        else:
            c = Ve[5] if (xx * 3 + yy) % 7 else Ve[4]
        return step(c, lift)

    def counter_cell(self, q, ox, oy, night):
        A.vellum_tablet(q, ox, oy, night)

    def counter_ink(self, night, dim):
        """A tablet's digit in rubric red, a leading nought faint on the vellum."""
        return RAMP["vellum"][3] if dim else O[3]

    def timeline_line(self, p, x0, x1, y, night):
        """The vine the releases hang from, up to today. A stub too short for a leaf is a bare stem."""
        A.stem(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        A.roundel(p, x, gy, kind, night, i, unlit=self.ink(night)["muted"])

    def today_mark(self, p, x, y, night):
        A.gilt_star(p, x - 2, y - 3, big=True)

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor as a miniature portrait in a gold frame: a bust painted from the seed of their
        name; a bot's portrait is of a little automaton."""
        A.portrait(p, cx, cy, i, person, night)

    def commit_bar(self, p, x, y, w, fill, night):
        """A contributor's share, in gold leaf on a line of ink."""
        p.box(x, y, w + 2, 4, self.wire_ink(night))
        for xx in range(fill):
            p.px(x + 1 + xx, y + 1, G[5] if xx % 5 else G[6])
            p.px(x + 1 + xx, y + 2, G[3])

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """A pendant seal of red wax round the disc; the drawing keeps where the seal is, so the ribbon
        the layout sets under it as a tag can be known for what it is (see `tag`)."""
        p.seal = (cx, cy)
        A.wax_seal(p, cx, cy, r0, r1, night)

    def seal_mark(self, p, x, y, night):
        A.ribbon_tails(p, x, y, night)

    def placard_mark(self, p, x, y, night):
        """A bird perched at the top of the page, turned to the title: the placard's marginal creature."""
        A.bird(p, x, y - 4, night, motion=False, red=True, flip=True)

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """The set's touch on a badge, a painted panel: a frame line of gold leaf round the badge's edge
        inside its shape, lit along the top and the left and shaded along the foot and the right, with a
        bead of light every sixth pixel along the top; a fleuron in each corner where the style leaves
        room for one and a tick where it leaves less; a faint diaper on the label's block above and below
        its letters; and a thin gold rule where the label's block meets the value's. The letters' rows and
        columns are left as the layout painted them."""
        h, corner = s["h"], s["corner"]
        ty = self._text_y(s)
        cap = 7 if s["font"] == "57" else 5
        text_rows = range(ty - 1, ty + cap + 1)
        mid = ty + cap // 2
        row = [p.get(x, mid) for x in range(w)]
        label = row[2]
        boundary = next((x for x in range(3, w - 2) if row[x] not in (label, None)), None)
        for y in range(h):
            for x in range(w):
                if not inside(x, y, w, h, corner):
                    continue
                edge = (x in (0, w - 1) or y in (0, h - 1) or not inside(x - 1, y, w, h, corner)
                        or not inside(x + 1, y, w, h, corner))
                if edge:
                    lit = y == 0 or (x < w // 2 and y < h - 1)
                    p.px(x, y, G[6] if y == 0 and (x + seed) % 6 == 2 else G[4] if lit else G[3])
                elif boundary and x == boundary - 1 and y not in (0, h - 1):
                    p.px(x, y, G[4])
                elif (boundary and 2 <= x < boundary - 2 and y not in text_rows and 1 <= y < h - 1
                      and (x + y) % 4 == 0):
                    p.px(x, y, self._lighter(label))
        if corner == "sharp" and h >= 14:
            for (cx, cy) in ((1, 1), (w - 4, 1), (1, h - 4), (w - 4, h - 4)):
                p.sprite(cx, cy, [".g.", "gGd", ".d."], {"g": G[6], "G": G[5], "d": G[3]})
        elif corner != "pill" and h >= 10:
            for (cx, cy) in ((1, 1), (w - 2, 1)):
                p.px(cx, cy, G[6])
                p.px(cx + (1 if cx == 1 else -1), cy, G[5])
                p.px(cx, cy + 1, G[5])
            for (cx, cy) in ((1, h - 2), (w - 2, h - 2)):
                p.px(cx, cy, G[5])

    @staticmethod
    def _lighter(c):
        """A tone lighter than `c` for the diaper on a block, or `c` itself where its ramp has none."""
        try:
            return step(c, 1)
        except KeyError:
            return c

    def badge_label(self):
        return (L[3], RAMP["vellum"][6])

    def badge_gold(self):
        return (G[3], C["ink"])

    def badge_states(self):
        # Green is verdigris, red oxblood, yellow an orpiment brighter than the gold label, grey a slate ink.
        return {"green": (V[3], C["white"]), "yellow": (X["yellow"], C["ink"]), "red": (O[3], RAMP["vellum"][6]),
                "slate": (C["slate"], C["white"])}

    def badge_swatches(self):
        Ve, I = RAMP["vellum"], RAMP["ink"]
        return {"oxblood": (O[3], Ve[6], None), "madder": (O[4], Ve[6], None),
                "redlead": (RAMP["redlead"][4], C["ink"], None), "gold": (G[4], C["ink"], None),
                "verdigris": (V[3], C["white"], None), "lapis": (L[3], Ve[6], None), "azure": (L[4], Ve[6], None),
                "tyrian": (RAMP["tyrian"][3], Ve[6], None), "vellum": (Ve[6], C["ink"], "outline"),
                "ink": (I[1], Ve[6], "diaper"), "slate": (C["slate"], C["white"], None),
                "sepia": (RAMP["wood"][3], Ve[6], None), "ash": (RAMP["ash"][3], Ve[6], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        if pattern == "diaper" and (x * 5 + y * 11) % 13 == 0 and y not in text_rows:
            return G[4]
        return c

    def badge_outline(self, pattern):
        return G[3] if pattern == "outline" else None

    def badge_shine(self, c, y, h):
        try:
            return step(c, 1) if y == 2 else step(c, -1) if y == h - 1 else c
        except KeyError:
            return c

    def plate_colours(self, mode):
        if mode == "day":
            return dict(paper=C["paper"], dot=RAMP["vellum"][4], frame=O[3], block=L[3], ink=C["ink"],
                        letters=RAMP["vellum"][6])
        if mode == "night":
            return dict(paper=O[1], dot=O[2], frame=G[4], block=G[4], ink=X["body_night"], letters=C["ink"])
        return dict(paper=G[4], dot=G[3], frame=RAMP["ink"][1], edge=G[2], ink=C["ink"])

    def plate_edge(self, block):
        """A live plate's edge: its block a step darker, and dark gold round the orpiment yellow, which is
        on no ramp."""
        try:
            return step(block, -1)
        except KeyError:
            return G[2]


SET = Illuminated()
