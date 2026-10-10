# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Tapestry set: the embroidered hanging, after the Bayeux Tapestry.

Every sheet is woven linen hung from a turned rod, hemmed down its sides with a running stitch and fringed with
tassels along its foot, drawn in the medieval collection's hand (see `collections.hand`). A border band of stitched
beasts (a lion, a griffin, a hawk, a hound), knotwork and vine runs across the top of a header with the comet
crossing behind it, pausing for the month's mark where the header carries it, and a lower border of the same beasts
over a braid runs along its stats rule, stepping down to the braid where the words come near. Titles are laid in
wool, a letter a colour, couched round with a darker thread. The scenes stand on the lower border: on an H1 the
charge, two knights at the gallop on horses set pixel by pixel, one further back and higher, against the English
shield wall under a tall tree; on an H2 the great horseman under his great banner, grown to twice the knights' size
as the embroiderers drew the duke larger than the men about him; on an H3 the hunt, Harold himself grown twice as the
duke is, on foot with his hawk on his fist and his great hound running before him, under the tall tree grown to rise
the strip's full height. A phone's H2 and H3 stand the great horseman and the hunt under their words. The faces and
hands are stitched in the hand's three skins. By night the hanging is in a torchlit hall: the linen falls to umber,
torches burn on the hand's flame in iron brackets with their smoke rising and their light pooled wide on the cloth,
and the letters are couched in gold that catches it.
A footer stands on the lower border sewn on its hem, its beasts walking wherever the words leave them the rows, and
carries the design's mark, Halley's comet as the embroidery shows it: flying over the beasts at a title block's right
end, a torch beside it by night, and falling beside a scale bar. At the corner of a footer's notes a needle trails its
thread, a torch by night. Links are embroidered patches; badges are cloth patches with a running stitch round their
edge; and the elements are laid and couched columns, a wheel of fortune with a needle for its hand, numerals on
patches, gonfanons hung from a couched cord, figures in profile, a stitched roundel, whip stitched cards on couched
wires, and cloth banners hung from a rod.
"""
from __future__ import annotations

import math

from ...holidays.designs import NARROW, WIDE
from ...holidays.designs.badges import inside
from ...holidays.designs.banners import MARK_Y
from ..hand import CollectionSet
from . import art as A
from .palette import C, RAMP, TOKENS, WOOLS, X, step

L_, T_, M_, O_, W_, U_, G_, S_ = (RAMP[n] for n in ("linen", "terracotta", "mustard", "olive", "woad", "umber", "gold",
                                                     "steel"))
LINK_SPRITES = ("shield", "crown", "hawk", "horse")
SHEET_RULE = 20   # the row an element's sheet rules off its tag and title at
# The rows a phone's H2 and H3 ask for under their words: the great horseman's room over the lower border, and the
# great hunt's, Harold under the tall tree, which grows to the rows the lower border leaves it, some 56.
PHONE_UNDER = {"H2": 80, "H3": 63}
HUNT_END = WIDE - A.TORCH_IN - 11   # a wide strip's hunt ends here, two columns short of the right corner torch
H1_RISE = 7                         # a wide H1's tall tree rises seven tenths of the rows from the top band to its feet
FOOT_TORCH = 14                     # a title block's torch by night stands this far in from its right edge
# Where the comet lies beside a scale bar, (x0, y0, x1, y1, the sizes that suit it, see `art.COMETS`): on a wide sheet
# right of the bar and short of its cell's divider, falling; on a phone's between the bar and the way back up, level.
SCALE_COMET = (70, 5, 94, 40, (3, 4))
PHONE_SCALE_COMET = (64, 5, 98, 33, (2, 3, 4))


class Tapestry(CollectionSet):
    collection = "medieval"
    key = "medieval-tapestry"
    name = "Tapestry"
    # What the design is, in words, for the page that shows the collection.
    tagline = (
        "An embroidered hanging after Bayeux: knights set pixel by pixel at the gallop between borders of beasts, lit "
        "by torches by night.")
    about = (
        "Every sheet is a length of warm woven linen, its weave strong enough to read as cloth, hung from a turned "
        "rod, hemmed with a running stitch and fringed with tassels at its foot. Across the top runs the Bayeux "
        "border, a lion with a raised paw, a griffin with a lifted wing, a hawk and a collared hound between knots and "
        "vine, pausing for the month's mark and standing even about it, and a lower border of the same beasts over a "
        "braid runs along every header's stats rule, stepping down to the braid alone wherever the words come near. "
        "Titles are laid in wool, a letter a colour, couched round with a darker thread. Between the borders the H1 "
        "shows the charge: two knights on horses set pixel by pixel, necks arched, manes and tails flying, galloping "
        "in a three frame stride, one further back and higher as the embroiderers drew them, lances level and pennons "
        "streaming, against a shield wall of three whose spears are braced, raised and upright under a tall twisted "
        "tree. The H2 has a great horseman, twice the size of the knights as the embroiderers drew the duke larger "
        "than the men about him, under his great gonfanon with a hound running ahead, and the H3 Harold himself, grown "
        "twice as the duke is, standing with his hawk on his fist and his great hound running before him under a tall "
        "tree that rises the strip's full height. The faces and hands of the knights, the men of the wall and Harold "
        "are stitched in three skins. By night the hanging is in a torchlit hall: the linen falls to deep umber, "
        "torches in iron brackets burn with their smoke rising and throw wide warm pools on the cloth, and the letters "
        "are couched in gold thread that catches the light along their tops, with a few stitches glinting. On a phone "
        "a knight still gallops over the lower border beneath the words with a footman and a tree, and the great "
        "horseman or Harold with his hound stands under the words of a section or a strip, lit by a torch on the hem "
        "at night. The footer stands on the lower border sewn on its hem, its beasts walking wherever the words leave "
        "them room, with Halley's comet flying over them at its right end and falling beside the scale bar, and at the "
        "corner of its notes a steel needle trailing its thread by day and small torches by night. Links are "
        "embroidered patches, and badges are cloth patches edged with a running stitch. The elements show their "
        "needlework: laid columns with a stitched top, a wheel of fortune whose hand is a steel needle, whip stitched "
        "cards with braided seams on couched threads of two wools, gonfanons with tails along the milestones, and "
        "torches on the hems by night.")
    tokens = frozenset(TOKENS)
    phone_scene_rows = 60   # a phone's charge: a knight at the gallop over the lower border, its notes set above

    # ---- colour and paper
    def ink(self, night):
        return dict(
            title=G_[4] if night else U_[2], shadow=U_[0] if night else L_[3],
            body=self.hand.body[night], muted=self.hand.muted[night],
            rule=X["rule_night"] if night else X["rule_day"], accent=G_[4] if night else T_[2],
            tag=T_[2], tag_ink=L_[6],
            fill=C["fill_n"] if night else C["fill"], dim=X["dim_night"] if night else X["dim_day"],
        )

    def lit(self, night):
        """Letters laid in wool, a letter a colour (see `title_text`, which couches them round first)."""
        return dict(paint=A.WOOL, night=night)

    def paper(self, p, night, uid="p"):
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        return A.bg_at(p, night, y)

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        """None: the hanging is indoors, in a hall lit by torches."""

    def frame(self, p, night, webs=False):
        """The rod, the hems and the fringe, and by night a header's corner torches. A footer, the sheet the
        layout frames without webs on the banners' paper, has its own torch at its notes and no knotwork under its
        rod, where its words stand."""
        A.frame(p, night, header=webs, footer=not webs and getattr(p, "sheet", "") == "p")

    def roundel(self, p, margin=2):
        """The box the month's mark takes at the top centre of a header, `margin` units wider all round, as (x0, y0,
        x1, y1), ends excluded."""
        n = self.hand.mark_size
        x0, y0 = p.w // 2 - n // 2, MARK_Y - n // 2
        return (x0 - margin, y0 - margin, x0 + n + margin, y0 + n + margin)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """The border band of beasts across the top, clear of the torches at the corners; in a wide header
        the comet crosses behind it. Where the header carries the month's mark, the beasts pause for it, ending
        either side of it with the twin rules running on behind it (see `art.border`)."""
        gap = self.roundel(p)[::2] if self.marked else None
        A.border(p, x0 + 12, x1 - 12, night, seed=seed, comet=p.w == WIDE, gap=gap)

    def tag(self, p, x, y, w, h, night):
        """A patch of terracotta wool a tag's cream letters are stitched on, with a running stitch along
        its top and its foot."""
        p.rect(x, y, w, h, T_[2])
        A.running(p, x, x + w, y, L_[5], on=2, off=2)
        A.running(p, x, x + w, y + h - 1, L_[5], on=2, off=2, phase=2)

    def title_text(self, p, x, y, s, night, scale):
        return A.title(p, x, y, s, scale, night, self.ink(night)["title"], lite=p.lite)

    # ---- the headers' scenes
    def section_mark(self, p, x, y, night):
        """A kite shield beside SECTION A-A, its couching a row above the words and its point two under them:
        two rows clear of the title's foot above and of the tagline below."""
        A.kite_shield(p, x + 1, y, night, "terracotta")

    def strip_mark(self, p, x, y, night):
        """A crown beside a strip's title."""
        A.crown(p, x, y - 4, night, big=True)

    @staticmethod
    def _room(p, x0, x1, g, most, least):
        """The rows free of words over the ground at row g between x0 and x1, `most` at the most and never into the
        upper border band, keeping three rows of margin above and two beside; None when fewer than `least` are
        free."""
        for room in range(min(most, g - A.BAND[1] - 2), least - 1, -1):
            if p.clear_of_words(x0 - 2, g - room - 3, x1 + 2, g + 3):
                return room
        return None

    def _widest(self, p, x0, edges, g, most, least):
        """The widest of the columns from x0 to each of `edges` whose room reaches `least` rows: (x1, room), or
        None."""
        for x1 in edges:
            room = self._room(p, x0, x1, g, most, least)
            if room:
                return x1, room
        return None

    def scene(self, design, p, rule, night, motion):
        """The scenes stand on the lower border (see `rule_decor`), each side built to the rows its words leave
        between the border's two bands, every figure two units clear of every word at every moment of its motion.
        H1: the charge, two knights at the gallop riding in from the left, one further back and higher (see
        `art.charge`), against the English shield wall under the tall tree at the right, the tree grown to rise
        seven tenths of the band where the rows allow (see `art.defenders`). H2: the great horseman (see
        `art.great_horseman`) with his great banner raised high under the tall tree at the right, and a hound running
        before him where the words leave it the columns. H3: the great hunt at the right (see `art.great_hunt`),
        Harold grown twice with his hawk on his fist under the tall tree grown to the strip's full height, and his
        great hound running before him where the columns allow, short of the right corner torch by night. In a
        moving header the horses gallop and the pennons and the banner wave. Returns no spans: the border runs on
        under them."""
        still = not motion
        spans = A.band_spans(p, 5, WIDE - 5, rule)
        if design == "H1":
            A.charge(p, 5, 62, A.ground(spans, 5, 62, rule), night, A.BAND[1] + 3, still)
            g = A.ground(spans, 350, WIDE - 4, rule)
            rise = max(len(A.TALL), H1_RISE * (g - A.BAND[1]) // 10)
            A.defenders(p, 348, WIDE - 5, g, night, A.BAND[1] + 3, rise)
            return []
        if design == "H2":
            g = A.ground(spans, 300, WIDE - 4, rule)
            for x0 in range(240, 390, 4):
                room = self._room(p, x0, 410, g, 80, 22)
                if room and A.great_horseman(p, x0, 410, g, night, room, still=still):
                    break
            return []
        for level, g in ((2, rule - A.LOW - 1), (1, rule - 3), (0, rule - 1)):
            x0 = A.stretch(spans, level, HUNT_END)
            if x0 is not None and A.great_hunt(p, x0, HUNT_END, g, night, A.BAND[1] + 3):
                break
        return []

    def scene_narrow(self, design, p, y, night):
        """A phone's scenes, each built to the rows its words leave free over it: on H1 a knight at the gallop at
        the left over the lower border and the tree with a man of the wall at the right. Where fewer rows are free
        than the smallest build needs, nothing stands. An H2's or H3's scene stands under its words instead, in the
        rows it asks for there (see `phone_rows` and `scene_under`)."""
        if design == "H1":
            spans = A.band_spans(p, 5, NARROW - 5, y)
            A.lower_band(p, 5, NARROW - 5, y, night, seed=y)
            p.banded = True
            g = A.ground(spans, 5, 50, y)
            pick = self._widest(p, 5, (50, 47, 44), g, 40, 33) or self._widest(p, 5, (50, 40, 32), g, 40, 12)
            if pick:
                A.charge_narrow(p, 5, pick[0], g, night, pick[1])
            g = A.ground(spans, 130, NARROW - 5, y)
            pick = self._widest(p, 142, (175,), g, 40, 10)
            if pick:
                A.defenders_narrow(p, 142, pick[0], g, night, pick[1])

    def phone_rows(self, design, title_w):
        """The rows a phone's H2 or H3 asks for under its words, always (see `PHONE_UNDER`): no phone's title leaves
        its hero the height the composition asks of it beside the words, so the great horseman or Harold stands under
        them instead."""
        return PHONE_UNDER[design]

    def scene_under(self, design, p, y0, y1, night):
        """A phone's scene in the rows its H2 or H3 asked for under its words (see `phone_rows`), from its last line
        of words at y0 down to its rule at y1."""
        self._scene_under(design, p, y1, night, top=y0)

    def _scene_under(self, design, p, rule, night, top=0):
        """The scene under a phone's words, standing as a phone's charge does on the lower border laid over its
        rule, and at the right, as the wide headers' scenes stand: on H2 the great horseman with his gonfanon raised
        and his hound running before him under the tall tree, as on a wide H2 (where the words leave him fewer rows,
        the horseman with his lance couched, his man bearing the gonfanon and a hound under the smaller tree); on H3
        the great hunt, Harold grown twice with his hawk on his fist, his great hound running before him and the tall
        tree grown to the rows under the words, no higher than row `top` (see `art.great_hunt`). Each is built to the
        rows the words leave over it. By night a torch burns in its bracket on the right hem beside them, its light
        pooled on the scene, so it stands lit as the rest of the hall."""
        A.lower_band(p, 5, NARROW - 5, rule, night, seed=rule)
        p.banded = True
        g = A.ground(A.band_spans(p, 5, NARROW - 5, rule), 5, NARROW - 5, rule)
        x1 = NARROW - 14   # the scene's right edge, three columns short of the torch on the hem by night
        if design == "H2":
            room = self._room(p, 50, x1, g, PHONE_UNDER[design], 14)
            stood = room and (A.great_horseman if room >= A.GREAT_ROOM else A.ride_narrow)(p, 5, x1, g, night, room)
        else:
            stood = A.great_hunt(p, 5, x1 + 1, g, night, top)
        if stood and night:
            A.hem_torch(p, g)

    def rule_decor(self, p, x0, x1, y, seed, night):
        """On a header (and a phone's) stats rule, the lower border of the hanging, built to the rows the words
        leave; on an element's sheet, French knots along its rule where no word lies near."""
        if getattr(p, "sheet", "") == "p":
            if not getattr(p, "banded", False):
                A.lower_band(p, x0, x1, y, night, seed=seed)
                p.banded = True
            return
        A.knots_along(p, x0, x1, y, night, seed=seed, every=(34, 60))

    def finish(self, p, night):
        """The last pass: the lower border on a phone's header that has not had it (see `phone_band`); by night an
        element's torches where they lie clear of its words and drawing, and the torches' light on what stands near
        them; and on a dial the wheel's spokes and its hand turned to a needle."""
        self.phone_band(p, night)
        self.sheet_torches(p, night)
        A.torchlight(p, night)
        if getattr(p, "dial", None):
            A.spokes(p, night, self.ink(night)["accent"])
            self._needle(p, night)

    def _finish(self, p, night):
        """The last pass (see `finish`) on every drawing, one made lighter to fit its budget too: the torches'
        light and a phone's lower border belong to the scene, and a lighter drawing thins only texture."""
        self.finish(p, night)

    def sheet_torches(self, p, night):
        """By night an element's sheet has its torches on its hems where they lie clear of its words and drawing."""
        if night and getattr(p, "sheet", "p")[:1] == "e":
            A.sheet_torches(p)

    def phone_band(self, p, night):
        """The lower border over a phone's header's rule when it has no figures to rule, and so never asked for the
        rule's decoration: its rule is the lowest row the rule's colour runs right across."""
        if getattr(p, "sheet", "") != "p" or p.w != NARROW or getattr(p, "banded", False):
            return
        rule = self.ink(night)["rule"]
        base = p.layers["base"]
        rows = [y for y in range(p.h - 1, 0, -1) if all(base.get((x, y)) == rule for x in range(4, NARROW - 4))]
        if rows:
            A.lower_band(p, 5, NARROW - 5, rows[0], night, seed=rows[0])
            p.banded = True

    def _needle(self, p, night):
        """The dial's hand as a steel needle: its point at the count, bright along its upper edge, and at the hub
        end its eye, open, with a terracotta thread through it."""
        cx, cy, r = p.dial
        reach = r - 11
        accent = self.ink(night)["accent"]
        hand = [(x, y) for (x, y), c in p.layers["base"].items() if c == accent
                and (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= reach ** 2 and y <= cy]
        if not hand:
            return
        tip = max(hand, key=lambda q: (q[0] + 0.5 - cx) ** 2 + (q[1] + 0.5 - cy) ** 2)
        shaft, point = (S_[5], S_[6]) if night else (S_[2], S_[3])
        ang = math.atan2(tip[1] + 0.5 - cy, tip[0] + 0.5 - cx)
        ux, uy, nx, ny = math.cos(ang), math.sin(ang), -math.sin(ang), math.cos(ang)
        for (x, y) in hand:
            d = ((x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2) ** 0.5
            p.px(x, y, point if d > reach - 4 else shaft)
        hole = self.ink(night)["fill"]
        for d in (4, 5, 6, 7):
            for side in (-1, 1):
                p.px(math.floor(cx + d * ux + side * nx), math.floor(cy + d * uy + side * ny), shaft)
            if d in (5, 6):
                p.px(math.floor(cx + d * ux), math.floor(cy + d * uy), hole)
        for j in range(2, 7):
            p.px(math.floor(cx + 5.5 * ux + j * nx - j * 0.4 * ux), math.floor(cy + 5.5 * uy + j * ny - j * 0.4 * uy),
                 T_[3] if j % 2 else T_[4])

    # ---- the footers and links
    def _footed(self, p, night, cell=None):
        """A finished footer's last pass, which its layouts give no hook for: its floor, the lower border of the
        hanging sewn on its hem (see `art.foot_floor`), and the comet, the design's mark, where the words leave it the
        room. On a title block it flies at the right end after the cells, over the border's beasts where they rise
        whole there, and by night, where no torch burns at the corner of the notes, a torch stands on the border
        beside it. Given `cell`, the box (x0, y0, x1, y1) by a scale bar and the sizes of comet that suit it (see
        `art.COMETS`), the comet lies there, the greatest that has the room over the floor, which rises no higher
        than braid and rule under it. By night the torches' light falls on what stands near them."""
        h = p.h
        spans = A.foot_floor(p, night, self.ink(night)["rule"], low=[cell[:3:2]] if cell else ())
        if cell:
            x0, y0, x1, y1, sizes = cell
            floor = min(h - A.FOOT_TOP[lv] for a, b, lv in spans if a < x1 and b > x0)
            spot = A.comet_spot(p, x0, x1, y0, min(y1, floor - 1), sizes)
            if spot:
                A.great_comet(p, *spot[:2], night, spot[2])
        elif spans and spans[-1][2] == 3:
            after = max((b[2] for b in p.words), default=0) + 2      # the right end, after the last of the words
            spot = A.comet_spot(p, max(after, spans[-1][0] + 4), p.w - FOOT_TORCH - 3, 5, h - 15, (0, 1, 2, 4))
            if spot:
                A.great_comet(p, *spot[:2], night, spot[2])
                if night and not p.lamps:
                    A.small_torch(p, p.w - FOOT_TORCH, h - 28, phase=1)
        if night:
            A.torchlight(p, True)
        return p

    def f1(self, ft, night):
        return self._footed(super().f1(ft, night), night)

    def f2(self, ft, night):
        """F2, the comet beside its scale bar in the bar's cell."""
        return self._footed(super().f2(ft, night), night, cell=SCALE_COMET)

    def f1_narrow(self, ft, night):
        return self._footed(super().f1_narrow(ft, night), night)

    def f2_narrow(self, ft, night):
        """A phone's F2, the comet beside its scale bar, between the bar and the way back up."""
        return self._footed(super().f2_narrow(ft, night), night, cell=PHONE_SCALE_COMET)

    def footer_mark(self, p, x, y, night):
        """A needle laid on the cloth trailing its thread at the corner of the closing notes by day; by
        night a torch in its bracket there, its light on the linen round it (see `_footed`, which lays its light on
        what stands near it once the footer is finished)."""
        if night:
            A.small_torch(p, x + 1, y - 2, phase=1)
        else:
            A.needle(p, x - 2, y - 1, False)

    def heart(self, p, x, y):
        A.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        """Blocks of terracotta and mustard wool by turns, laid on the diagonal."""
        A.wool_blocks(p, x0, y0, w, h, period)

    def link_colours(self, night):
        """A patch of linen whip-stitched in terracotta with dark letters by day; by night a patch of umber
        cloth stitched in gold with cream letters."""
        if night:
            return U_[2], G_[3], L_[6], U_[0]
        return L_[5], T_[3], U_[1], L_[3]

    def link_top(self, p, x0, x1, y, seed, night):
        """The patch's whip-stitched edge: slanting stitches of the edge's thread round the whole patch."""
        A.whip_edge(p, 0, 2, p.w, 11, night, seed)

    def link_icon(self, index, night, ink):
        return A.ICONS[LINK_SPRITES[index % len(LINK_SPRITES)]], A.icon_pal(night, ink)

    # ---- the elements
    def card_bevel(self, night):
        return (U_[4], U_[0]) if night else (L_[6], L_[3])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A card as an embroidered panel: its icon's cell in terracotta wool with the icon in cream, a braided
        seam down the cell's edge, its edge whip stitched round, and a French knot on its lid."""
        k = self.ink(night)
        A.card_panel(p, x, y, w, h, night, k["body"], k["fill"], lid)

    def wire_ink(self, night):
        """A wire is a laid thread of blue grey wool (see `wire_lights` for its couching)."""
        return W_[4] if night else W_[3]

    def wire_lights(self, p, cells, night, seed):
        """A second thread beside the laid one and the mustard couching stitches that hold the pair down."""
        A.couching(p, cells, night)

    def dashes(self, night):
        return [M_[4] if night else M_[3], O_[4] if night else O_[2]]

    def ornament(self, kind, p, x, y, night):
        """A knight on a standing horse in a free corner of the schematic."""
        if kind == "schematic":
            if p is not None:
                A.knight(p, x + 1, y + 32, night, A.REAR[0], "base", arms="none", gait="stand", face=2)
            return (36, 34)
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as a column of laid and couched work, a band of gold stitches along its top."""
        A.column(p, bx, base, bw, v, night, i=bx // 11)

    def peak_mark(self, p, x, y, night):
        A.crown(p, x, y + 1, night)

    def dial_ring(self, p, arc, night):
        """The felloe of a wheel of fortune; the drawing keeps where it is, for the spokes and the needle (see
        `finish`)."""
        A.wheel(p, arc, night)
        (x0, y0), (x1, _) = arc[0], arc[-1]
        p.dial = ((x0 + x1) / 2, y0, (x1 - x0) / 2 + 1.5)

    def dial_tick(self, p, x, y, night):
        """A knot of gold thread on the wheel's rim."""
        p.px(x, y, G_[5 if not night else 4])
        p.px(x + 1, y + 1, G_[2])

    def dial_hub(self, p, cx, cy, night):
        A.hub(p, cx, cy, night)

    def material(self, i, xx, yy, y0, y1, lift, night):
        """The wools by turns, each a block of laid work with its diagonal showing."""
        R = RAMP[(WOOLS + ("sage",))[i % 5]]
        k = -1 if night else 0
        return step(R[3 + k] if (xx + yy) % 3 == 0 else R[4 + k], lift)

    def counter_cell(self, q, ox, oy, night):
        A.patch_cell(q, ox, oy, night)

    def counter_ink(self, night, dim):
        """A numeral stitched on its patch in terracotta (mustard by night); a leading nought in a fainter
        thread."""
        if night:
            return U_[5] if dim else M_[4]
        return L_[2] if dim else T_[2]

    def timeline_line(self, p, x0, x1, y, night):
        """The couched thread the releases stand on, up to today, with a knot every so often."""
        if x1 - x0 >= 2:
            A.couched_thread(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        """A gonfanon hung from the cord for a release, one with a cross for a big one, its outline alone for one
        to come, the small tree for the repository's founding, and a knot in the cord for a patch."""
        if kind == "minor":
            A.thread_knot(p, x, gy, night)
            return
        if kind == "made":
            A.tree(p, x - 9, gy + 1, night, height=12)
            return
        A.gonfanon(p, x, gy + 2, WOOLS[i % len(WOOLS)], night, kind=kind)

    def today_mark(self, p, x, y, night):
        """The comet over the thread's end at today."""
        A.small_comet(p, x + 1, y - 5, night)

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor as a figure in profile, each in a different wool; a bot in a helm and mail."""
        A.figure(p, cx, cy, i, night, bot=not person.get("initials"))

    def commit_bar(self, p, x, y, w, fill, night):
        """A contributor's share as a band of stitches in terracotta inside a couched channel."""
        k = -1 if night else 0
        p.box(x, y, w + 2, 4, U_[1])
        for xx in range(fill):
            p.px(x + 1 + xx, y + 1, T_[4 + k] if xx % 3 else T_[3 + k])
            p.px(x + 1 + xx, y + 2, T_[3 + k] if xx % 3 else T_[2 + k])

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """A stitched roundel round the seal's disc."""
        A.roundel(p, cx, cy, r0, r1, night)

    def seal_mark(self, p, x, y, night):
        A.crown(p, x + 3, y, night, big=True)

    def placard_board(self, p, night):
        """A cloth banner hung from a rod, with a long fringe."""
        self.paper(p, night, uid="pl")
        A.banner_board(p, night)

    def placard_mark(self, p, x, y, night):
        """The border's hawk beside the placard's title."""
        A.beast(p, "hawk", x + 2, y - 3, night)

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """A badge as a cloth patch: a running stitch of cream thread just inside its edge, the cloth's
        weave showing faintly on each block clear of the letters, and a seam where the two blocks meet."""
        h = s["h"]
        ty = self._text_y(s)
        text_rows = range(ty - 1, ty + (7 if s["font"] == "57" else 5) + 1)
        mid = h // 2
        row = [p.get(x, mid) for x in range(w)]
        first = next((x for x in range(w) if row[x]), 0)
        seam = next((x for x in range(first + 1, w) if row[x] != row[first]), w)
        stitch = L_[6]

        def ins(x, y):
            return 0 <= x < w and 0 <= y < h and inside(x, y, w, h, s["corner"])
        for y in range(h):
            for x in range(w):
                if not ins(x, y):
                    continue
                if y in (0, h - 1) or not ins(x - 1, y) or not ins(x + 1, y):
                    continue
                c = p.get(x, y)
                inner = y in (1, h - 2) or not ins(x - 2, y) or not ins(x + 2, y)
                if inner:
                    if (x + y + seed) % 4 < 2 and (y not in text_rows or x not in (seam, seam - 1)):
                        p.px(x, y, stitch)
                elif y not in text_rows and (x * 3 + y) % 5 == 0:
                    try:
                        p.px(x, y, step(c, 1 if y < mid else -1))
                    except KeyError:
                        pass
        if 0 < seam < w:
            for y in range(1, h - 1):
                if ins(seam, y) and y % 2 == 0:
                    p.px(seam, y, U_[0])

    def badge_label(self):
        return (U_[1], L_[6])

    def badge_gold(self):
        return (M_[4], U_[0])

    def badge_states(self):
        return {"green": (O_[2], C["white"]), "yellow": (M_[4], U_[0]), "red": (RAMP["madder"][3], C["white"]),
                "slate": (W_[2], C["white"])}

    def badge_swatches(self):
        Sg, Md, In, Mu = (RAMP[n] for n in ("sage", "madder", "indigo", "mulberry"))
        return {"madder": (Md[3], C["white"], None), "terracotta": (T_[3], C["white"], None),
                "mustard": (M_[4], U_[0], None), "olive": (O_[2], C["white"], None),
                "sage": (Sg[2], C["white"], None), "indigo": (In[3], C["white"], None),
                "woad": (W_[3], C["white"], None), "mulberry": (Mu[3], C["white"], None),
                "linen": (L_[6], U_[1], "weave"), "umber": (U_[1], L_[6], None), "walnut": (U_[3], L_[6], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        if pattern == "weave" and (x + y) % 4 == 0 and y not in text_rows:
            return L_[4]
        return c

    def badge_outline(self, pattern):
        return L_[3] if pattern == "weave" else None

    def badge_shine(self, c, y, h):
        try:
            return step(c, 1) if y == 2 else step(c, -1) if y == h - 1 else c
        except KeyError:
            return c

    def plate_colours(self, mode):
        """A plate is a linen patch with its weave showing, the value on a block of terracotta wool, framed
        by a whip stitch; by night the linen is umber and the block mustard; a live plate is mustard wool."""
        if mode == "day":
            return dict(paper=L_[5], dot=L_[3], frame=T_[3], block=T_[2], ink=U_[1], letters=L_[6])
        if mode == "night":
            return dict(paper=U_[2], dot=U_[3], frame=G_[3], block=M_[4], ink=L_[5], letters=U_[0])
        return dict(paper=M_[4], dot=M_[3], frame=U_[1], edge=M_[2], ink=U_[0])

    def plate_edge(self, block):
        return step(block, -1)


SET = Tapestry()
