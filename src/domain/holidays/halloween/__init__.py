# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Halloween set: a haunted sheet by moonlight.

Titles drip with slime; a rod striped like a witch's stockings frames every
sheet and jack-o'-lanterns hang across the top. Headers stand on a graveyard
of mounds, a dead tree against the moon, a headstone and carved pumpkins in
drifting fog, with bats circling and a ghost that bobs. By day the paper is
fog-lilac; by night a purple sky with its stars.
"""
from __future__ import annotations

import math
import random

from ..designs import NARROW, Holiday
from ..designs.badges import inside
from ..pixel import LX, LY, LZ, Pix, sphere, tube
from . import art as A
from .palette import BULBS, C, NIGHT_SKY, RAMP, TOKENS, X, ramp_for, step

LINK_SPRITES = ("pumpkin", "bat", "ghost", "hat")


def slime(p: Pix, cells, scale, L, rnd, y0):
    """Slime poured over a title: a thin lumpy coat along the letters' upper edges (the top two rows
    of the face, so it never pools inside a B or an E), and drips that run down the strokes, a few
    of them past the foot of the letter, each ending in a drop that catches the light."""
    S = RAMP["slime"]
    tops = {(gx, gy) for (gx, gy) in cells if (gx, gy - 1) not in cells and gy < y0 + 2 * scale}
    for (gx, gy) in sorted(tops):
        left_end, right_end = (gx - 1, gy) not in tops, (gx + 1, gy) not in tops
        p.px(gx, gy, S[3] if right_end else S[4], L)
        if not (left_end or right_end) and rnd.random() < 0.45:
            p.px(gx, gy - 1, S[5], L)
    if scale < 2:
        return
    runs = []
    for (gx, gy) in sorted(tops, key=lambda q: (q[1], q[0])):
        if (gx - 1, gy) in tops:
            continue
        n = 1
        while (gx + n, gy) in tops:
            n += 1
        runs.append((gx, gy, n))
    dw = 2 if scale >= 4 else 1
    for (gx, gy, n) in runs:
        if n < dw + 2:
            continue
        for _ in range(1 + n // 16):
            if rnd.random() > (0.42 if scale >= 3 else 0.3):
                continue
            x0 = gx + rnd.randint(1, n - dw - 1)
            depth = 0
            while all((x0 + i, gy + depth + 1) in cells for i in range(dw)):
                depth += 1
            if depth < 2:
                continue
            ln = rnd.randint(max(2, depth // 3), max(2, int(depth * 0.85)))
            if ln >= depth - 1 and rnd.random() < 0.55:
                ln = depth + rnd.randint(1, max(1, scale // 2 + 1))    # it runs off the foot
            for i in range(1, ln + 1):
                for j in range(dw):
                    p.px(x0 + j, gy + i, (S[5] if j == 0 else S[3]) if dw == 2 else S[4], L)
            yb = gy + ln
            p.px(x0 - (1 if dw == 1 else 0), yb + 1, S[4], L)
            p.px(x0 + dw - (1 if dw == 1 else 0), yb + 1, S[3], L)
            for j in range(dw):
                p.px(x0 + j, yb + 1, S[5] if j == 0 else S[4], L)
                p.px(x0 + j, yb + 2, S[3], L)
            p.px(x0, yb + 1, S[6], L)


def floating_ghost(p: Pix, x, y, w, h, night, motion=True):
    """A ghost that floats: in a moving file it bobs up and down on a loop of its own; still, it rests."""
    L = p.layer("bob0", ("bob", [0, 0, 1, 2, 2, 1], 2.6)) if motion else "base"
    A.ghost(p, x, y, w, h, night, L=L)


class Halloween(Holiday):
    key = "halloween"
    name = "Halloween"
    tokens = frozenset(TOKENS)

    # ---- colour and paper
    def ink(self, night):
        return dict(
            title=X["title_night"] if night else C["witch"], shadow=RAMP["purple"][3] if night else RAMP["pumpkin"][3],
            body=X["body_night"] if night else C["ink"], muted=X["muted_night"] if night else X["muted_day"],
            rule=C["lilac"] if night else C["violet"], accent=X["accent_night"] if night else X["accent_day"],
            tag=C["orange"], tag_ink=C["coal"],
            fill=X["node_night"] if night else C["white"], dim=X["dim_night"] if night else X["dim_day"],
        )

    def lit(self, night):
        """A bevel down the title's left edges and along its foot, and by night a pumpkin glow."""
        if night:
            return dict(bevel=(RAMP["pumpkin"][5], RAMP["pumpkin"][2]), glow=(RAMP["pumpkin"][4], (0.2,)), night=True)
        return dict(bevel=(RAMP["purple"][4], RAMP["purple"][1]), night=False)

    def paper(self, p, night, uid="p"):
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        if not night:
            return C["fog"]
        return NIGHT_SKY[min(len(NIGHT_SKY) - 1, int(y * len(NIGHT_SKY) / p.h))]

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        A.stars(p, x0, y0, x1, y1, n, seed=seed, twinkling=twinkling, faint=faint, avoid=avoid)

    def frame(self, p, night, webs=False):
        A.stocking_frame(p, night, webs=webs)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        A.lanterns(p, x0, x1, y, sag=sag, span=span, spacing=spacing, night=night, seed=seed)

    def tag(self, p, x, y, w, h, night):
        """The orange block a tag's black letters sit on: lit along its top, shaded along its foot."""
        P = RAMP["pumpkin"]
        p.rect(x, y, w, h, C["orange"])
        p.hline(x, x + w, y, P[5])
        p.hline(x, x + w, y + h - 1, P[2])

    def title_text(self, p, x, y, s, night, scale):
        """Shaded letters dripping with slime, lit by the theme."""
        k = self.ink(night)
        return p.text(x, y, s, k["title"], "57", scale, shadow=k["shadow"], finish=slime, **self.lit(night))

    # ---- the headers' scenes
    def section_mark(self, p, x, y, night):
        A.bat(p, x, y, 0, night)

    def strip_mark(self, p, x, y, night):
        A.spider(p, x, y, top=9, night=night)

    def _moon(self, p, cx, cy, r, bats, night, motion, seed):
        """The moon and the bats round it, where no word stands in their way."""
        if p.clear_of_words(cx - r - 3, cy - r - 3, cx + r + 4, cy + r + 4):
            A.moon(p, cx, cy, r, night=night)
            if bats:
                A.bats(p, cx, cy, *bats, night, motion=motion, seed=seed)

    def scene(self, design, p, rule, night, motion):
        if design == "H1":
            self._moon(p, 74, rule - 60, 8, (22, 10, 2), night, motion, 4)
            A.mound(p, 5, 66, rule - 3, rule, seed=2, night=night)
            A.dead_tree(p, 32, rule - 1, 48, night, seed=3)
            A.mound(p, 338, 410, rule - 3, rule, seed=6, night=night)
            A.tombstone(p, 341, rule - 1, 15, 18, night)
            A.pumpkin(p, 372, rule - 1, 8, night=night, face="grin", phase=0)
            A.pumpkin(p, 392, rule - 1, 5, night=night, face="plain", phase=1)
            A.pumpkin(p, 404, rule - 1, 3.5, night=night)
            for (sx_, sr_) in ((348, 8.5), (372, 9), (392, 5.5), (404, 4)):
                A.contact(p, sx_, rule - 1, sr_)
            floating_ghost(p, 383, rule - 43, 13, 17, night, motion)
            A.fog(p, 5, 70, rule - 9, rule, night, seed=3, motion=motion, name="fogl")
            A.fog(p, 336, 410, rule - 9, rule, night, seed=8, motion=motion, name="fogr")
            return [(5, 66), (338, 410)]
        if design == "H2":
            self._moon(p, 351, rule - 61, 17, (30, 14, 3), night, motion, 7)
            A.mound(p, 296, 410, rule - 3, rule, seed=3, night=night)
            A.dead_tree(p, 373, rule - 1, 84, night, seed=9, clip=(5, p.w - 5))
            A.tombstone(p, 299, rule - 1, 15, 18, night)
            A.pumpkin(p, 330, rule - 1, 10, night=night, face="grin", phase=0)
            A.pumpkin(p, 396, rule - 1, 6, night=night, face="o", phase=1)
            A.pumpkin(p, 406, rule - 1, 3.5, night=night)
            for (sx_, sr_) in ((306, 8.5), (330, 11), (396, 6.5), (406, 4)):
                A.contact(p, sx_, rule - 1, sr_)
            if p.clear_of_words(278, rule - 68, 299, rule - 45):   # the ghost's box as high as it bobs, and a margin
                floating_ghost(p, 282, rule - 64, 13, 17, night, motion)
            A.fog(p, 294, 410, rule - 10, rule, night, seed=5, motion=motion)
            return [(296, 410)]
        A.mound(p, 352, 410, rule - 3, rule, seed=4, night=night)
        A.dead_tree(p, 395, rule - 1, 30, night, seed=13)
        A.pumpkin(p, 370, rule - 1, 6, night=night, face="o", phase=2)
        A.contact(p, 370, rule - 1, 6.5)
        A.candy_corn(p, 354, rule - 9, 7, night=night)
        A.bats(p, 384, rule - 41, 11, 6, 1, night, motion=motion, seed=2)
        A.fog(p, 350, 410, rule - 8, rule, night, seed=6, motion=motion)
        return [(352, 410)]

    def scene_narrow(self, design, p, y, night):
        if design == "H1":
            A.mound(p, 5, 42, y - 3, y, seed=7, night=night)
            A.dead_tree(p, 22, y - 1, 30, night, seed=5)
            A.mound(p, 140, NARROW - 5, y - 3, y, seed=9, night=night)
            A.pumpkin(p, NARROW - 22, y - 1, 7, night=night, face="grin")
            A.contact(p, NARROW - 22, y - 1, 7.5)
            if p.clear_of_words(NARROW - 34, y - 29, NARROW - 25, y - 18):
                A.ghost(p, NARROW - 34, y - 29, 9, 11, night)
        elif design == "H2":
            if p.clear_of_words(NARROW - 25, y - 4, NARROW - 16, y + 7):
                A.ghost(p, NARROW - 25, y - 4, 9, 11, night)
        else:
            A.pumpkin(p, 162, y, 6, night=night, face="o")

    def rule_decor(self, p, x0, x1, y, seed, night):
        A.ooze(p, x0, x1, y, seed=seed, drips=0.22, glints=1.0, reach=2)

    def finish(self, p, night):
        A.lamplight(p, night)

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        A.spider(p, x, y, top=4, night=night)

    def heart(self, p, x, y):
        A.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        """A bar striped like a witch's stockings, orange and black, `period` pixels a stripe: lit along
        the top, shaded along the bottom."""
        P, K = RAMP["pumpkin"], RAMP["coal"]
        for yy in range(y0, y0 + h):
            f = (yy - y0) / max(1, h - 1)
            band = 0 if f < 0.2 else (1 if f < 0.7 else 2)
            for xx in range(x0, x0 + w):
                orange = ((xx - x0) // period) % 2 == 0
                p.px(xx, yy, (P[5], P[4], P[2])[band] if orange else (K[4], K[2], K[1])[band])

    def link_colours(self, night):
        if night:
            return X["node_night"], C["lilac"], X["body_night"], RAMP["purple"][1]
        return C["white"], C["violet"], C["witch"], X["dim_day"]

    def link_top(self, p, x0, x1, y, seed, night):
        if night:
            p.hline(x0, x1, y + 1, RAMP["purple"][2])
        A.ooze(p, x0, x1, y, seed=seed, cap=1)

    def link_icon(self, index, night, ink):
        return A.ICONS[LINK_SPRITES[index % len(LINK_SPRITES)]], A.icon_pal("night" if night else "day", ink)

    # ---- the elements
    def card_bevel(self, night):
        return (RAMP["purple"][2], RAMP["purple"][0]) if night else (C["white"], X["dim_day"])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A stocking-striped band down the icon cell's edge, a pumpkin sitting on the lid, slime beside it."""
        P, K = RAMP["pumpkin"], RAMP["coal"]
        for yy in range(y + 1, y + h - 1):
            orange = ((yy - y) // 3) % 2 == 0
            for i, (o, b) in enumerate(((P[5], K[4]), (P[4], K[3]), (P[2], K[1]))):
                p.px(x + 10 + i, yy, o if orange else b)
        if lid:
            p.stamp(("lid", night), lambda q, ox, oy: A.pumpkin(q, ox, oy, 4, night=night, vine=False), x + 11, y)
        A.ooze(p, x + (17 if lid else 3), x + w - 2, y, seed=x + y, cap=1)

    def wire_ink(self, night):
        return RAMP["ghost"][4] if night else self.ink(night)["body"]

    def wire_lights(self, p, cells, night, seed):
        """A string of bulbs along the wire, every ninth pixel, each glass and glow drawn once a colour."""
        for i, (x, y, d) in enumerate(cells[5:-7]):
            if i % 9:
                continue
            colr = BULBS[(i // 9 + seed) % 3]
            R = ramp_for(colr)
            key = ("wirebulb", colr, d, night)
            if key not in p.syms:
                if d == "h":
                    glass = {(-1, 2): R[4], (0, 2): R[6], (1, 2): R[3], (-1, 3): R[3], (0, 3): R[4], (1, 3): R[2],
                             (0, 4): R[2]}
                    socket, centre = (0, 1), (0.5, 3.5)
                else:
                    glass = {(-2, -1): R[4], (-3, -1): R[3], (-2, 0): R[6], (-3, 0): R[4], (-4, 0): R[2],
                             (-2, 1): R[3], (-3, 1): R[2]}
                    socket, centre = (-1, 0), (-2.5, 0.5)
                cells_ = A.glow_cells(centre[0], centre[1], 3.2, 3.2, R[4], (0.16, 0.3) if night else (0.08, 0.15), glass)
                cells_.update(glass)
                cells_[socket] = RAMP["coal"][2]
                p.symbol(key, cells_)
            p.use(key, x, y)

    def dashes(self, night):
        return [C["orange"], C["witch"] if not night else X["muted_night"]]

    def ornament(self, kind, p, x, y, night):
        if kind == "schematic":
            if p is not None:
                A.cauldron(p, x, y, night)
            return (18, 20)
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as a kernel of candy corn stood on end: a yellow foot, an orange middle and a
        white tip, in proportion to its own height, lit from the left."""
        P, F, B = RAMP["pumpkin"], RAMP["flame"], RAMP["bone"]
        for xx in range(bx, bx + bw):
            nx = 2 * (xx - bx + 0.5) / bw - 1
            lam = max(0.0, nx * LX + (1 - nx * nx) ** 0.5 * LZ)
            for yy in range(base - v, base):
                f = (base - yy - 0.5) / v
                ramp, lo, hi = (B, 3, 6) if f > 0.78 else ((P, 2, 5) if f > 0.42 else (F, 2, 5))
                p.px(xx, yy, ramp[max(lo, min(hi, round(lo + 0.2 + (hi - lo) * lam)))])
        p.box(bx - 1, base - v - 1, bw + 2, v + 1, self.wire_ink(night))

    def peak_mark(self, p, x, y, night):
        A.candy_corn(p, x, y, 5)

    def dial_ring(self, p, arc, night):
        """A pumpkin vine bent into a half ring."""
        tube(p, arc, 2.6, _vine(8), outline=RAMP["slime"][0])

    def dial_tick(self, p, x, y, night):
        _tiny_pumpkin(p, x - 1, y - 2)

    def dial_hub(self, p, cx, cy, night):
        sphere(p, cx + 0.5, cy - 0.5, 2.6, RAMP["purple"], lo=2)
        S = RAMP["stone"]
        for i, xx in enumerate(range(cx - 4, cx + 5)):
            p.px(xx, cy + 2, S[5] if i < 3 else S[4] if i < 7 else S[2])

    def material(self, i, xx, yy, y0, y1, lift, night):
        """Candy wrappers by turns: stocking stripes, purple polka dots, candy corn and a ghostly white."""
        P, Pu, F, B, G, K = (RAMP[n] for n in ("pumpkin", "purple", "flame", "bone", "ghost", "coal"))
        kind = i % 4
        if kind == 0:
            c = P[4] if ((xx + yy) // 3) % 2 == 0 else K[3]
        elif kind == 1:
            c = Pu[5] if (xx % 4 == 1 and yy % 4 == 1) or (xx % 4 == 3 and yy % 4 == 3) else Pu[3]
        elif kind == 2:
            c = B[5] if yy < y0 + 4 else (P[4] if yy < y0 + 8 else F[4])
        else:
            c = G[6] if (xx + yy) % 5 else G[4]
        return step(c, lift)

    def counter_cell(self, q, ox, oy, night):
        """One counter's blank stone: a slab with a round top, 11 by 15, lit from the left, a pale face."""
        S = RAMP["stone"]
        cells = set()
        for yy in range(15):
            for xx in range(11):
                if yy < 5 and math.hypot(xx + 0.5 - 5.5, yy + 0.5 - 5.5) > 5.6:
                    continue
                cells.add((xx, yy))
        for (xx, yy) in cells:
            c = S[6]
            if (xx - 1, yy) not in cells or (xx, yy - 1) not in cells:
                c = X["moonlit"] if night else C["white"]
            elif (xx + 1, yy) not in cells or yy == 14:
                c = S[3]
            elif (xx + 2, yy) not in cells or yy == 13:
                c = S[5]
            q.px(ox + xx, oy + yy, c)
        for xx in range(11):
            if xx % 3 != 1:
                q.px(ox + xx, oy + 14, RAMP["slime"][2])

    def counter_ink(self, night, dim):
        S = RAMP["stone"]
        return S[2] if dim else S[0]

    def timeline_line(self, p, x0, x1, y, night):
        """The wire the releases hang from: black, lit along its top."""
        K = RAMP["coal"]
        for x in range(x0, x1):
            p.px(x, y, X["moonlit"] if night else K[4])
            p.px(x, y + 1, K[3] if night else K[1])

    def release(self, p, x, gy, kind, night, i=0):
        """A jack-o'-lantern, bigger for a big release; a small one for a release; a bulb for a patch; for
        one still to come a lantern not yet lit; for the repository's creation a skull."""
        if kind == "big":
            p.stamp(("bigjack", night), lambda q, ox, oy: A.pumpkin(q, ox, oy + 11, 5.5, night=night, face="plain",
                                                                     vine=False), x, gy)
        elif kind == "major":
            A.mini_lantern(p, x - 3, gy + 1, night, i)
        elif kind == "minor":
            A.bulb(p, x - 1, gy + 1, BULBS[1 + i % 2], "base", night)
        elif kind == "made":
            A.skull(p, x - 5, gy + 1, night=night)
        else:
            art = ["...s...", ".o.o.o.", "o.....o", "o.....o", ".o...o.", "..o.o.."]
            p.sprite(x - 3, gy + 1, art, {"s": RAMP["slime"][2], "o": self.ink(night)["muted"]})

    def today_mark(self, p, x, y, night):
        A.flame(p, x, y, night)

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor: a ball in their colour under a witch's hat, their initials on it; a bot is a
        ghost with an aerial, the ghost in the machine."""
        if not person.get("initials"):
            A.ghost(p, cx - 6, cy - 8, 13, 16, night, glow=False, arms=False, blush=False)
            p.vline(cx, cy - 12, cy - 8, RAMP["coal"][4] if night else RAMP["coal"][3])
            p.halo(cx + 0.5, cy - 12.5, 2.4, 2.4, RAMP["slime"][4], (0.2, 0.35))
            p.px(cx, cy - 13, RAMP["slime"][5])
            return
        name = ("pumpkin", "purple", "slime")[i % 3]
        Rm = RAMP[name]
        lo, hi = {"pumpkin": (2, 5), "purple": (1, 4), "slime": (0, 3)}[name]
        sphere(p, cx + 0.5, cy + 0.5, 7.2, Rm, lo=lo, hi=hi)
        ini = str(person["initials"])[:2]
        if name == "pumpkin":
            p.text(cx - 3, cy - 1, ini, RAMP["coal"][0], "35")
        else:
            p.text(cx - 3, cy - 1, ini, C["white"], "35", shadow=Rm[0])
        A.witch_hat(p, cx - 6, cy - 18)

    def commit_bar(self, p, x, y, w, fill, night):
        """A contributor's share, striped like a witch's stockings."""
        P, K = RAMP["pumpkin"], RAMP["coal"]
        p.box(x, y, w + 2, 4, self.wire_ink(night))
        for xx in range(fill):
            orange = (xx // 2) % 2 == 0
            p.px(x + 1 + xx, y + 1, P[5] if orange else K[4])
            p.px(x + 1 + xx, y + 2, P[3] if orange else K[2])

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """A rosette of candy corn round the seal: `n` kernels standing out from radius r0 to r1, each a
        wedge with a yellow foot, an orange middle and a white tip, lit on the side that faces the light."""
        B, P, F = RAMP["bone"], RAMP["pumpkin"], RAMP["flame"]
        k = -1 if night else 0
        step_a = 2 * math.pi / n
        for y in range(math.floor(cy - r1) - 1, math.ceil(cy + r1) + 1):
            for x in range(math.floor(cx - r1) - 1, math.ceil(cx + r1) + 1):
                dx, dy = x + 0.5 - cx, y + 0.5 - cy
                rho = math.hypot(dx, dy)
                if not r0 - 0.5 <= rho <= r1:
                    continue
                th = math.atan2(dy, dx)
                j = round(th / step_a)
                off = th - j * step_a
                f = (rho - r0) / (r1 - r0)
                half = step_a * 0.47 * (1 - 0.85 * f) + 0.02
                if abs(off) > half:
                    continue
                side = off / half
                ang = j * step_a
                facing = math.cos(ang) * LX + math.sin(ang) * LY
                lit = (0.55 - 0.45 * side * (1 if math.sin(ang) * LX - math.cos(ang) * LY > 0 else -1)) + 0.35 * facing
                R, lo, hi = (F, 2, 5) if f < 0.42 else ((P, 2, 5) if f < 0.78 else (B, 3, 6))
                t = max(lo, min(hi, round(lo + (hi - lo) * max(0.0, min(1.0, lit)))))
                p.px(x, y, R[max(0, t + k)])

    def seal_mark(self, p, x, y, night):
        A.bat(p, x, y, 1, night)

    def placard_board(self, p, night):
        """A graveyard sign: weathered planks with a grain, lit on their top-left faces, nailed at the
        corners, slime along the top and a cobweb in a corner."""
        A.paper(p, night, 3, 5, p.w - 6, p.h - 8, uid="pl")
        if night:
            A.stars(p, 8, 10, p.w - 8, p.h - 32, 24, seed=9, twinkling=False, faint=True)
        W = RAMP["wood"]
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
            p.px(nx, ny, RAMP["coal"][5])
            p.px(nx + 1, ny, RAMP["coal"][3])
        A.ooze(p, 1, w - 1, 2, seed=11, drips=0.3, reach=3)
        A.web(p, 4, h - 7, 5, False, night)

    def placard_mark(self, p, x, y, night):
        A.spider(p, x, y, top=7, night=night)

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """Slime along the badge's top edge, kept inside its shape: patches a row deep over a darker row,
        and now and then a drip a pixel long."""
        tmp = Pix(w, s["h"])
        A.ooze(tmp, 1, w - 1, 1, seed=seed, cap=1, drips=0.18, reach=1)
        for (x, y), c in tmp.layers["base"].items():
            if inside(x, y, w, s["h"], s["corner"]):
                p.px(x, y, c)

    def badge_label(self):
        return (RAMP["purple"][2], C["white"])

    def badge_gold(self):
        return (RAMP["flame"][3], C["coal"])

    def badge_states(self):
        # Yellow is drawn in orange, so it stands apart from the gold label, with dark letters.
        return {"green": (RAMP["slime"][2], C["white"]), "yellow": (C["orange"], C["coal"]),
                "red": (RAMP["blood"][3], C["white"]), "slate": (C["slate"], C["white"])}

    def badge_swatches(self):
        return {"pumpkin": (C["orange"], C["coal"], None), "flame": (RAMP["flame"][4], C["coal"], None),
                "slime": (RAMP["slime"][4], C["coal"], None), "witch": (C["purple"], C["white"], None),
                "lilac": (RAMP["purple"][5], C["coal"], None), "blood": (RAMP["blood"][3], C["white"], None),
                "bone": (C["white"], C["witch"], "outline"), "night": (RAMP["purple"][1], C["white"], "stars"),
                "stone": (RAMP["stone"][3], C["white"], None), "wood": (RAMP["wood"][4], C["white"], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        if pattern == "stars" and (x * 7 + y * 13) % 29 == 0 and y not in text_rows:
            return RAMP["flame"][5]
        return c

    def badge_outline(self, pattern):
        return RAMP["ghost"][3] if pattern == "outline" else None

    def badge_shine(self, c, y, h):
        try:
            return step(c, 1) if y == 2 else step(c, -1) if y == h - 1 else c
        except KeyError:
            return c

    def plate_colours(self, mode):
        if mode == "day":
            return dict(paper=C["fog"], dot=C["grid"], frame=C["purple"], block=C["purple"], ink=C["witch"],
                        letters=C["white"])
        if mode == "night":
            return dict(paper=RAMP["purple"][0], dot=C["grid_n"], frame=C["orange"], block=C["orange"],
                        ink=X["body_night"], letters=C["coal"])
        return dict(paper=RAMP["flame"][3], dot=RAMP["flame"][2], frame=C["coal"], edge=RAMP["flame"][2],
                    ink=C["coal"])

    def plate_edge(self, block):
        return step(block, -1)


TINY_PUMPKIN = [".s.", "454", "321"]


def _tiny_pumpkin(p: Pix, x, y, L="base"):
    """A pumpkin three pixels wide, top-left at (x, y): a tick on the dial."""
    P = RAMP["pumpkin"]
    p.sprite(x, y, TINY_PUMPKIN, {"s": RAMP["slime"][3], "1": P[1], "2": P[2], "3": P[3], "4": P[4], "5": P[5]}, 1, L)


def _vine(seed=0, lo=1, hi=4):
    """A colour for each pixel of a vine: the tube's light, twisted by a darker spiral."""
    rnd = random.Random(seed)
    S = RAMP["slime"]

    def colour(s, o, lam, x, y):
        v = lo + 0.2 + (hi - lo) * lam + rnd.uniform(-0.5, 0.5)
        if int(s * 0.9 + o * 1.6) % 3 == 0:
            v -= 1.1
        return S[max(lo - 1, min(hi, round(v)))]
    return colour


SET = Halloween()
