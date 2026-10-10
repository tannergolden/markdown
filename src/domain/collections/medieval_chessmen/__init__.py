# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Chessmen set: a winter's game in a Norse hall, the Lewis chessmen in walrus ivory and bone stained red.

Every header is the hall itself: a wall of upright oak planks, weathered pale by day and dark by night, under a
crossbeam, the hall's posts at its ends, and a woven hanging behind its words, a calm twill of natural wool for them
to sit on, bordered in tablet weave of madder, woad and weld. Along its top runs a band carved with the board's long
diagonal in its notation, a1 to h8, and its titles are cut deep and inked dark by day. Footers, links, badges and
elements are panels of polished walrus ivory framed in the edge of a chessboard.

An H1 is the hall: at its left the hearth with its fire, the cauldron over it, the hall's post carved with a
dragon's head and the drinking horn hung from it by its strap, a round shield on the wall, a bench and the gaming
purse spilling its tablemen; at its right the game on its trestle table, a shallow board in perspective with the
Lewis pieces standing on it large enough to read at a glance, the whole board where the room runs wide and its near
corner running off under the frame where the words come nearer, the knight lifting off his square and leaping to
the next, and a soapstone lamp at the board's corner. By day a shaft of winter light from the smoke hole falls on
the game, motes drifting down it; by night the hearth and the lamp are the hall's two lights, a pool round each with
the dark of the hall between, the pieces' faces lit and their shadows thrown long across the board. An H2 is its
showpieces, the king on his throne with his sword across his knees and the berserker biting his shield before him,
as tall as the floor under the crossbeam lets them stand, their eyes wide and staring, the throne's back carved in
plaited interlace and its seat in round arches; an H3 is the queen on her throne with her hand to her cheek,
filling her strip. The ivory is shaded in its honey patina and the red bone in its stain. On a phone each scene is
built to the rows the words leave, the showpieces standing under the words.

A footer lies on the board's edge. Where its cells leave a long stretch of the foot, a rank of the board lies along
it with the pieces taken in the game standing on it and the toppled king of checkmate lying across its end, a
candle lit beside him at night; elsewhere the king lies at the corner of the notes and the pawns taken lie beside
the board. Links are tablemen with their icons carved in them, badges are plaques of carved ivory with labels of
red bone, and the elements are the same set's things: tablets of ivory and thongs of leather, stacks of tablemen, a
quadrant with a bishop's crozier for its hand, numerals carved on tablemen, a rank of the board with pawns at its
releases and a queen being crowned at today, contributors as chessmen stained in their own colours, a crown of red
bone for a seal, and the stone kist the hoard was found in for a placard.

