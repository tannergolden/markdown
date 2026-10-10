# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Valentine's Day set: a love letter of a sheet.

Titles are candy-apple lacquer ringed in wine by day and a pink neon sign by
night; a red satin ribbon stitched with white hearts frames every sheet and
heart bunting swags across the top. The headers stand on a table laid for the
day, a lace runner with red roses, chocolates, candles, a teddy bear, a present
with heart balloons riding the air and Cupid on a cloud; on the quay in Paris,
the Eiffel Tower over the roofs and love locks on the railing, with Cupid on the
wing; or where Cupid looses an arrow into a heart hung from the bunting. Rose
petals lie along every rule. By day the paper is blush white; by night a plum
sky, and sky lanterns rise into it.
"""
from __future__ import annotations

from ..designs import NARROW, Holiday
from ..designs.badges import inside
from ..pixel import Paint, Pix
from . import art as A
from .palette import C, NIGHT_SKY, RAMP, TOKENS, X, step

# The title's lacquer by day and its neon by night: a band of colour for each row of the face.
FOIL = Paint("foil", A.foil_fill)
LINK_SPRITES = ("heart", "letter", "rose", "gift")
# The colours the petals along a badge's top come in, by turns.
PETAL_TRIM = ("blush", "lace", "gold", "rose", "blush", "lilac")


def clear(p: Pix, x0, y0, x1, y1) -> bool:
    """Whether a sprite in the box from (x0, y0) to (x1, y1) stands clear of every word, with a unit or a
    few to spare and, to its right, room for the block a numbered note's number sits on before its words."""
    return p.clear_of_words(x0 - 3, y0 - 1, x1 + 12, y1 + 1)


