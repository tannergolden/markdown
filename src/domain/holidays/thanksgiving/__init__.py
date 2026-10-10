# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Thanksgiving set: a harvest sheet at the turn of the leaves.

Titles are lettered in the turn of the leaves, gold at the crown of each
letter through squash to cranberry at its foot, with a leaf come to rest on a
few of them. Woven wicker frames every sheet, a garland of maple leaves on
twine hangs across the top, and fallen leaves lie along every rule. Headers
stand on the ground at harvest time: a red barn far off on a harvested hill,
a shock of corn and pumpkins, a horn of plenty, a tree in full colour, a
turkey, a pie steaming on a bale of hay by a candle and a scarecrow, with
leaves coming down and geese flying south. By day the paper is linen; by
night an evening sky with the harvest moon up.
"""
from __future__ import annotations

import math
import random

from ..designs import NARROW, Holiday
from ..designs.badges import inside
from ..pixel import FONTS, LX, LZ, clip, fold, measure, sphere
from . import art as A
from .palette import C, NIGHT_SKY, RAMP, TOKENS, X, step

# The leaf a link button starts with, turning colour down the row.
LINK_LEAVES = ("cranberry", "squash", "wheat", "bark")
# The rule under an element sheet's title, where the fallen leaves lie further apart than on a header's.
SHEET_RULE = 20
# The badges' trim: little leaves along the top two rows, red, orange, gold and brown by turns.
TRIM = ("cranberry", "squash", "wheat", "bark", "squash", "cranberry")
# The cornucopia a schematic keeps in a free corner: how much room it takes, and how far its foot is below its top.
HORN, HORN_FOOT = (49, 27), 28


class Thanksgiving(Holiday):
    key = "thanksgiving"
    name = "Thanksgiving"
    tokens = frozenset(TOKENS)

    # ---- colour and paper
    def ink(self, night):
        """The set's colours. `title` stands for the painted letters (by day their dark edge); `shadow` is
        the shade under a check mark."""
        return dict(
            title=X["maple_night"] if night else RAMP["bark"][2], shadow=RAMP["squash"][2] if night else RAMP["squash"][1],
            body=X["body_night"] if night else C["ink"], muted=X["muted_night"] if night else X["muted_day"],
            rule=X["night_rule"] if night else X["rule_day"], accent=X["accent_night"] if night else X["accent_day"],
            tag=RAMP["cranberry"][3], tag_ink=RAMP["linen"][6],
            fill=X["node_night"] if night else C["white"], dim=X["dim_night"] if night else X["dim_day"],
        )

    def lit(self, night):
        """The turn of the leaves painted over the letters, a tone or two lighter by night. (By day
        `title_text` sets a dark edge round them and a pale shadow under them.)"""
        return dict(paint=A.AUTUMN, night=night)

    def paper(self, p, night, uid="p"):
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        if not night:
            return C["paper"]
        return NIGHT_SKY[min(len(NIGHT_SKY) - 1, int(y * len(NIGHT_SKY) / p.h))]

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        A.stars(p, x0, y0, x1, y1, n, seed=seed, twinkling=twinkling, faint=faint, avoid=avoid)

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The paper, or by night the evening sky with a star every twelve units across (half as many on a
        drawing made lighter). A wide header's still file has the same stars as its moving one, held still."""
        self.paper(p, night)
        if night:
            self.stars(p, 6, 16, p.w - 6, int(y1 * 0.7), n=p.w // (24 if p.lite else 12), seed=seed,
                       twinkling=motion or p.w > NARROW, avoid=avoid)

    def frame(self, p, night, webs=False):
        A.wicker_frame(p, night)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """Maple leaves on twine: a span of 45 sagging 4 on a wide sheet, 34 sagging 3 on a phone."""
        wide = p.w > NARROW
        A.garland(p, x0, x1, y, 45 if wide else 34, 4 if wide else 3, night)

    def tag(self, p, x, y, w, h, night):
        """The cranberry block a tag's cream letters sit on: lit along its top, shaded along its foot."""
        R = RAMP["cranberry"]
        p.rect(x, y, w, h, R[3])
        p.hline(x, x + w, y, R[4])
        p.hline(x, x + w, y + h - 1, R[2])

    def title_text(self, p, x, y, s, night, scale):
        """Letters in the turn of the leaves: by day each on a pale shadow inside a dark brown edge, by night
        bare, the warm colours reading on the sky. A small leaf has come to rest on top of every third
        letter whose top row is inked (not on a drawing made lighter)."""
        k = self.ink(night)
        s = fold(s, "57")
        glyphs, _, space = FONTS["57"]
        spots, cx = [], x                   # (index, letter, x) of every letter, as the face sets them
        for i, ch in enumerate(s):
            if ch == " ":
                cx += (space + 1) * scale
                continue
            spots.append((i, ch, cx))
            cx += (glyphs[ch][0] + 1) * scale
        if not night:
            for _, ch, gx in spots:
                p.use(A.title_edge(p, ch, scale, RAMP["linen"][3], RAMP["bark"][1]), gx, y, scale=scale)
        w = p.text(x, y, s, k["title"], "57", scale, **self.lit(night))
        if p.lite:
            return w
        fams = ("squash", "cranberry", "wheat")
        for i, ch, gx in spots:
            top = sorted(glyphs[ch][1][0])
            if i % 3 == 1 and top:
                A.leaf(p, gx + top[len(top) // 2] * scale - 1, y - 2, fams[(i // 3) % 3], night, "tiny", L="near",
                       flip=i % 2 == 0)
        return w

    # ---- the headers' scenes
    @staticmethod
    def _clear(p, x0, y0, x1, y1, m=2):
        """Whether the box from (x0, y0) to (x1, y1), and `m` more all round, touches no word."""
        return p.clear_of_words(x0 - m, y0 - m, x1 + m, y1 + m)

    def section_mark(self, p, x, y, night):
        """A cranberry maple leaf after SECTION A-A, a pixel nearer the words on a wide sheet."""
        A.leaf(p, x - (1 if p.w > NARROW else 0), y - 1, "cranberry", night, "maple7", reuse=False)

    def strip_mark(self, p, x, y, night):
        """A squash maple leaf beside an H3's title, and an acorn under its tip."""
        A.leaf(p, x + 1, y - 4, "squash", night, "maple9", reuse=False)
        A.acorn(p, x + 12, y + 4, night)

    def _moon(self, p, cx, cy, r, night):
        """The harvest moon, by night only, where no word stands in its way."""
        if night and self._clear(p, cx - r - 1, cy - r - 1, cx + r + 2, cy + r + 2):
            A.harvest_moon(p, cx, cy, r)

    @staticmethod
    def _falls(p, specs, night, motion):
        """Leaves falling across a header: each (x, y, ground, drift, seconds, phase), a colour each in turn."""
        fams = ("squash", "cranberry", "squash", "wheat", "cranberry")
        A.falling_leaves(p, [(x, y, gy, fams[i % len(fams)], drift, dur, ph)
                             for i, (x, y, gy, drift, dur, ph) in enumerate(specs)], night, motion)

    def scene(self, design, p, rule, night, motion):
        """What stands on the ground is set from the rule; what is in the sky (the moon, the geese, where the
        leaves start to fall) from the top, as the sample drew it, but H2's moon, which rises behind the tree."""
        if design == "H1":
            self._moon(p, 82, 36, 10, night)
            A.treeline(p, 5, 60, rule - 2, 14, night, seed=2, taper=(False, True))
            A.ground(p, 5, 58, rule - 3, rule, seed=2, night=night)
            A.field_hill(p, 5, 44, rule - 13, rule - 2, night)
            A.barn(p, 9, rule - 11, night)
            A.corn_shock(p, 46, rule - 1, 34, night, seed=2)
            A.pumpkin(p, 17, rule - 1, 7, night=night)
            A.pumpkin(p, 29, rule - 1, 4.5, night=night, fam="linen")
            A.gourd(p, 34, rule - 1, "stripe", night)
            A.treeline(p, 352, 410, rule - 2, 14, night, seed=6, taper=(True, False))
            A.ground(p, 356, 410, rule - 3, rule, seed=6, night=night)
            A.cornucopia(p, 360, rule - 1, night)
            for (sx_, sr_) in ((17, 8), (29, 5), (37, 3), (46, 10), (374, 16), (393, 6), (402, 4)):
                A.contact(p, sx_, rule - 1, sr_)
            A.geese(p, (430, 66), (378, 36), (318, -30), night, motion, dur=15.0)
            self._falls(p, [(52, 16, rule - 1, -22, 7.0, 0.0), (368, 16, rule - 1, 18, 8.2, 0.4),
                            (392, 24, rule - 1, 6, 6.4, 0.7)], night, motion)
            return [(5, 58), (356, 410)]
        if design == "H2":
            self._moon(p, 348, max(42, rule - 75), 14, night)
            A.treeline(p, 290, 374, rule - 2, 14, night, seed=3, taper=(True, True))
            crown = A.autumn_tree(p, 391, rule - 1, 62, night, seed=4, clip=(5, p.w - 5))
            A.ground(p, 294, 410, rule - 3, rule, seed=3, night=night)
            A.field_hill(p, 294, 334, rule - 12, rule - 2, night)
            A.barn(p, 300, rule - 10, night)
            A.pumpkin(p, 303, rule - 1, 7, night=night)
            A.pumpkin(p, 316, rule - 1, 4.5, night=night, fam="linen")
            A.turkey(p, 334, rule - 1, night)
            A.hay_bale(p, 352, rule - 1, 19, 9, night)
            A.pie(p, 353, rule - 10, night, w=16)
            A.candle(p, 378, rule - 1, 10, night, phase=0, motion=motion)
            A.gourd(p, 398, rule - 1, "pear", night)
            A.steam(p, 357, rule - 18, night, motion, phase=0)
            for (sx_, sr_) in ((303, 8), (316, 5), (334, 9), (361, 11), (378, 3), (391, 5), (401, 3)):
                A.contact(p, sx_, rule - 1, sr_)
            if night:
                A.light_pool(p, 378, rule - 2, 10, 2.5, night)
            cx, cy = crown["cx"], crown["cy"]
            A.geese(p, (430, 58), (376, 30), (300, -30), night, motion, dur=15.0)
            self._falls(p, [(cx - 14, cy - 4, rule - 1, -22, 7.4, 0.0), (cx + 4, cy + 2, rule - 1, -30, 8.6, 0.35),
                            (cx - 24, cy + 8, rule - 1, -18, 6.6, 0.7)], night, motion)
            return [(294, 410)]
        self._moon(p, 330, 30, 9, night)
        A.ground(p, 352, 410, rule - 3, rule, seed=4, night=night)
        A.turkey(p, 361, rule - 1, night, s=0.62)
        A.scarecrow(p, 382, rule - 1, night)
        A.pumpkin(p, 397, rule - 1, 5.5, night=night)
        A.pumpkin(p, 406, rule - 1, 3.5, night=night, fam="linen")
        for (sx_, sr_) in ((361, 6), (382, 3), (397, 7), (406, 4)):
            A.contact(p, sx_, rule - 1, sr_)
        A.geese(p, (430, 50), (372, 24), (250, -30), night, motion, dur=17.0)
        self._falls(p, [(368, 14, rule - 1, -12, 6.8, 0.2), (300, 16, 44, 14, 6.0, 0.6)], night, motion)
        return [(352, 410)]

    def scene_narrow(self, design, p, y, night):
        if design == "H1":
            A.treeline(p, 5, 37, y - 2, 11, night, seed=7, taper=(False, True))
            A.ground(p, 5, 40, y - 3, y, seed=7, night=night)
            A.corn_shock(p, 15, y - 1, 25, night, seed=4)
            A.pumpkin(p, 30, y - 1, 5, night=night)
            A.treeline(p, 145, NARROW - 5, y - 2, 11, night, seed=9, taper=(True, False))
            A.ground(p, 140, NARROW - 5, y - 3, y, seed=9, night=night)
            A.turkey(p, 150, y - 1, night, s=0.55)
            A.pumpkin(p, 163, y - 1, 4, night=night, fam="linen")
            A.candle(p, NARROW - 9, y - 1, 9, night, motion=False)
            for (sx_, sr_) in ((15, 7), (30, 6), (150, 5), (163, 5), (NARROW - 9, 3)):
                A.contact(p, sx_, y - 1, sr_)
        elif design == "H2":
            if self._clear(p, NARROW - 22, y - 3, NARROW - 13, y + 6):
                A.leaf(p, NARROW - 22, y - 3, "squash", night, "maple9", reuse=False)
            p.harvest_on_rule = True        # the figures' rule, which only its decoration is told of, takes a harvest
        elif self._clear(p, 156, y - 18, 171, y - 4):
            A.leaf(p, 156, y - 18, "wheat", night, "maple9", reuse=False)
            A.acorn(p, 167, y - 10, night)

    def rule_decor(self, p, x0, x1, y, seed, night):
        """Fallen leaves along the rule, further apart under an element sheet's title; and on a phone's H2 a
        little harvest standing at the right end of the figures' rule, where no word is."""
        A.leaves_on(p, x0, x1, y, seed=seed, night=night, gap=(9, 24) if y == SHEET_RULE else (7, 20))
        if getattr(p, "harvest_on_rule", False) and self._clear(p, 146, y - 11, 174, y):
            A.pumpkin(p, 152, y - 1, 4.5, night=night)
            A.pumpkin(p, 163, y - 1, 3.5, night=night, fam="linen")
            A.acorn(p, 169, y - 6, night)

    def finish(self, p, night):
        A.lamplight(p, night)

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        """A pumpkin and an acorn in the corner of the notes, where no word is."""
        if p.w > NARROW:
            (cx, base, rx), (ax, ay) = (x + 1, y + 18, 5.5), (x + 9, y + 12)
        else:
            (cx, base, rx), (ax, ay) = (x + 7, y + 3, 5), (x + 14, y - 3)
        if self._clear(p, cx - 7, base - 11, cx + 8, base, 1):
            A.pumpkin(p, cx, base, rx, night=night)
        if self._clear(p, ax, ay, ax + 4, ay + 6, 1):
            A.acorn(p, ax, ay, night)

    def heart(self, p, x, y):
        A.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        """A bar striped like a harvest table runner, squash and cream, `period` pixels a stripe: lit along
        the top, shaded along the bottom."""
        S, Ln = RAMP["squash"], RAMP["linen"]
        for yy in range(y0, y0 + h):
            f = (yy - y0) / max(1, h - 1)
            band = 0 if f < 0.2 else (1 if f < 0.7 else 2)
            for xx in range(x0, x0 + w):
                warm = ((xx - x0) // period) % 2 == 0
                p.px(xx, yy, (S[5], S[4], S[3])[band] if warm else (Ln[6], Ln[5], Ln[3])[band])

    def link_colours(self, night):
        if night:
            return X["node_night"], X["night_rule"], X["body_night"], RAMP["coal"][2]
        return C["white"], X["rule_day"], C["ink"], X["dim_day"]

    def link_top(self, p, x0, x1, y, seed, night):
        """A rim of wicker along the button's top edge, straw woven over brown stakes."""
        Wh, B = RAMP["wheat"], RAMP["bark"]
        k = -1 if night else 0
        for xx in range(x0 - 1, x1 + 1):
            stake = (xx + seed) % 4 == 1
            p.px(xx, y, B[4 + k] if stake else Wh[4 + k])
            p.px(xx, y + 1, B[3 + k] if stake and (xx // 4) % 2 else Wh[2 + k] if stake else Wh[3 + k])

    def link_icon(self, index, night, ink):
        """A maple leaf, turning colour from one button to the next."""
        return A.MAPLE7, A.leaf_pal(LINK_LEAVES[index % len(LINK_LEAVES)], night)

    # ---- the elements
    def card_bevel(self, night):
        return (RAMP["coal"][3], RAMP["coal"][0]) if night else (C["white"], X["dim_day"])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A band of wicker down the icon cell's edge, an acorn on the lid and fallen leaves along it."""
        Wh, B = RAMP["wheat"], RAMP["bark"]
        k = -1 if night else 0
        for yy in range(y + 1, y + h - 1):
            stake = (yy - y) % 4 == 1
            for i in range(3):
                over = (i != 1) if ((yy - y) // 4) % 2 == 0 else (i == 1)
                c = (B[5 + k], B[4 + k], B[2 + k])[i] if stake and over else (Wh[5 + k], Wh[4 + k], Wh[2 + k])[i]
                p.px(x + 10 + i, yy, c)
        if lid:
            A.acorn(p, x + 9, y - 5, night)
        A.leaves_on(p, x + (15 if lid else 3), x + w - 2, y, seed=x + y, night=night, gap=(10, 24))

    def wire_ink(self, night):
        return RAMP["linen"][4] if night else self.ink(night)["body"]

    def wire_lights(self, p, cells, night, seed):
        """Small leaves caught along the wire where it runs level, every seventh pixel."""
        run = sorted((x, y) for (x, y, d) in cells[4:-6] if d == "h")
        fams = ("cranberry", "squash", "wheat")
        for i, (x, y) in enumerate(run[::7]):
            A.leaf(p, x - 1, y + 1, fams[(i + seed) % 3], night, "tiny", flip=i % 2 == 1)

    def dashes(self, night):
        return [RAMP["cranberry"][4], X["muted_night"]] if night else [RAMP["cranberry"][3], RAMP["bark"][3]]

    def ornament(self, kind, p, x, y, night):
        """The horn of plenty spilling beside the schematic's flow."""
        if kind != "schematic":
            return (0, 0)
        if p is not None:
            A.cornucopia(p, x, y + HORN_FOOT, night)
        return HORN

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as an ear of corn standing on end: rows of golden kernels, each lit on its upper
        left, the ear rounded at its tip and shaded round from the left, and green husks flaring at its foot."""
        Wh, S = RAMP["wheat"], RAMP["sage"]
        k = -1 if night else 0
        edge = self.wire_ink(night)
        for xx in range(bx, bx + bw):
            nx = 2 * (xx - bx + 0.5) / bw - 1
            lam = max(0.0, nx * LX + math.sqrt(1 - nx * nx) * LZ)
            for yy in range(base - v, base):
                if yy == base - v and xx in (bx, bx + bw - 1):
                    continue
                t = round(2.6 + 2.4 * lam)
                if (xx - bx) % 3 == 2 or (base - yy) % 3 == 0:
                    t -= 1                                  # the seams between the kernels
                p.px(xx, yy, Wh[max(1, min(6, t + k))])
        for xx in range(bx - 1, bx + bw + 1):
            if xx in (bx - 1, bx + bw):
                p.vline(xx, base - v + 1, base, edge)
            elif xx in (bx, bx + bw - 1):
                p.px(xx, base - v, edge)
            else:
                p.px(xx, base - v - 1, edge)
        hh = min(5, max(2, v // 5))
        for j in range(hh):                                 # the husks, flaring out at the foot
            f = j / max(1, hh - 1)
            for xx in (bx - 1 - round(f * 1.4), bx + bw + round(f * 1.4)):
                p.px(xx, base - 1 - j, S[3 + k] if xx < bx else S[2 + k])
            p.px(bx + round(bw * 0.3), base - 1 - j, S[4 + k])
            p.px(bx + round(bw * 0.7), base - 1 - j, S[3 + k])

    def peak_mark(self, p, x, y, night):
        A.leaf(p, x - 1, y - 1, "cranberry", night, "maple7", reuse=False)

    def dial_ring(self, p, arc, night):
        """Half a pumpkin pie for the dial: the smooth orange filling, and round it the golden crust,
        crimped every tenth of the half turn, each crimp lit and shaded. Its inner edge keeps clear of the
        figures the dial sets inside it."""
        (x0, cy), (x1, _) = arc[0], arc[-1]
        cx, r = (x0 + x1) / 2, (x1 - x0) / 2 + 1.5
        S, Wh = RAMP["squash"], RAMP["wheat"]
        k = -1 if night else 0
        r0, n = r - 7, 20
        for yy in range(math.floor(cy - r) - 1, math.ceil(cy) + 1):
            for xx in range(math.floor(cx - r) - 1, math.ceil(cx + r) + 1):
                dx, dy = xx + 0.5 - cx, yy + 0.5 - cy
                rho = math.hypot(dx, dy)
                f = (math.pi - math.atan2(-dy, dx)) / (math.pi / n)
                within = f - math.floor(f)
                if not r0 <= rho <= r + 0.9 * math.sin(math.pi * within) - 0.6 or dy > 0:
                    continue
                if rho < r0 + 3:
                    lit = -dx / r * 0.6 - dy / r * 0.6
                    c = S[(5 if lit > 0.45 else 4) + k]
                else:
                    c = Wh[(5 if within < 0.5 else 3) + k] if rho > r - 2.2 else Wh[4 + k]
                p.px(xx, yy, c)

    def dial_tick(self, p, x, y, night):
        """None: the crust's crimps are the dial's ticks."""

    def dial_hub(self, p, cx, cy, night):
        A.acorn(p, cx - 2, cy - 4, night)

    def material(self, i, xx, yy, y0, y1, lift, night):
        """Four cloths for a harvest table, by turns: a flannel plaid, a cable knit, burlap and plain linen."""
        Cr, B, Ln, Wh = RAMP["cranberry"], RAMP["bark"], RAMP["linen"], RAMP["wheat"]
        kind = i % 4
        if kind == 0:
            a, b = (xx // 3) % 3 == 0, ((yy - y0) // 3) % 3 == 0
            c = B[2] if a and b else (Cr[2] if a or b else Cr[3])
        elif kind == 1:
            c = Ln[5] if ((xx + (yy // 2)) % 4) in (0, 1) else Ln[4]
        elif kind == 2:
            c = Wh[3] if (xx + yy) % 2 == 0 else Wh[2]
        else:
            c = Ln[6] if (xx + yy) % 5 else Ln[4]
        return step(c, lift)

    def counter_cell(self, q, ox, oy, night):
        """A counter's blank place card, 11 by 15, as set at a harvest table: a cream card folded along its
        top, lit on its left, a red maple leaf printed in its corner. It lies on a layer just under the
        drawing's own, so the digit written on it is always over it, whatever ink the digit takes."""
        Ln, Cr = RAMP["linen"], RAMP["cranberry"]
        k = -1 if night else 0
        L = q.layer("card", z=-1)
        for yy in range(15):
            for xx in range(11):
                c = Ln[6 + k] if xx < 8 else Ln[5 + k]
                if yy == 0:
                    c = Ln[4 + k]
                if yy == 1:
                    c = Ln[3 + k]
                if xx == 10 or yy == 14:
                    c = Ln[3 + k]
                q.px(ox + xx, oy + yy, c, L)
        q.sprite(ox + 7, oy + 2, [".a.", "aab", ".b."], {"a": Cr[4 + k], "b": Cr[3 + k]}, L=L)

    def counter_ink(self, night, dim):
        """Ink on the card; a leading nought written pale, as an unused place is."""
        return RAMP["linen"][3] if dim else C["ink"]

    def timeline_line(self, p, x0, x1, y, night):
        """The twine the releases hang from: two strands twisted together, light and dark by turns."""
        B = RAMP["bark"]
        k = -1 if night else 0
        for x in range(x0, x1):
            p.px(x, y, B[5 + k] if x % 3 == 0 else B[4 + k])
            p.px(x, y + 1, B[3 + k] if x % 3 != 1 else B[2 + k])

    def release(self, p, x, gy, kind, night, i=0):
        """A release hanging from the twine by its stem: a maple leaf, a bigger one for a big release, a
        cranberry for a patch, the outline of a leaf not yet turned for one still to come, and an acorn for
        the repository's creation, the seed it grew from."""
        k = -1 if night else 0
        if kind == "big":
            A.leaf(p, x - 4, gy + 1, "squash", night, "maple9", turn=2, reuse=False)
        elif kind == "major":
            A.leaf(p, x - 3, gy + 1, ("cranberry", "squash", "wheat")[i % 3], night, "maple7", turn=2)
        elif kind == "minor":
            Cr = RAMP["cranberry"]
            for (dx, dy, c) in ((0, 2, RAMP["bark"][3 + k]), (0, 3, Cr[5 + k]), (1, 3, Cr[3 + k]), (0, 4, Cr[3 + k]),
                                (1, 4, Cr[2 + k])):
                p.px(x + dx, gy + dy, c)
        elif kind == "made":
            A.acorn(p, x - 1, gy + 1, night)
        else:
            art = ["...#...", "...#...", ".#.#.#.", "#.....#", ".#...#.", "#.#.#.#", "...#..."]
            p.sprite(x - 3, gy + 1, art, {"#": self.ink(night)["muted"]})

    def today_mark(self, p, x, y, night):
        """At today a leaf has just let go of the twine, as far below it as the sheet's frame allows."""
        A.leaf(p, x + 2, min(y + 5, p.h - 10), "wheat", night, "maple5", turn=1, reuse=False)

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor as an acorn: a nut in their colour with their initials on it, under a cap of scales
        with its stalk; a bot is a little turkey with an aerial."""
        if not person.get("initials"):
            A.turkey(p, cx, cy + 8, night, s=0.62)
            p.vline(cx, cy - 12, cy - 8, RAMP["coal"][4] if night else RAMP["coal"][3])
            p.halo(cx + 0.5, cy - 12.5, 2.2, 2.2, RAMP["wheat"][4], (0.25, 0.4))
            p.px(cx, cy - 13, RAMP["wheat"][5])
            return
        name = ("cranberry", "squash", "sage")[i % 3]
        Rm = RAMP[name]
        lo, hi = {"cranberry": (1, 4), "squash": (3, 6), "sage": (1, 4)}[name]     # so the initials keep 4.5:1
        sphere(p, cx + 0.5, cy + 1.5, 7.0, Rm, lo=lo, hi=hi)
        ini = str(person["initials"])[:2]
        if name == "squash":
            p.text(cx - 3, cy, ini, RAMP["coal"][0], "35")
        else:
            p.text(cx - 3, cy, ini, C["white"], "35", shadow=Rm[0])
        B = RAMP["bark"]
        k = -1 if night else 0
        for j in range(4):                                     # the cap: rows of scales, lit on the left
            half = 7.6 - (3 - j) * 0.9 if j else 5.6
            for xx in range(math.floor(cx + 0.5 - half), math.ceil(cx + 0.5 + half)):
                u = (xx + 0.5 - cx - 0.5) / half
                t = 4 if u < -0.3 else (3 if u < 0.4 else 2)
                if (xx + j) % 2 == 0:
                    t -= 1
                p.px(xx, cy - 7 + j, B[max(1, t + k + (1 if j == 0 else 0))])
        p.px(round(cx), cy - 8, B[3 + k])
        p.px(round(cx) + 1, cy - 9, B[3 + k])

    def commit_bar(self, p, x, y, w, fill, night):
        """A contributor's share, striped like a harvest table runner, squash and cream."""
        S, Ln = RAMP["squash"], RAMP["linen"]
        p.box(x, y, w + 2, 4, self.wire_ink(night))
        for xx in range(fill):
            warm = (xx // 2) % 2 == 0
            p.px(x + 1 + xx, y + 1, S[4] if warm else Ln[6])
            p.px(x + 1 + xx, y + 2, S[2] if warm else Ln[4])

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """A wreath of autumn leaves round the seal: `n` maple leaves laid round a ring just outside the
        disc, each pointing outward, red, orange and gold by turns."""
        fams = ("cranberry", "squash", "wheat", "squash")
        for j in range(n):
            a = -math.pi / 2 + j * 2 * math.pi / n
            x, y = cx + math.cos(a) * (r0 + 3), cy + math.sin(a) * (r0 + 3)
            turn = round(((a + math.pi / 2) % (2 * math.pi)) / (math.pi / 2)) % 4
            A.leaf(p, round(x) - 3, round(y) - 3, fams[j % 4], night, "maple7", turn=turn)

    def seal_mark(self, p, x, y, night):
        A.acorn(p, x + 5, y, night)

    def placard_board(self, p, night):
        """A farm stand's sign: planks with a grain, lit on their top-left faces and nailed at the corners,
        round the evening or the linen it is painted on."""
        A.paper(p, night, 3, 5, p.w - 6, p.h - 8, uid="pl")
        if night:
            A.stars(p, 8, 10, p.w - 8, p.h - 32, 24, seed=9, twinkling=False, faint=True)
        W = RAMP["bark"]
        rnd = random.Random(4)
        streak = {yy: rnd.choice((2, 2, 3, 1)) for yy in range(0, p.h)}
        streak_v = {xx: rnd.choice((2, 2, 3, 1)) for xx in range(0, p.w)}
        w, h = p.w, p.h
        for (x, y, bw, bh, horiz) in ((0, 2, w, 4, True), (0, h - 6, w, 4, True), (0, 2, 4, h - 4, False),
                                      (w - 4, 2, 4, h - 4, False)):
            for yy in range(y, y + bh):
                for xx in range(x, x + bw):
                    t = streak[yy] if horiz else streak_v[xx]
                    if (xx * 7 + yy * 13) % 37 == 0:
                        t = 1
                    p.px(xx, yy, W[t])
        p.hline(0, w, 2, W[4])
        p.vline(0, 2, h - 2, W[4])
        p.hline(0, w, h - 3, W[1])
        p.vline(w - 1, 2, h - 2, W[1])
        p.hline(0, w, h - 2, W[0])
        p.box(3, 5, w - 6, h - 10, W[0])
        p.hline(4, w - 4, 6, X["shade_ink"] + ":0.18")
        p.vline(4, 7, h - 6, X["shade_ink"] + ":0.18")
        for (nx, ny) in ((1, 3), (w - 3, 3), (1, h - 5), (w - 3, h - 5)):
            p.px(nx, ny, RAMP["wheat"][4])
            p.px(nx + 1, ny, RAMP["wheat"][2])

    def placard(self, d, night):
        """The kit's placard on the farm stand's sign, then a garland of leaves along the sign's top, clear of
        the owner's tag, and a pumpkin at the foot of the description, where no word of it lies."""
        p = super().placard(d, night)
        owner = clip(fold(str(d.get("owner", "")).upper(), "35"), 120, "35")
        x0 = max(90, 28 + measure(owner, "35") + 6)
        if 170 - x0 >= 30:
            A.garland(p, x0, 170, 3, 40, 3, night, gap=7)
        if self._clear(p, 185, 56, 189, 60, 0) and self._clear(p, 180, 60, 193, 67, 0):     # its stem, its body
            A.pumpkin(p, 186, 67, 4.5, night=night)
        return p

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """Fallen leaves along the badge's top, kept inside its shape: little leaves two rows deep, each a
        point over a lit and a shaded half, red, orange, gold and brown by turns, a pixel or two apart."""
        x, i = 1 + seed % 2, 0
        while x < w - 2:
            R = RAMP[TRIM[(i + seed) % len(TRIM)]]
            for (dx, dy, c) in ((1, 0, R[5]), (0, 1, R[4]), (1, 1, R[4]), (2, 1, R[3])):
                if inside(x + dx, dy, w, s["h"], s["corner"]):
                    p.px(x + dx, dy, c)
            x += 3 + (1 if (i * 7 + seed) % 3 == 0 else 0)
            i += 1

    def badge_label(self):
        return (RAMP["bark"][3], C["white"])

    def badge_gold(self):
        return (RAMP["wheat"][4], C["coal"])

    def badge_states(self):
        # Yellow is drawn in squash, so it stands apart from the wheat label, with dark letters.
        return {"green": (RAMP["sage"][2], C["white"]), "yellow": (RAMP["squash"][4], C["coal"]),
                "red": (RAMP["cranberry"][3], C["white"]), "slate": (C["slate"], C["white"])}

    def badge_swatches(self):
        # A plaid is cranberry checked with a darker cranberry; that darker red is its block, so a deep red
        # written colour takes it while a brighter one stays plain cranberry.
        return {"cranberry": (RAMP["cranberry"][3], C["white"], None),
                "plaid": (RAMP["cranberry"][2], C["white"], "plaid"),
                "squash": (RAMP["squash"][4], C["coal"], None), "wheat": (RAMP["wheat"][4], C["coal"], None),
                "sage": (C["sage"], C["white"], None), "plum": (RAMP["plum"][4], C["white"], None),
                "linen": (C["white"], C["ink"], "outline"), "evening": (RAMP["plum"][1], C["white"], "stars"),
                "slate": (C["slate"], C["white"], None), "bark": (RAMP["bark"][4], C["white"], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        if pattern == "plaid":
            return RAMP["cranberry"][2] if (x // 3) % 3 == 0 or (y // 3) % 3 == 0 else RAMP["cranberry"][3]
        if pattern == "stars" and (x * 7 + y * 13) % 23 == 0 and y not in text_rows:
            return C["white"] if (x + y) % 2 else RAMP["wheat"][5]
        return c

    def badge_outline(self, pattern):
        return RAMP["bark"][3] if pattern == "outline" else None

    def badge_shine(self, c, y, h):
        """Plastic's gloss: the leaves light its top, so only its foot is shaded a step."""
        try:
            return step(c, -1) if y == h - 1 else c
        except KeyError:
            return c

    def plate_colours(self, mode):
        if mode == "day":
            return dict(paper=C["paper"], dot=C["grid"], frame=RAMP["bark"][3], block=RAMP["bark"][3], ink=C["ink"],
                        letters=C["white"])
        if mode == "night":
            return dict(paper=RAMP["coal"][1], dot=C["grid_n"], frame=RAMP["cranberry"][4], block=RAMP["cranberry"][3],
                        ink=X["body_night"], letters=C["white"])
        return dict(paper=RAMP["wheat"][4], dot=RAMP["wheat"][3], frame=C["coal"], edge=RAMP["wheat"][2], ink=C["coal"])

    def plate_edge(self, block):
        return step(block, -1)


SET = Thanksgiving()