It is the medieval collection's February, drawn in the collection's hand (see `collections.hand`): its words are
set in the hand's two inks, the ivory and the wool they sit on by day fall within the hand's band, its hearth, its
lamp and its candle burn on the hand's flame and flicker on the engine's cadence, and the band's glint passes on the
hand's period. As the month's design it carries the month's sign at the top centre of every header, and on a
phone, where the band is short, its names part into two runs either side of it. The chessmen are carvings, so their
faces stay ivory and red bone."""
from __future__ import annotations

from ...holidays.designs.badges import inside
from ...holidays.pixel import Pix, clip, fold
from ..hand import CollectionSet
from . import art as A
from .palette import C, RAMP, TOKENS, X, step

IV, HO, RD, OAK = RAMP["ivory"], RAMP["honey"], RAMP["stain"], RAMP["oak"]


class Chessmen(CollectionSet):
    """The Chessmen design: the Lewis chessmen at a winter's game in a Norse hall, the medieval collection's
    February."""

    key = "medieval-chessmen"
    name = "Chessmen"
    collection = "medieval"
    tagline = "A winter's game in a hall of oak and wool, the Lewis chessmen in walrus ivory and bone stained red."
    about = ("Every header is the Norse hall itself: a wall of upright oak planks under a crossbeam, the hall's posts "
             "at its ends, and a woven hanging of natural wool bordered in tablet weave hung behind the words. Across "
             "the top runs a carved band naming the board's long diagonal, a1 to h8, in sunken cartouches, a glint of "
             "light travelling along it in a moving header, and the titles are cut deep and inked dark by day, "
             "polished cream over dark hollows by night. The H1 sets the hearth at the left, with its fire, the "
             "cauldron over it, the hall's post carved with a dragon's head, the drinking horn hung by its strap, a "
             "round shield and a bench, and at the right the game on a trestle table, Lewis pieces large enough to "
             "read at a glance standing on a shallow board, the knight leaping from square to square. By day a shaft "
             "of winter light falls from the smoke hole onto the game with motes drifting in it; by night the hearth "
             "and a soapstone lamp by the board are the hall's two lights, a pool of firelight round each with the "
             "dark hall between them. The H2 is its showpieces, the king on his throne with his sword across his "
             "knees and the berserker biting his shield, as tall as the room allows, their eyes wide and staring and "
             "the throne carved in plaited interlace, and the H3 the queen with her hand to her cheek, filling her "
             "strip. The ivory pieces are shaded in their honey patina and the red ones in their stain, and on a "
             "phone each scene is built to the room the words leave. The footer is a panel of ivory on the board's "
             "edge, and where its cells leave room a rank of the board holds the pieces taken in the game standing in "
             "a row, the toppled king lying across its end and a candle burning by him at night. Links are tablemen "
             "with their icons carved in them, and badges are plaques of carved ivory with labels of red bone. The "
             "elements are carved from the same set: stacks of tablemen for the histogram, a quadrant with a bishop's "
             "crozier for its hand, numerals carved on tablemen, a rank of the board with pawns at the releases and a "
             "queen being crowned at today, contributors as chessmen stained in their own colours, a crown of red "
             "bone for the seal, and placards the stone kist the hoard was found in.")
    tokens = frozenset(TOKENS)

    # ---- colour and paper
    def ink(self, night):
        """The set's inks: dark on the ivory by day, pale in the dark hall by night, every text colour at 4.5:1. The
        words are in the hand's two inks; the titles, the labels and the accents keep the set's own ivory, madder and
        firelight."""
        return dict(
            title=IV[4] if night else HO[1], shadow=RAMP["hall"][0] if night else IV[3],
            body=self.hand.body[night], muted=self.hand.muted[night],
            rule=X["rule_night"] if night else X["rule_day"], accent=X["accent_night"] if night else X["accent_day"],
            tag=RD[2], tag_ink=IV[6],
            fill=C["fill_n"] if night else C["fill"], dim=X["dim_night"] if night else X["dim_day"],
        )

    def paper(self, p, night, uid="p"):
        """Polished walrus ivory, or by night the same ivory in the dark hall (see `art.paper`)."""
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        """The colour behind row y: the ivory, or the night's band of the hall there."""
        return A.bg_at(p, night, y)

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """A header's ground: the hall's wall of planks down to the floor at row y1 and its crossbeam under the band
        (see `art.hall_wall`), over the ivory the figures stand on; by night the hall dark, warmed from the hearth's
        side."""
        A.paper(p, night, hall=True)
        A.hall_wall(p, night, y1)
        A.crossbeam(p, night)
        p.motion = motion

    def frame(self, p, night, webs=False):
        """The board's edge round the sheet; a footer (the sheet framed without webs on the banners' paper) leaves its
        foot to the board's edge its last pass lays there."""
        A.frame(p, night, header=webs, footer=not webs and getattr(p, "sheet", "") == "p")

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """The band carved with the board's notation along a header's top, its glint running only in a wide
        moving header (see `art.notation`)."""
        A.notation(p, 0, p.w, night, motion=getattr(p, "motion", False) and p.w > 200)

    def tag(self, p, x, y, w, h, night):
        """A label of bone stained red, its upper edge catching the light. The ribbon under a certificate's seal, the
        one tag set low on its sheet, is a band of tablet weaving, its edges woven in ivory, its ends falling either
        side cut in forks where its column has room for them."""
        p.rect(x, y, w, h, RD[2])
        if y >= 30 and h >= 9:
            tail = min(4, x - 6, (100 if p.w == 415 else 88) - 2 - (x + w))
            A.ribbon_band(p, x, y, w, h, night, tail=tail if tail >= 3 else 0)
            return
        p.hline(x, x + w, y, RD[4])
        p.hline(x, x + w, y + h - 1, RD[0])

    def title_text(self, p, x, y, s, night, scale):
        """A title carved deep in the ivory (see `art.carved_title`)."""
        return A.carved_title(p, x, y, s, night, scale)

    @staticmethod
    def _fits(p, draw, ceil=False):
        """Whether everything `draw(q)` lays on a scratch drawing the size of `p` keeps two units from every word on
        `p`, and, `ceil`, stands below the crossbeam."""
        q = Pix(p.w, p.h)
        draw(q)
        cells = set(getattr(q, "filled", ()))
        for layer in q.layers.values():
            cells |= set(layer)
        if ceil and cells and min(y for _, y in cells) < A.CEIL:
            return False
        return all(p.clear_of_words(x - 2, y - 2, x + 3, y + 3) for x, y in cells)

    def scene(self, design, p, rule, night, motion):
        """A wide header's scene on its floor: the hall on an H1, the court on an H2 and the queen on an H3, each
        as wide as the words leave it room. Returns the spans of the rule it covers."""
        g = rule - 1
        if design == "H1":
            return self._hall(p, g, night, motion)
        draw = A.court if design == "H2" else A.queen_seat
        for layout in A.COURT_ORDER:
            if self._fits(p, lambda q, lay=layout: draw(q, 409, g, night, lay), ceil=True):
                return [draw(p, 409, g, night, layout)]
        return []

    @staticmethod
    def _room(p, x0, x1, g, most, least):
        """The rows free of words over the floor at row g between x0 and x1, `most` at the most, keeping three rows of
        margin above and two beside; None when fewer than `least` are free."""
        for room in range(most, least - 1, -1):
            if p.clear_of_words(x0 - 2, g - room - 3, x1 + 2, g + 3):
                return room
        return None

    # ---- a phone's scenes
    phone_scene_rows = 66            # a phone's hall: the hearth and the game under its words, its notes set above
    PHONE_ROWS = {"H2": 86, "H3": 60}   # the rows the court and the queen take under a phone's words
    _under = None                    # the header being laid out with those rows

    def scene_narrow(self, design, p, y, night):
        """A phone's hall on an H1, built to the rows its words leave free between the hall's posts: the hearth and
        the game under the words (`art.phone_hall`). A phone's H2 and H3 stand their showpieces under their words
        instead (see `scene_under`)."""
        if design == "H1":
            g = y - 1
            room = self._room(p, 5, 176, g, self.HALL_ROWS, 44)
            if room:
                A.phone_hall(p, g, night, room)

    HALL_ROWS = 66                   # the rows a phone's hall stands in, under its words and its notes

    def h1_narrow(self, h, night):
        """A phone's H1, its hall given the rows it stands in under the words and the notes set under them, however
        many notes there are."""
        self.phone_scene_rows = self.HALL_ROWS + 4 + 10 * len(self.said(h))
        try:
            return super().h1_narrow(h, night)
        finally:
            del self.phone_scene_rows

    def h2_narrow(self, h, night):
        """A phone's H2, laid out with rows under its words for the showpieces at their full size (see
        `phone_rows`): the hand's hero on a phone stands forty rows tall or more, which beside the words would reach
        into the crossbeam, so the court always stands under them."""
        return self._phone("H2", super().h2_narrow, h, night)

    def h3_narrow(self, h, night):
        """A phone's H3, laid out with rows under its words for the queen at her full size (see `phone_rows`)."""
        return self._phone("H3", super().h3_narrow, h, night)

    def _phone(self, design, draw, h, night):
        """A phone's `design` header drawn by `draw` with the rows under its words that `phone_rows` gives it."""
        self._under = design
        try:
            return draw(h, night)
        finally:
            self._under = None

    def phone_rows(self, design, title_w):
        """The rows a phone's H2 or H3 leaves under its words for its showpieces: as many as the court or the queen
        needs."""
        return self.PHONE_ROWS[design] if self._under == design else 0

    def scene_under(self, design, p, y0, y1, night):
        """The scene under a phone's words, from the last of them at row y0 to the rule at y1: on an H2 the court of
        great pieces on a stretch of the board, on an H3 the queen on hers."""
        if design == "H2":
            A.phone_court(p, y1 - 1, night)
        else:
            A.phone_queen(p, y1 - 1, night)

    def _hall(self, p, g, night, motion):
        """The left of an H1, the hearth of the hall with its fire, its horn and its purse, the dragon's head on its
        post and a round shield on the wall where the words leave them room, the tablemen spilled beside it and a
        bench on the floor where the words leave the floor clear; at its right the game on its table, staged as
        wide as the words leave it room, the knight making his move. Returns the spans of the rule they cover."""
        spans = []
        for wall, spill in ((2, True), (2, False), (1, True), (1, False), (0, True), (0, False)):
            if self._fits(p, lambda q, w=wall, s=spill: A.hearth(q, 6, g, night, False, spill=s, wall=w)):
                spans.append(A.hearth(p, 6, g, night, motion, spill=spill, wall=wall))
                if self._fits(p, lambda q: A.bench(q, spans[0][1] + 4, g + 1, night)):
                    A.bench(p, spans[0][1] + 4, g + 1, night)
                    spans[0] = (spans[0][0], spans[0][1] + 6 + A.BENCH_W)
                break
        if self._fits(p, lambda q: A.staged_game(q, 409, g, night, True, "wide")):
            spans.append(A.staged_game(p, 409, g, night, motion, "wide"))
            return spans
        for x0 in range(250, 372):
            if self._fits(p, lambda q, x=x0: A.staged_game(q, 409, g, night, True, "corner", x0=x)):
                reach = next((r for r in range(60, 0, -4) if self._fits(
                    p, lambda q, x=x0, r=r: A.staged_game(q, 409, g, night, True, "corner", x0=x, reach=r))), 0)
                spans.append(A.staged_game(p, 409, g, night, motion, "corner", x0=x0, reach=reach))
                break
        return spans

    def section_mark(self, p, x, y, night):
        """A red pawn beside SECTION A-A, as tall as the room between the title's carving and the words under it
        lets it stand: full size, smaller, or smallest."""
        for kind, foot in (("pawn", y + 9), ("pawn_s", y + 8), ("pawn_xs", y + 7)):
            if self._fits(p, lambda q, k=kind, f=foot: A.piece(q, k, "red", x + 4, f, night)):
                A.piece(p, kind, "red", x + 4, foot, night)
                return

    def strip_mark(self, p, x, y, night):
        """The ivory knight on his pony beside a strip's title, his plinth on the title's foot."""
        if self._fits(p, lambda q: A.piece(q, "knight", "ivory", x + 9, y + 12, night)):
            A.piece(p, "knight", "ivory", x + 9, y + 12, night)

    def finish(self, p, night):
        """The last pass: on a header the woven hanging behind its words and the hall's posts at its ends; by night
        the hearth's light on what stands near it; on an instruments sheet the dial's hand made a bishop's crozier."""
        if getattr(p, "hall", None) is not None:
            A.hanging(p, night)
            A.wall_posts(p, night)
        if night:
            A.firelight(p)
        if getattr(p, "dial", None):
            A.crozier_hand(p, night, self.ink(night)["accent"])

    def _finish(self, p, night):
        """The last pass, on a drawing made lighter to fit its budget as on any other: the lighter drawing keeps the
        hearth's light, thinned to its near half (see `art.firelight`), and the crozier."""
        self.finish(p, night)

    def rule_decor(self, p, x0, x1, y, seed, night):
        """A rank of the board inlaid along a rule where no scene stands on it, kept two units from every word."""
        A.rank_inlay(p, x0, x1, y, night)

    # ---- the elements
    def card_bevel(self, night):
        """A card's edge, lit and shaded: polished ivory by day, ivory in the dark by night."""
        return (IV[2], RAMP["hall"][0]) if night else (X["sheen"], IV[4])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A card as a tablet of ivory: its icon carved in a tableman at its left, of bone stained red and of ivory
        by turns, and along its lid a rank of the board inlaid."""
        A.tablet_card(p, x, y, w, h, night, self.ink(night)["body"], seed, lid)

    def wire_ink(self, night):
        """The leather of a wire, its arrow and the ribbon's edge."""
        return RAMP["leather"][5] if night else RAMP["leather"][2]

    def wire_lights(self, p, cells, night, seed):
        """The wire as a thong of leather, twisted, knotted where it bends."""
        A.thong(p, cells, night)

    def dashes(self, night):
        """A group's border cut in red bone and the honey of the patina by turns."""
        return [RD[4], HO[4]] if night else [RD[3], HO[3]]

    def ornament(self, kind, p, x, y, night):
        """The berserker of red bone biting the rim of his shield, in a free corner of the schematic."""
        if kind == "schematic":
            if p is not None:
                A.piece(p, "berserker", "red", x + 6.5, y + 23, night)
            return (13, 23)
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as a stack of tablemen, every fifth stained red as a player counts his men."""
        A.tablemen_stack(p, bx, base, bw, v, night)

    def peak_mark(self, p, x, y, night):
        """A small crown of red bone beside the busiest week's count."""
        A.crown_mark(p, x, y, night)

    def dial_ring(self, p, arc, night):
        """The dial as a quadrant of carved ivory, a groove along its middle."""
        cx = (arc[0][0] + arc[-1][0]) / 2
        cy = arc[0][1]
        r = (arc[-1][0] - arc[0][0]) / 2 + 1.5
        p.dial = (cx, cy, r)
        A.quadrant(p, arc, night)

    def dial_tick(self, p, x, y, night):
        """A ring and dot cut in the quadrant."""
        A.ring_dot(p, x, y, night)

    def dial_hub(self, p, cx, cy, night):
        """The boss of ivory the crozier turns on."""
        A.ivory_boss(p, cx, cy, night)

    def material(self, i, xx, yy, y0, y1, lift, night):
        """The hall's materials by turns (see `art.matter`)."""
        return A.matter(i, xx, yy, y0, y1, lift, night)

    def counter_cell(self, q, ox, oy, night):
        """A tableman standing on its edge for a numeral to be carved in (see `art.counter_disc`)."""
        A.counter_disc(q, ox, oy, night)

    def counter_ink(self, night, dim):
        """A numeral carved in the tableman: dark in the ivory, a leading nought cut shallower."""
        return IV[2] if dim else HO[0]

    def timeline_line(self, p, x0, x1, y, night):
        """A rank of the board the releases stand on, up to today."""
        if x1 - x0 >= 2:
            A.rank_line(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        """A pawn on the rank at a release (see `art.release_piece`)."""
        A.release_piece(p, x, gy, kind, night, i)

    def today_mark(self, p, x, y, night):
        """A queen being crowned at today's end of the rank: standing on it where the words and the releases leave
        her room, else just past its end in front of the line; in the key, and where neither leaves room, the crown
        alone."""
        w, h = len(A.QUEEN_S[0]), A.QUEEN_S_H
        if y < p.h - 24:
            stood = getattr(p, "stood_at", [])
            for qx, foot in ((x, y + 3), (x + w // 2 + 3, y + 11)):
                x0, top = qx - w // 2, foot - h
                if p.clear_of_words(x0 - 2, top - 2, x0 + w + 2, foot + 2) and not any(
                        x0 - 1 < b[2] and b[0] < x0 + w + 1 and top < b[3] and b[1] < foot for b in stood):
                    A.queen_crowned(p, qx, foot, night)
                    return
        A.gilt_crown(p, x - 2, y - 3, night)

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor as one of the chessmen, head and shoulders, stained in their own colour: a king, a queen, a
        bishop and a warder by turns; a bot as a plain pawn."""
        A.bust(p, cx, cy, i, night, bot=not person.get("initials"))

    def commit_bar(self, p, x, y, w, fill, night):
        """A contributor's share as a groove cut in the ivory with tablemen of red bone laid in it as far as their
        commits reach."""
        A.counters_bar(p, x, y, w, fill, night)

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """The seal as a king's crown of red bone carved round it."""
        A.crown_seal(p, cx, cy, r0, r1, n, night)

    def seal_mark(self, p, x, y, night):
        """A tableman of ivory set at the seal's foot."""
        A.seal_tableman(p, x, y, night)

    def placard_board(self, p, night):
        """The stone kist the hoard was found in, its lid carved."""
        A.kist(p, night)

    def placard_mark(self, p, x, y, night):
        """The small king of ivory standing on the kist's lid."""
        A.stamp(p, x + 1, y - 7, A.KING_S, A.piece_pal("ivory", night))

    def footer_mark(self, p, x, y, night):
        """Where the toppled king lies at the corner of a footer's closing notes: laid once the footer's words are
        set, on the board's edge along its foot (see `art.footing`)."""
        p.mark_at = (x + 18, y)

    def _footed(self, p, night):
        """A footer once its cells are laid: the board's edge along its foot, the captured pieces laid beside it and
        the toppled king at the corner of the notes."""
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

    def heart(self, p, x, y):
        """The heart in BUILT WITH (heart) BY, of bone stained red, lit on its upper left."""
        p.sprite(x, y, [".rr.rr.", "rRRrRRr", "rRRRRRr", ".rRRRr.", "..rRr..", "...r..."], {"r": RD[1], "R": RD[3]})

    def bar(self, p, x0, y0, w, h, period=5):
        """The graphic scale's bar as a rank of the board: squares of red bone and of ivory by turns, a square every
        `period` pixels."""
        for x in range(x0, x0 + w):
            for y in range(y0, y0 + h):
                p.px(x, y, RD[3] if ((x - x0) // period) % 2 == 0 else IV[5])

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """A badge as a plaque of carved ivory: along its top two rows a rank of the board inlaid, squares of ivory
        and of red bone by turns, lit along their tops; a cut where the label's block meets the value's; and its
        foot in shade. All of it kept inside the badge's shape and off its letters."""
        h = s["h"]
        k = -1 if night else 0

        def ins(x, y):
            return 0 <= x < w and 0 <= y < h and inside(x, y, w, h, s["corner"])
        row = h - 2 if (h - 2) % 4 != 2 else h - 3
        first = next((x for x in range(w) if ins(x, row) and ins(x, row - 1)), 0)
        edge = next((x for x in range(first + 2, w) if ins(x, row) and p.get(x, row) != p.get(x - 1, row)
                     and p.get(x, row - 1) != p.get(x - 1, row - 1)), w)
        for y in range(h):
            for x in range(w):
                if not ins(x, y):
                    continue
                red = (x // 3) % 2 == 1
                if y == 0:
                    p.px(x, y, RD[5 + k] if red else IV[6 + k])
                    continue
                if y == 1:
                    p.px(x, y, RD[2 + k] if red else IV[3 + k])
                    continue
                c = p.get(x, y)
                try:
                    if y == h - 1 or (x == edge and edge < w):
                        p.px(x, y, step(c, -1))
                except KeyError:
                    pass

    def badge_label(self):
        """A static badge's label: bone stained red, its letters ivory."""
        return (RD[2], IV[6])

    def badge_gold(self):
        """A live badge's label: gilt, its letters the dark of the patina."""
        return (RAMP["gilt"][4], HO[0])

    def badge_states(self):
        """The live states as the stains of the hall: verdigris, weld, madder and the grey of the kist's stone."""
        return {"green": (RAMP["verd"][2], IV[6]), "yellow": (RAMP["weld"][4], HO[0]),
                "red": (RD[3], IV[6]), "slate": (RAMP["stone"][3], IV[6])}

    def badge_swatches(self):
        """The value's block: ivory, or ivory soaked in one of the carver's stains."""
        R = RAMP
        return {"madder": (RD[3], IV[6], None), "amber": (R["fire"][3], HO[0], None),
                "weld": (R["weld"][4], HO[0], None), "verdigris": (R["verd"][2], IV[6], None),
                "woad": (R["woad"][2], IV[6], None), "sloe": (R["sloe"][2], IV[6], None),
                "ivory": (IV[5], C["ink"], "grain"), "jet": (R["hall"][2], IV[6], None),
                "stone": (R["stone"][3], IV[6], None), "oak": (R["oak"][3], IV[6], None),
                "gilt": (R["gilt"][4], HO[0], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        """Ivory with the grain of the tusk running along it, kept off the letters' rows."""
        if pattern == "grain" and y not in text_rows and (x * 3 + y * 7) % 11 < 4:
            return IV[4]
        return c

    def badge_outline(self, pattern):
        """The line round a block of ivory."""
        return IV[3] if pattern == "grain" else None

    def badge_shine(self, c, y, h):
        """Plastic's gloss: the plaque's foot a step in shade."""
        try:
            return step(c, -1) if y == h - 1 else c
        except KeyError:
            return c

    def plate_colours(self, mode):
        """A plate is a slip of ivory: polished by day and in the hall's dark by night, the value on a block of
        red bone with ivory letters; a live plate is gilt."""
        if mode == "day":
            return dict(paper=IV[5], dot=IV[4], frame=IV[1], block=RD[2], ink=C["ink"], letters=IV[6])
        if mode == "night":
            return dict(paper=RAMP["hall"][3], dot=RAMP["hall"][5], frame=IV[2], block=RD[2], ink=C["ink_n"],
                        letters=IV[6])
        return dict(paper=RAMP["gilt"][4], dot=RAMP["gilt"][5], frame=HO[0], edge=RAMP["gilt"][2], ink=HO[0])

    def plate_edge(self, block):
        """The edge round a live plate's value: its stain a step darker."""
        return step(block, -1)

    def link_colours(self, night):
        """A tableman's tag: its ivory face, its edge, the dark letters on it and its shaded foot."""
        return (IV[5] if not night else IV[4]), IV[0], C["ink"], IV[3]

    def link_icon(self, index, night, ink):
        """The icon carved in a link's tableman, a crown, a knight, a mitre and a pawn by turns."""
        return A.link_icon(index, night)

    def link_button(self, label, index, night):
        """A link under the footer, 26 px tall like the kit's: a tableman, ivory or red by the button's place in the
        row, with its icon carved in it, on a tag of ivory its label is lettered on in capitals (see
        `art.tableman_link`)."""
        text = clip(fold(label, "57").upper(), 360)
        p = self.canvas(A.LINK_TEXT + Pix.measure(text) + 6, 13)
        A.tableman_link(p, index, night)
        p.text(A.LINK_TEXT, 4, text, C["ink"])
        return p


SET = Chessmen()