class ValentinesDay(Holiday):
    key = "valentines-day"
    name = "Valentine's Day"
    tokens = frozenset(TOKENS)

    # ---- colour and paper
    def ink(self, night):
        """The set's colours. A title's letters are painted (see `title_text`); `title` is the lacquer's
        deepest band by day and the neon's dimmest by night."""
        return dict(
            title=RAMP["blush"][4] if night else RAMP["rose"][2], shadow=RAMP["rose"][2] if night else RAMP["rose"][1],
            body=X["body_night"] if night else C["ink"], muted=X["muted_night"] if night else X["muted_day"],
            rule=X["night_rule"] if night else X["rule_day"], accent=RAMP["blush"][5] if night else RAMP["rose"][3],
            tag=RAMP["rose"][3], tag_ink=C["white"],
            fill=X["node_night"] if night else C["white"], dim=X["dim_night"] if night else X["dim_day"],
        )

    def lit(self, night):
        """By day candy-apple lacquer with a wine edge round every letter and a pink shadow under it; by night
        a pink neon sign, its glow spreading two pixels round every letter."""
        if night:
            return dict(glow=(RAMP["blush"][4], (0.12, 0.22)), night=True)
        return dict(outline=RAMP["rose"][0], shadow=RAMP["blush"][5], night=False)

    def paper(self, p, night, uid="p"):
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        if not night:
            return C["paper"]
        return NIGHT_SKY[min(len(NIGHT_SKY) - 1, int(y * len(NIGHT_SKY) / p.h))]

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        A.stars(p, x0, y0, x1, y1, n, seed=seed, twinkling=twinkling, faint=faint, avoid=avoid)

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The paper, or by night the plum sky with a star for every twelve units of its width (half as many
        on a drawing made lighter to fit its budget)."""
        self.paper(p, night)
        if night:
            self.stars(p, 6, 16, p.w - 6, int(y1 * 0.7), n=p.w // (24 if p.lite else 12), seed=seed,
                       twinkling=motion, avoid=avoid)

    def frame(self, p, night, webs=False):
        A.ribbon_frame(p, night)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """Heart bunting swagged from tack to tack just under the ribbon: forty units a swag, sagging four, on
        a wide sheet; thirty-four, sagging three, on a phone's."""
        wide = x1 - x0 > NARROW
        A.bunting(p, x0, x1, y - 1, span=40 if wide else 34, sag=4 if wide else 3, night=night)

    def tag(self, p, x, y, w, h, night):
        """The red block a tag's white letters sit on: lit along its top, shaded along its foot."""
        R = RAMP["rose"]
        p.rect(x, y, w, h, R[3])
        p.hline(x, x + w, y, R[4])
        p.hline(x, x + w, y + h - 1, R[2])

    def title_text(self, p, x, y, s, night, scale):
        """Lacquered letters lit by the theme (see `lit`), and here and there a glint where the light catches
        them. A drawing made lighter keeps the letters and the edge they read by, and leaves out the glints
        and the shadow."""
        k = self.ink(night)
        lit = self.lit(night)
        if p.lite:
            lit.pop("shadow", None)
        w = p.text(x, y, s, k["title"], "57", scale, paint=FOIL, **lit)
        if not p.lite:
            A.glints(p, x, y, s, scale)
        return w

    # ---- the headers' scenes
    def section_mark(self, p, x, y, night):
        A.tiny_heart(p, x - 1, y + 1, "blush" if night else "rose", night)

    def strip_mark(self, p, x, y, night):
        """A stuffed heart beside the strip's title, and a glint beside it."""
        A.puffy_heart(p, x - 2, y - 4, 7, "rose", night)
        A.sparkle(p, x + 9, y - 5, L=p.twinkle(2))

    def scene(self, design, p, rule, night, motion):
        """H1 stands on the table laid for the day, H2 on the quay in Paris and H3 on Cupid's archery. By night
        in a moving file the hearts stitched along the ribbon's top and foot light up in turn."""
        if night and motion:
            A.heart_chase(p)
        if design == "H1":
            return self._table(p, rule, night, motion)
        if design == "H2":
            return self._quay(p, rule, night, motion)
        return self._archery(p, rule, night, motion)

    def _table(self, p, rule, night, motion):
        """A lace runner at each end of the foot. On the left Cupid perched on a cloud over a vase of red roses,
        a box of chocolates standing open and two candles; on the right heart balloons riding the air, tied
        to a present, a teddy bear holding a heart and a love letter. Petals fall from the roses, hearts rise
        from the present, and by night sky lanterns are let go into the dark."""
        A.lace_runner(p, 5, 62, rule - 3, rule, seed=2, night=night)
        A.lace_runner(p, 352, 410, rule - 3, rule, seed=6, night=night)
        if p.clear_of_words(4, 15, 38, 40):
            A.perched_cupid(p, 8, 17, night, motion)
        A.vase_of_roses(p, 14, rule - 1, night)
        A.chocolate_box(p, 24, rule - 1, night)
        A.candle(p, 48, rule, 12, night, motion=motion, phase=0)
        A.candle(p, 54, rule, 7, night, motion=motion, phase=1, fam="blush")
        rides = A.bobbing(p, motion, "bob0", (0, 0, 1, 2, 2, 1), 3.2)
        rides2 = A.bobbing(p, motion, "bob1", (0, 1, 2, 2, 1, 0), 3.8)
        for (bx, by, fam, w, L) in ((377, rule - 50, "blush", 9, rides2), (401, rule - 52, "gold", 9, rides2),
                                    (389, rule - 60, "rose", 11, rides)):
            kx, ky = A.heart_balloon(p, bx, by, fam, night, L=L, string=0, w=w)
            A.tether(p, kx, ky, 389, rule - 13, night, L=L)
        A.gift_box(p, 383, rule - 1, 12, 9, "blush", "rose", night)
        A.teddy(p, 368, rule - 1, night)
        A.love_letter(p, 398, rule - 8, night)
        for (sx, sr) in ((14, 5), (34, 9), (49, 2), (55, 2), (368, 7), (389, 7), (403, 6)):
            A.contact(p, sx, rule - 1, sr)
        A.falling_petals(p, [(36, 22, rule - 1, 6, 7.4, 0.0, 11), (44, 30, rule - 1, -8, 8.6, 0.5, 12)], night, motion)
        A.rising_hearts(p, [(362, rule - 22, 12, -6, 6.8, 0.0, 3)], night, motion)
        if night:
            lanterns = [(50, rule - 36, 8, -2, 15.0, 0.1), (399, rule - 70, 6, -4, 13.0, 0.6)]
            A.sky_lanterns(p, [s for s in lanterns if p.clear_of_words(s[0] - 3, s[1] - 3, s[0] + 9, s[1] + 11)],
                           motion)
        return [(5, 62), (352, 410)]

    def _quay(self, p, rule, night, motion):
        """Paris from the quay: the Eiffel Tower over the roofs, the parapet's railing hung with love locks and
        a lamp at each end, and Cupid on the wing across the sky. By day the winter sun is low and a cloud has
        taken the shape of a heart; by night a crescent moon is up, the tower is lit gold and sparkles on the
        hour, the windows and the lamps are lit and a lantern rises."""
        if night:
            A.moon(p, 318, 26, 6)
        else:
            A.sun(p, 318, 26, 5)
            A.cloud(p, 330, 30, 22)
            if p.clear_of_words(284, 15, 302, 31):
                A.cloud(p, 286, 17, 13, heart=True)
        A.eiffel(p, 372, rule - 9, 64, night, motion=motion)
        A.paris(p, 312, 410, rule - 9, night, seed=3, lo=8, hi=14, sun_x=318)
        A.quay(p, 296, 410, rule, night, h=4, rail=6)
        A.lamp_post(p, 298, rule - 4, 20, night, phase=0)
        A.lamp_post(p, 402, rule - 4, 20, night, phase=1)
        A.cupid_flies(p, A.wavy(386, 12, 262, 30, 34, 3, 1.5) + [(-40, -40)] * 8, night, motion, dur=10.0)
        if night:
            A.sky_lanterns(p, [(344, rule - 26, 10, -8, 14.0, 0.3)], motion)
        return [(294, 410)]

    def _archery(self, p, rule, night, motion):
        """Cupid on a cloud drawing his bow on a heart hung from the bunting: he looses, the arrow flies, the
        heart takes it and beats, and little hearts fly out of it; held still, his arrow is through the heart.
        By day a conversation heart lies on the runner, by night a candle burns there."""
        A.lace_runner(p, 352, 410, rule - 3, rule, seed=4, night=night)
        cy = rule - 33
        cloud_y = cy + 17
        if not night:
            A.cloud(p, 351, cloud_y, 20, 6, L="base")
        else:
            for (dx, dy) in ((0, 1), (3, 0), (8, 0), (13, 0), (17, 1)):
                p.px(353 + dx, cloud_y + 2 + dy, RAMP["wine"][5])
            p.hline(354, 370, cloud_y + 3, RAMP["wine"][4])
        hx, hw = 392, 13
        hy = cy + 4                                          # the heart hangs square on the arrow's line
        for yy in range(8, hy):
            p.px(hx + hw // 2, yy, RAMP["rose"][3] if night else RAMP["rose"][4])
        A.puffy_heart(p, hx, hy, hw, "rose", night)
        ay = cy + 10
        if motion:
            dur = 6.0
            A.cupid(p, 352, cy, "aim", night, L=p.seq("cpa", 0.0, 0.5, dur, z=1))
            A.cupid(p, 352, cy, "loosed", night, L=p.seq("cpl", 0.5, 1.0, dur, keep=True, z=1))
            key = ("arrow", night)
            if key not in p.syms:
                q = Pix(40, 8)
                A.arrow_cells(q, 0, 3, 7, night)
                p.symbol(key, A.cells_of(q))
            for i, ax in enumerate((372, 379, 385)):
                p.use(key, ax, ay - 3, p.seq(f"arw{i}", 0.5 + i * 0.04, 0.54 + i * 0.04, dur, z=2))
            hit = p.seq("hit", 0.62, 1.0, dur, keep=True, z=2)
            A.puffy_heart(p, hx - 1, hy - 1, hw + 2, "rose", night, L=p.seq("beat", 0.62, 0.72, dur, z=2.2))
            for i, (t0, t1, r) in enumerate(((0.64, 0.76, 3), (0.72, 0.86, 7))):
                burst = p.seq(f"burst{i}", t0, t1, dur, z=2.4)
                for (dx, dy) in ((-2, -3), (hw + 1, -2), (hw + 2, 5), (-3, 4)):
                    sx = hx + dx + (-r // 2 if dx < 0 else r // 2)
                    A.tiny_heart(p, sx, hy + dy - r // 3, "blush" if i else "rose", night, L=burst)
        else:
            hit = "base"
            A.cupid(p, 352, cy, "loosed", night)
        q = Pix(40, 8)                                       # the arrow, through the heart and out the far side
        A.arrow_cells(q, 0, 3, 21, night)
        for (ax, ay_), col in A.cells_of(q).items():
            gx, gy = hx - 9 + ax, ay - 3 + ay_
            if not hx + 2 <= gx <= hx + hw - 3:
                p.px(gx, gy, col, hit)
        if night:
            A.candle(p, 402, rule, 6, night, motion=motion, phase=2, fam="blush")
        else:
            A.candy_heart(p, 378, 0, "XO", "lilac", night, foot=rule - 3)
        return [(352, 410)]

    def scene_narrow(self, design, p, y, night):
        """On a phone: H1 stands on the table laid for the day, each thing on it only where it stands clear of
        the words; H2 has the low sun, or the moon, beside SECTION A-A; H3 a stuffed heart and a glint beside
        the title."""
        if design == "H1":
            self._table_narrow(p, y, night)
        elif design == "H2":
            if p.clear_of_words(NARROW - 22, y - 3, NARROW - 11, y + 9):
                if night:
                    A.moon(p, NARROW - 17, y + 3, 4)
                else:
                    A.sun(p, NARROW - 17, y + 3, 3)
        else:
            A.puffy_heart(p, 152, y - 17, 7, "rose", night)
            A.sparkle(p, 164, y - 19, L="near")

    def _table_narrow(self, p, ry, night):
        """The table on a phone, on row `ry`: a runner at each end, the roses, the chocolates and two candles on
        the left, the teddy bear, the present, its balloons and a love letter on the right."""
        A.lace_runner(p, 5, 60, ry - 3, ry, seed=7, night=night)
        A.lace_runner(p, 118, NARROW - 5, ry - 3, ry, seed=9, night=night)
        stood = []
        if clear(p, 5, ry - 30, 24, ry):
            A.vase_of_roses(p, 14, ry - 1, night)
            stood.append((14, 5))
        if clear(p, 24, ry - 24, 45, ry):
            A.chocolate_box(p, 24, ry - 1, night)
            stood.append((34, 9))
        if clear(p, 47, ry - 14, 58, ry):
            A.candle(p, 48, ry, 9, night, motion=False, phase=0)
            A.candle(p, 54, ry, 6, night, motion=False, phase=1, fam="blush")
            stood += [(49, 2), (55, 2)]
        if clear(p, 123, ry - 19, 138, ry):
            A.teddy(p, 130, ry - 1, night)
            stood.append((130, 7))
        if clear(p, 143, ry - 13, NARROW - 4, ry):
            A.gift_box(p, 144, ry - 1, 12, 9, "blush", "rose", night)
            A.love_letter(p, 160, ry - 8, night, w=11)
            stood += [(150, 7), (165, 6)]
            if clear(p, 140, ry - 39, 166, ry - 13):
                for (bx, by, fam, w) in ((146, ry - 38, "rose", 11), (160, ry - 32, "gold", 9)):
                    kx, ky = A.heart_balloon(p, bx, by, fam, night, string=0, w=w)
                    A.tether(p, kx, ky, 150, ry - 13, night)
        for (sx, sr) in stood:
            A.contact(p, sx, ry - 1, sr)

    def rule_decor(self, p, x0, x1, y, seed, night):
        A.petals_on(p, x0, x1, y, seed=seed, night=night)

    def finish(self, p, night):
        A.lamplight(p, night)

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        """A long-stemmed rose and a little heart in the corner of the notes: at the cell's foot on a wide sheet,
        at its top on a phone's."""
        if p.w > NARROW:
            A.a_rose(p, x - 2, y + 9, night)
            A.tiny_heart(p, x + 6, y + 4, "blush", night)
        else:
            A.a_rose(p, x + 4, y - 4, night)
            A.tiny_heart(p, x + 12, y - 4, "blush", night)

    def heart(self, p, x, y):
        A.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        """A bar striped like a length of candy ribbon, red and white."""
        A.candy_ribbon(p, x0, y0, w, h, period)

    def link_colours(self, night):
        if night:
            return X["node_night"], X["night_rule"], X["body_night"], RAMP["wine"][2]
        return C["white"], X["rule_day"], C["ink"], X["dim_day"]

    def link_top(self, p, x0, x1, y, seed, night):
        """A strip of red satin ribbon along the button's top edge, a seed pearl sewn on every four pixels."""
        A.satin_trim(p, x0 - 1, x1 + 1, y, seed, night)

    def link_icon(self, index, night, ink):
        return A.icon(LINK_SPRITES[index % len(LINK_SPRITES)], night)

    # ---- the elements
    def card_bevel(self, night):
        return (RAMP["wine"][3], RAMP["wine"][0]) if night else (C["white"], X["dim_day"])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A strip of red satin ribbon down the icon cell's edge with a heart stitched into it, a stuffed heart
        on the lid, and petals along the lid beside it."""
        R = RAMP["rose"]
        k = -1 if night else 0
        for yy in range(y + 1, y + h - 1):
            for i, t in enumerate((4, 3, 2)):
                p.px(x + 10 + i, yy, R[t + k])
        hy = y + h // 2 - 1
        for (a, b) in A.STITCH:
            p.px(x + 10 + a, hy + b, RAMP["blush"][5] if night else C["white"])
        if lid:
            A.puffy_heart(p, x + 7, y - 5, 5, "rose", night)
        A.petals_on(p, x + (15 if lid else 3), x + w - 2, y, seed=x + y, night=night, gap=(5, 14))

    def wire_ink(self, night):
        return RAMP["lace"][4] if night else self.ink(night)["body"]

    def wire_lights(self, p, cells, night, seed):
        """Petals caught along a wire where it runs level, every fifth pixel, over it and under it by turns."""
        run = sorted((x, y) for (x, y, d) in cells[4:-6] if d == "h")
        for i, (x, y) in enumerate(run[::5]):
            R = RAMP[("rose", "blush", "rose")[(i + seed) % 3]]
            p.px(x, y - 1 if i % 2 else y + 1, R[(5 if i % 3 != 1 else 3) - (1 if night else 0)])

    def dashes(self, night):
        return [RAMP["blush"][5], X["muted_night"]] if night else [RAMP["rose"][3], RAMP["blush"][4]]

    def ornament(self, kind, p, x, y, night):
        """In a free corner of the schematic, a box of chocolates standing open and a teddy bear holding a
        heart."""
        if kind != "schematic":
            return (0, 0)
        if p is not None:
            A.chocolate_box(p, x, y + 23, night)
            A.teddy(p, x + 36, y + 23, night)
        return (44, 23)

    def hist_bar(self, p, bx, base, bw, v, night):
        A.ribbon_bar(p, bx, base, bw, v, night, self.wire_ink(night))

    def peak_mark(self, p, x, y, night):
        """A stuffed heart beside the busiest week's count, where it stands clear of every word."""
        if p.clear_of_words(x - 1, y - 3, x + 8, y + 5):
            A.puffy_heart(p, x, y - 2, 7, "rose", night)

    def dial_ring(self, p, arc, night):
        """The upper half of a clock's face, eight units deep along the ring, its hours for the dial's ticks."""
        (x0, cy), (x1, _) = arc[0], arc[-1]
        r = (x1 - x0) / 2
        A.clock_ring(p, round((x0 + x1) / 2), round(cy), r - 3.5, r + 4.5, night)

    def dial_tick(self, p, x, y, night):
        """None: the clock's face has its own hours."""

    def dial_hub(self, p, cx, cy, night):
        A.boss(p, cx, cy)

    def material(self, i, xx, yy, y0, y1, lift, night):
        """The cloths of a sweetheart's dress by turns: red satin, pink lace, chocolate velvet and cream silk."""
        return A.cloth(i, xx, yy, y0, lift)

    def counter_cell(self, q, ox, oy, night):
        A.flip_tile(q, ox, oy)

    def counter_ink(self, night, dim):
        """A flip clock's digit, bright on its plum tile; a leading nought dim."""
        return RAMP["wine"][5] if dim else RAMP["blush"][6]

    def timeline_line(self, p, x0, x1, y, night):
        A.twine(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        A.charm(p, x, gy, kind, night, i, ink=self.ink(night)["muted"])

    def today_mark(self, p, x, y, night):
        """A warm glint at today's end of the twine."""
        A.sparkle(p, x + 2, y, big=True, warm=True)

    def avatar(self, p, cx, cy, i, person, night):
        A.sweetheart(p, cx, cy, i, str(person.get("initials") or "")[:2], night)

    def commit_bar(self, p, x, y, w, fill, night):
        A.candy_share(p, x, y, w, fill, self.wire_ink(night))

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """A paper lace doily behind the seal's disc, its scallops standing a few pixels out from it."""
        A.doily(p, cx, cy, r0 + 2, night)

    def placard_board(self, p, night):
        """A valentine: the paper inside a red satin ribbon, heart bunting swagged along its top, drawn in
        pixels so that the owner's tag, however long, stands in front of it."""
        A.paper(p, night, 3, 5, p.w - 6, p.h - 8, uid="pl")
        if night:
            A.stars(p, 8, 10, p.w - 8, p.h - 32, 24, seed=9, twinkling=False, faint=True)
        A.ribbon_frame(p, night, 0, 2, p.w, p.h - 4, uid="plq")
        A.bunting(p, 90, 170, 5, 40, 3, night, reuse=False)

    def placard(self, d, night):
        """The shared card, and at its foot the stuffed heart a valentine is signed with, where no word is."""
        p = super().placard(d, night)
        if p.clear_of_words(182, 58, 193, 68):
            A.puffy_heart(p, 184, 60, 7, "rose", night)
        return p

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """Rose petals lying along the badge's top two rows, kept inside its shape: curls and flat petals,
        pink, white, gold, red and lilac by turns, some face up and some turned, a pixel or two apart."""
        x, i = 1 + seed % 2, 0
        while x < w - 2:
            R = RAMP[PETAL_TRIM[(i + seed) % len(PETAL_TRIM)]]
            lit, dark = (R[6], R[4]) if R is RAMP["lace"] else (R[5], R[3])
            shape = (((0, 0, lit), (1, 0, dark)), ((0, 1, lit), (1, 1, lit)), ((0, 0, dark), (0, 1, lit)))[i % 3]
            for (dx, dy, c) in shape:
                if inside(x + dx, dy, w, s["h"], s["corner"]):
                    p.px(x + dx, dy, c)
            x += 3 + (1 if (i * 7 + seed) % 3 == 0 else 0)
            i += 1

    def badge_label(self):
        return (RAMP["wine"][3], C["white"])

    def badge_gold(self):
        """A live badge's label: the set's blush pink, with dark letters."""
        return (RAMP["blush"][5], C["coal"])

    def badge_states(self):
        # Green is leaf green, red is rose and yellow is gold with dark letters, so each reads at 4.5:1 and
        # none is the pink of the label.
        return {"green": (RAMP["leaf"][2], C["white"]), "yellow": (RAMP["gold"][4], C["coal"]),
                "red": (RAMP["rose"][3], C["white"]), "slate": (C["slate"], C["white"])}

    def badge_swatches(self):
        R, B, G = RAMP["rose"], RAMP["blush"], RAMP["gold"]
        return {"rose": (R[3], C["white"], None), "blush": (B[5], C["ink"], None),
                "lace": (RAMP["lace"][5], C["ink"], "outline"), "cocoa": (RAMP["cocoa"][3], C["white"], None),
                "sprinkles": (B[2], C["white"], "sprinkles"), "starlight": (RAMP["wine"][1], C["white"], "stars"),
                "gold": (G[4], C["coal"], None), "amber": (G[3], C["coal"], None),
                "leaf": (RAMP["leaf"][3], C["white"], None), "lilac": (RAMP["lilac"][3], C["white"], None),
                "silver": (RAMP["silver"][2], C["white"], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        """Sprinkles of pink, white and red, or a night's stars, scattered on the block clear of its letters."""
        if y in text_rows:
            return c
        if pattern == "sprinkles" and (x * 5 + y * 11) % 13 == 0:
            return (RAMP["blush"][5], C["white"], RAMP["rose"][5])[(x + y) % 3]
        if pattern == "stars" and (x * 7 + y * 13) % 23 == 0:
            return C["white"] if (x + y) % 2 else RAMP["blush"][6]
        return c

    def badge_outline(self, pattern):
        return RAMP["rose"][3] if pattern == "outline" else None

    def badge_shine(self, c, y, h):
        """Plastic's gloss: the petals light its top, and its foot is shaded a step."""
        if y != h - 1:
            return c
        try:
            return step(c, -1)
        except KeyError:
            return c

    def plate_colours(self, mode):
        R, B, W = RAMP["rose"], RAMP["blush"], RAMP["wine"]
        if mode == "day":
            return dict(paper=C["paper"], dot=C["grid"], frame=R[3], block=R[3], ink=C["ink"], letters=C["white"])
        if mode == "night":
            return dict(paper=W[1], dot=C["grid_n"], frame=B[5], block=B[5], ink=X["body_night"], letters=C["ink"])
        return dict(paper=B[5], dot=B[4], frame=C["coal"], edge=B[3], ink=C["coal"])

    def plate_edge(self, block):
        return step(block, -1)


SET = ValentinesDay()
