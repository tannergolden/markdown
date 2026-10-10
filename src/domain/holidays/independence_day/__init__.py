# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Independence Day set: the Fourth of July in red, white and blue.

Titles are painted with the flag, the union's stars on blue across their
tops and red and white stripes below. A band of the union set with stars
frames every sheet, swags of bunting hang across the top from gold stars and
little stars lie along the rules. Headers stand on a summer lawn before a line
of trees: the flag flying from its pole with its free end fluttering, and a
picnic with a sparkler burning. By day the paper is a cool white; by night
the sky is a deep blue, a lamp at the foot of the pole lights the flag,
fireflies blink over the grass and fireworks rise, burst and fall. Nothing
the night brings is drawn by day: no firework, no firefly, no lamp.
"""
from __future__ import annotations

import math
import random

from ..designs import NARROW, Holiday
from ..designs.badges import TOP, inside
from ..pixel import LX, LZ, sphere
from . import art as A
from .palette import C, NIGHT_SKY, RAMP, TOKENS, X, step

# A link button's star by turns, as the stars along a rule take them; by day the white one is the union's blue.
LINK_STARS = ("gold", "red", "white")


def _clear(p, cx, cy, cells, margin=1) -> bool:
    """Whether every pixel of `cells`, placed at (cx, cy), stands `margin` clear of every word."""
    return all(p.clear_of_words(cx + x - margin, cy + y - margin, cx + x + 1 + margin, cy + y + 1 + margin)
               for x, y in cells)


def _starts(p, y0, y1) -> int:
    """Where the first word set in rows y0 to y1 begins: how far a scene on a sheet's left may reach."""
    return min((b[0] for b in p.words if b[1] < y1 and y0 < b[3]), default=p.w)


def _ends(p, y0, y1) -> int:
    """Where the last word set in rows y0 to y1 ends: where a scene on a sheet's right may begin."""
    return max((b[2] for b in p.words if b[1] < y1 and y0 < b[3]), default=0)


class IndependenceDay(Holiday):
    key = "independence-day"
    name = "Independence Day"
    tokens = frozenset(TOKENS)

    # ---- colour and paper
    def ink(self, night):
        """`title` is the union's blue; a title is painted with the flag, so it is never drawn plain, but by
        night it is a step lighter than the union, which reads on every row of the sky. `shadow` is what a
        check mark's shadow takes, the red two steps down."""
        N, R = RAMP["navy"], RAMP["red"]
        return dict(
            title=N[6] if night else N[3], shadow=R[2] if night else R[1],
            body=X["body_night"] if night else C["ink"], muted=X["muted_night"] if night else X["muted_day"],
            rule=X["night_rule"] if night else N[4], accent=X["accent_night"] if night else X["accent_day"],
            tag=R[3], tag_ink=C["white"],
            fill=X["node_night"] if night else C["white"], dim=X["dim_night"] if night else X["dim_day"],
        )

    def lit(self, night):
        """The flag laid over a title's letters; by day a dark edge round them, so the white stripes hold
        their shape on the white paper, and a pale shadow under them. The night sky needs no edge."""
        if night:
            return dict(paint=A.FLAG, night=True)
        return dict(paint=A.FLAG, outline=RAMP["navy"][0], shadow=RAMP["cloth"][3], night=False)

    def paper(self, p, night, uid="p"):
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        if not night:
            return C["paper"]
        return NIGHT_SKY[min(len(NIGHT_SKY) - 1, int(y * len(NIGHT_SKY) / p.h))]

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        A.stars(p, x0, y0, x1, y1, n, seed=seed, twinkling=twinkling, faint=faint, avoid=avoid)

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The paper, or by night the sky with a star to every twelve units of its width (half as many on a
        drawing made lighter to fit its budget), twinkling if it moves."""
        self.paper(p, night)
        if night:
            self.stars(p, 6, 16, p.w - 6, int(y1 * 0.7), n=p.w // (24 if p.lite else 12), seed=seed,
                       twinkling=motion, avoid=avoid)

    def frame(self, p, night, webs=False):
        A.star_frame(p, night)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """Swags of bunting hung from gold stars: 45 units a swag and 7 deep across a wide sheet, 34 and 6
        across a phone's."""
        wide = x1 - x0 > NARROW
        A.bunting(p, x0, x1, y, 45 if wide else 34, 7 if wide else 6, night)

    def tag(self, p, x, y, w, h, night):
        """The red block a tag's white letters sit on: lit along its top, shaded along its foot."""
        R = RAMP["red"]
        p.rect(x, y, w, h, R[3])
        p.hline(x, x + w, y, R[4])
        p.hline(x, x + w, y + h - 1, R[2])

    def title_text(self, p, x, y, s, night, scale):
        """The flag laid over the letters (see `lit`)."""
        return p.text(x, y, s, self.ink(night)["title"], "57", scale, **self.lit(night))

    # ---- fireworks, after dark only
    def _burst(self, p, x, y, r, colour, kind, night, motion, seed, name=None, offset=0.0, light=0, rise=None,
               floor=None):
        """A firework (see `art.firework`), by night only and only where it lies clear of every word and above
        row `floor`, when there is one. A rising trail that would pass behind a word, or reach the floor,
        starts higher; a burst that would lie on a word is left out."""
        if not night:
            return
        body = A.burst_cells(kind, r, ("open", "bloom", "fall", "fade") if motion else ("bloom",), seed)
        if not _clear(p, x, y, body) or (floor is not None and y + max(q[1] for q in body) >= floor):
            return
        rise = r + 7 if rise is None else rise
        if motion:
            low = round(r * 0.45) + 3                 # where the second, higher trail starts
            if floor is not None:
                rise = min(rise, floor - y - 6)
            rise = max(rise, low)
            while rise > low and not _clear(p, x, y, A.burst_cells(kind, r, ("trail1",), seed, rise)):
                rise -= 1
            if not _clear(p, x, y, A.burst_cells(kind, r, ("trail1", "trail2"), seed, rise)):
                return
        A.firework(p, x, y, r, colour, kind, night, motion=motion, offset=offset, seed=seed, name=name,
                   light=light, rise=rise)

    def _show(self, p, bursts, night, motion, first=0, of=None, floor=None):
        """The fireworks of a header taking turns round one loop, each (x, y, r, colour, kind, light) and a
        seventh value, the rise, where the approved art set its trail short of the words below. `first` is
        the first one's place in a show of `of`, when the show's other bursts are drawn elsewhere."""
        n = of or len(bursts)
        for i, (x, y, r, colour, kind, light, *rise) in enumerate(bursts, first):
            self._burst(p, x, y, r, colour, kind, night, motion, i + x, name=f"fw{i}",
                        offset=round(i * A.SHOW_SPAN / max(1, n - 1), 3), light=light,
                        rise=rise[0] if rise else None, floor=floor)

    # ---- the headers' scenes
    def section_mark(self, p, x, y, night):
        A.star5(p, x, y, 7, "red", night)

    def strip_mark(self, p, x, y, night):
        """By night the first of H3's three fireworks, bursting beside the title. The tagline under the title
        is not set yet, so the burst and its trail keep above the title's foot, the last line set. A moving
        file shows it rise and fall; a still one keeps it in bloom."""
        foot = p.words[-1][3] if p.words else y + 13
        self._show(p, [(x + 13, min(y - 5, foot - 15), 9, "red", "peony", 0, 13)], night, True, of=3, floor=foot)

    def scene(self, design, p, rule, night, motion):
        return {"H1": self._h1_scene, "H2": self._h2_scene, "H3": self._h3_scene}[design](p, rule, night, motion)

    def _h1_scene(self, p, rule, night, motion):
        """On the left the flag flies over the lawn before a line of trees, a firecracker and a skyrocket at
        its foot; on the right a picnic on the grass, a sparkler burning. By night fireworks burst over both.
        Where a long line of words comes near, the trees stop short of it and the flag is the phone's smaller
        one."""
        left = _starts(p, rule - 60, rule)
        A.treeline(p, 5, min(70, _starts(p, rule - 16, rule) - 2), rule - 2, 13, night, seed=2, taper=(False, True))
        A.lawn(p, 5, 66, rule - 3, rule, seed=2, night=night)
        if left > 60:                                  # the flag's free end reaches x = 59
            A.flagpole(p, 9, rule - 58, rule - 1, night, flag_foot=rule - 30)
            A.waving_flag(p, 11, rule - 56, 2, night, motion=motion)
        else:
            A.flagpole(p, 9, rule - 32, rule - 1, night, flag_foot=rule - 17)
            A.waving_flag(p, 11, rule - 30, 1, night, motion=motion)
        A.firecracker(p, 46, rule - 1, night)
        if p.clear_of_words(52, rule - 20, 61, rule):
            A.rocket(p, 54, rule - 1, night, "blue")
        right = _ends(p, rule - 16, rule)
        A.treeline(p, max(334, right + 2), 410, rule - 2, 13, night, seed=6, taper=(True, False))
        A.lawn(p, 338, 410, rule - 3, rule, seed=6, night=night)
        A.blanket(p, 341, 386, rule - 1, night)
        if p.clear_of_words(342, rule - 18, 360, rule):
            A.basket(p, 345, rule - 3, night, w=13)
        A.watermelon(p, 365, rule - 3, night, w=11)
        A.sparkler(p, 395, rule - 1, 13, night, phase=0, motion=motion, lean=-1)
        A.rocket_pop(p, 402, rule - 16, night)
        for (sx, sr) in ((10, 3), (48, 3), (56, 3), (363, 22), (403, 3)):
            A.contact(p, sx, rule - 1, sr)
        if night:
            A.light_pool(p, 394, rule - 2, 9, 2.5, night)
        A.fireflies(p, max(340, _ends(p, rule - 27, rule - 7) + 2), 408, rule - 26, rule - 8, 4, night, seed=3,
                    motion=motion)
        A.fireflies(p, 8, min(64, _starts(p, rule - 21, rule - 5) - 2), rule - 20, rule - 6, 3, night, seed=5,
                    motion=motion)
        self._show(p, [(86, 34, 14, "red", "peony", 46, 15), (370, 30, 11, "gold", "willow", 36),
                       (30, 24, 7, "blue", "ring", 30)], night, motion)
        return [(5, 66), (338, 410)]

    def _h2_scene(self, p, rule, night, motion):
        """On the right the flag flies from its pole in front of a line of trees, its free end fluttering,
        and below it a picnic on the lawn with a sparkler burning; by night fireworks burst behind it. The
        pole stands clear of the longest line of words beside it."""
        A.treeline(p, max(290, _ends(p, rule - 17, rule) + 2), 410, rule - 2, 15, night, seed=3, taper=(True, False))
        A.lawn(p, 294, 410, rule - 3, rule, seed=3, night=night)
        top = rule - 58
        pole = max(303, _ends(p, top - 2, rule) + 2)
        A.flagpole(p, pole, top, rule - 1, night, flag_foot=top + 30)
        A.waving_flag(p, pole + 2, top + 2, 2, night, motion=motion)
        A.blanket(p, 336, 394, rule - 1, night)
        A.basket(p, 341, rule - 3, night)
        A.watermelon(p, 361, rule - 3, night)
        A.rocket_pop(p, 380, rule - 16, night)
        A.sparkler(p, 401, rule - 1, 15, night, phase=0, motion=motion, lean=-1)
        for (sx, sr) in ((pole + 1, 3), (365, 30), (401, 2.5)):
            A.contact(p, sx, rule - 1, sr)
        if night:
            A.light_pool(p, 400, rule - 2, 10, 2.5, night)
        A.fireflies(p, 330, 408, rule - 30, rule - 10, 5, night, seed=7, motion=motion)
        self._show(p, [(380, 38, 18, "red", "peony", 62), (338, 22, 9, "gold", "willow", 34),
                       (401, 66, 7, "blue", "ring", 30)], night, motion)
        return [(294, 410)]

    def _h3_scene(self, p, rule, night, motion):
        """On the lawn at the right a small flag on its pole, a sparkler and a firecracker; by night two more
        fireworks after the one beside the title."""
        A.treeline(p, max(348, _ends(p, rule - 14, rule) + 2), 410, rule - 2, 11, night, seed=4, taper=(True, False))
        A.lawn(p, 352, 410, rule - 3, rule, seed=4, night=night)
        A.flagpole(p, 362, rule - 32, rule - 1, night, flag_foot=rule - 17)
        A.waving_flag(p, 364, rule - 30, 1, night, motion=motion)
        A.sparkler(p, 398, rule - 1, 11, night, phase=1, motion=motion)
        A.firecracker(p, 404, rule - 1, night, h=7)
        A.contact(p, 363, rule - 1, 3)
        if night:
            A.light_pool(p, 398, rule - 2, 8, 2.2, night)
        A.fireflies(p, 356, 408, rule - 22, rule - 6, 3, night, seed=2, motion=motion)
        self._show(p, [(330, 30, 8, "blue", "ring", 0, 13), (392, 26, 8, "gold", "willow", 30)], night, motion,
                   first=1, of=3)
        return [(352, 410)]

    def scene_narrow(self, design, p, y, night):
        if design == "H1":
            A.treeline(p, 5, 37, y - 2, 10, night, seed=7, taper=(False, True))
            A.lawn(p, 5, 44, y - 3, y, seed=7, night=night)
            if p.clear_of_words(8, y - 31, 40, y - 12):
                A.flagpole(p, 10, y - 30, y - 1, night, flag_foot=y - 15)
                A.flag(p, 12, y - 28, 1, night)
            A.treeline(p, 145, NARROW - 5, y - 2, 10, night, seed=9, taper=(True, False))
            A.lawn(p, 138, NARROW - 5, y - 3, y, seed=9, night=night)
            if p.clear_of_words(140, y - 8, 155, y):
                A.watermelon(p, 142, y - 1, night, w=11)
            A.sparkler(p, NARROW - 16, y - 1, 12, night, motion=False)
            A.rocket(p, NARROW - 11, y - 1, night)
            A.contact(p, 147, y - 1, 7)
            self._burst(p, NARROW - 36, y - 22, 7, "red", "peony", night, False, 3)
        elif design == "H2":
            self._burst(p, NARROW - 20, y + 1, 6, "gold", "willow", night, False, 5)
        else:
            self._burst(p, 160, min(36, y - 5), 8, "blue", "ring", night, False, 2)

    def rule_decor(self, p, x0, x1, y, seed, night):
        """Stars lying along a rule, further apart along the rule under an element's tag (row 20). In a
        drawing that moves, one whose flag flutters, a few of them twinkle."""
        moving = any(m[2] and m[2][0] == "seq" for m in p.meta.values())
        A.spangles(p, x0, x1, y, seed=seed, night=night, twinkling=moving, gap=(10, 30) if y == 20 else (9, 26))

    def finish(self, p, night):
        A.lamplight(p, night)

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        A.liberty_bell(p, x - 2, y - 3, night, w=13)

    def heart(self, p, x, y):
        A.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        """A bar in the flag's stripes, red and white, `period` pixels a stripe: lit along the top, shaded
        along the bottom."""
        R, W = RAMP["red"], RAMP["cloth"]
        for yy in range(y0, y0 + h):
            f = (yy - y0) / max(1, h - 1)
            band = 0 if f < 0.2 else (1 if f < 0.7 else 2)
            for xx in range(x0, x0 + w):
                red = ((xx - x0) // period) % 2 == 0
                p.px(xx, yy, (R[4], R[3], R[2])[band] if red else (W[6], W[5], W[3])[band])

    def link_colours(self, night):
        if night:
            return X["node_night"], X["night_rule"], X["body_night"], RAMP["navy"][1]
        return C["white"], RAMP["navy"][4], C["ink"], X["dim_day"]

    def link_top(self, p, x0, x1, y, seed, night):
        """A strip of the union along the button's top edge, a white star every four pixels, and a strip of
        the flag down its left side: blue with a star over red and white stripes."""
        N, R, W = RAMP["navy"], RAMP["red"], RAMP["cloth"]
        for xx in range(x0 - 1, x1 + 1):
            p.px(xx, y, W[6] if (xx + seed) % 4 == 2 else (N[3] if night else N[2]))
        for yy in range(y + 1, y + 10):
            for i, xx in enumerate((x0 - 1, x0)):
                if yy < y + 4:
                    c = W[6] if (yy == y + 2 and i == 0) else (N[4], N[2])[i]
                else:
                    red = (yy - y - 4) % 2 == 0
                    c = (R[4], R[2])[i] if red else (W[6], W[4])[i]
                p.px(xx, yy, c)

    def link_icon(self, index, night, ink):
        """The set's star, 7 by 7 (see `LINK_STARS`)."""
        colour = LINK_STARS[index % len(LINK_STARS)]
        if colour == "white" and not night:
            colour = "navy"
        cells = A.star_cells(7, colour, night)
        tones = sorted(set(cells.values()))
        pal = {chr(ord("a") + i): c for i, c in enumerate(tones)}
        code = {c: ch for ch, c in pal.items()}
        return ["".join(code[cells[(i, j)]] if (i, j) in cells else "." for i in range(7)) for j in range(7)], pal

    # ---- the elements
    def card_bevel(self, night):
        return (RAMP["navy"][2], RAMP["navy"][0]) if night else (C["white"], X["dim_day"])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A strip of the flag for the icon cell's edge (the union's blue with stars at the top, red and white
        stripes below), a gold star on the lid and stars along it."""
        N, R, W = RAMP["navy"], RAMP["red"], RAMP["cloth"]
        union = y + 1 + (h - 2) * 3 // 7
        for yy in range(y + 1, y + h - 1):
            for i in range(3):
                if yy < union:
                    c = W[6] if i == 1 and (yy - y) % 3 == 2 else (N[4], N[3], N[2])[i]
                else:
                    red = ((yy - union) // 2) % 2 == 1
                    c = (R[4], R[3], R[2])[i] if red else (W[6], W[5], W[3])[i]
                p.px(x + 10 + i, yy, c)
        if lid:
            A.star5(p, x + 9, y - 4, 5, "gold", night, reuse=True)
        A.spangles(p, x + (17 if lid else 3), x + w - 2, y, seed=x + y, night=night, gap=(12, 30))

    def wire_ink(self, night):
        return RAMP["cloth"][4] if night else self.ink(night)["body"]

    def wire_lights(self, p, cells, night, seed):
        """Pennants strung where the wire runs level, every seventh pixel, red, white and blue by turns."""
        N, R, W = RAMP["navy"], RAMP["red"], RAMP["cloth"]
        cols = [(R[4], R[3], R[2]), (W[6], W[4], W[3]) if night else (W[5], W[3], W[2]),
                (N[5], N[4], N[3]) if night else (N[4], N[3], N[2])]
        run = sorted((x, y) for (x, y, d) in cells[4:-6] if d == "h")
        for i, (x, y) in enumerate(run[::7]):
            a, b, c = cols[(i + seed) % 3]
            p.px(x, y + 1, a)
            p.px(x + 1, y + 1, b)
            p.px(x + 2, y + 1, c)
            p.px(x + 1, y + 2, c)

    def dashes(self, night):
        return [RAMP["red"][4] if night else RAMP["red"][3], X["muted_night"] if night else RAMP["navy"][3]]

    def ornament(self, kind, p, x, y, night):
        """The Liberty Bell, in a free corner of the schematic."""
        if kind == "schematic":
            if p is not None:
                A.liberty_bell(p, x, y, night, w=23)
            return (23, 26)
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as an ice pop in three flavours: blue at the foot, white in the middle and red at
        the top, in proportion to its own height, lit from the left, its top rounded and outlined."""
        R, W, N = RAMP["red"], RAMP["cloth"], RAMP["navy"]
        for xx in range(bx, bx + bw):
            nx = 2 * (xx - bx + 0.5) / bw - 1
            lam = max(0.0, nx * LX + math.sqrt(1 - nx * nx) * LZ)
            for yy in range(base - v, base):
                if yy == base - v and xx in (bx, bx + bw - 1):
                    continue
                f = (base - yy - 0.5) / v
                ramp, lo, hi = (R, 2, 5) if f > 0.64 else ((W, 3, 6) if f > 0.32 else (N, 2, 5))
                p.px(xx, yy, ramp[max(lo, min(hi, round(lo + 0.2 + (hi - lo) * lam)))])
        edge = self.wire_ink(night)
        for xx in range(bx - 1, bx + bw + 1):
            if xx in (bx - 1, bx + bw):
                p.vline(xx, base - v + 1, base, edge)
            elif xx in (bx, bx + bw - 1):
                p.px(xx, base - v, edge)
            else:
                p.px(xx, base - v - 1, edge)

    def peak_mark(self, p, x, y, night):
        A.star5(p, x - 1, y, 7, "gold", night)

    def dial_ring(self, p, arc, night):
        """The upper half of a pleated fan of bunting, its pleats the dial's ticks, nine units deep and set
        four outside the ring, so the dial's figures stand as clear of it as they do in the approved art."""
        (x0, cy), (x1, _) = arc[0], arc[-1]
        cx, r = round((x0 + x1) / 2), round((x1 - x0) / 2 + 1.5)
        A.fan_ring(p, cx, round(cy), r - 5, r + 4, night)

    def dial_tick(self, p, x, y, night):
        """None: the fan's pleats are the ticks."""

    def dial_hub(self, p, cx, cy, night):
        A.star5(p, cx - 3, cy - 4, 7, "gold", night)

    def material(self, i, xx, yy, y0, y1, lift, night):
        """Four cloths by turns: the flag's stripes, stars on the union's blue, picnic gingham and white linen."""
        R, N, W = RAMP["red"], RAMP["navy"], RAMP["cloth"]
        kind = i % 4
        if kind == 0:
            return step(R[3], lift) if ((yy - y0) // 2) % 2 == 0 else step(W[5], lift)
        if kind == 1:
            return W[6] if (yy % 3 == 1 and (xx + (yy // 3) * 2) % 4 == 1) else step(N[3], lift)
        if kind == 2:
            a, b = (xx // 2) % 2 == 0, (yy // 2) % 2 == 0
            return step(R[3] if a and b else (R[5] if a or b else W[5]), lift)
        return step(W[6] if (xx + yy) % 5 else W[4], lift)

    def counter_cell(self, q, ox, oy, night):
        """One counter's blank firecracker, 11 by 15: a red paper tube lit from the left, a white label round
        its middle where the digit goes, and a fuse curling from its top. It lies on the layer under the
        drawing, so the digit lettered on it is never covered."""
        R, W, K = RAMP["red"], RAMP["cloth"], RAMP["coal"]
        k = -1 if night else 0
        for yy in range(15):
            for xx in range(11):
                u = (xx + 0.5) / 11 * 2 - 1
                lam = max(0.0, u * LX + math.sqrt(max(0.0, 1 - u * u)) * LZ)
                if 2 <= yy <= 12 and 1 <= xx <= 9:
                    c = W[4] if xx == 9 else (W[6] if xx < 7 else W[5])
                else:
                    c = R[max(1, min(6, round(1.6 + 2.6 * lam) + 1 + k))]
                if yy == 14:
                    c = step(c, -1)
                q.px(ox + xx, oy + yy, c, "far")
        for (dx, dy) in ((5, -1), (5, -2), (6, -3), (7, -3)):
            q.px(ox + dx, oy + dy, K[5] if night else K[3], "far")

    def counter_ink(self, night, dim):
        """Ink on the firecracker's white label, a leading nought printed pale."""
        return RAMP["cloth"][3] if dim else C["ink"]

    def timeline_line(self, p, x0, x1, y, night):
        """The fuse the releases hang from: a braided cord, twisted light and dark by turns along its top."""
        Bz = RAMP["bronze"]
        for x in range(x0, x1):
            p.px(x, y, Bz[5] if x % 3 == 0 else (Bz[3] if night else Bz[4]))
            p.px(x, y + 1, Bz[2] if x % 3 != 1 else Bz[3])

    def release(self, p, x, gy, kind, night, i=0):
        """A release hanging from the fuse by a thread: a gold star, a bigger one for a big release, a bead of
        red, white or blue for a patch, the outline of a star not yet lit for one still to come, and a
        rosette for the repository's creation."""
        R, W, N = RAMP["red"], RAMP["cloth"], RAMP["navy"]
        thread = W[2] if night else W[3]
        if kind == "big":
            p.px(x, gy + 2, thread)
            A.star5(p, x - 4, gy + 3, 9, "gold", night)
        elif kind == "major":
            p.px(x, gy + 2, thread)
            A.star5(p, x - 3, gy + 3, 7, "gold", night, reuse=True)
        elif kind == "minor":
            a, b = [(R[4], R[2]), (W[6], W[3]) if night else (W[4], W[2]), (N[5] if night else N[4], N[2])][i % 3]
            for (dx, dy, c) in ((0, 2, a), (-1, 3, a), (0, 3, a), (1, 3, b), (0, 4, b)):
                p.px(x + dx, gy + dy, c)
        elif kind == "made":
            p.px(x, gy + 2, thread)
            A.rosette(p, x - 2, gy + 3, night)
        else:
            p.px(x, gy + 2, thread)
            art = ["...#...", "..#.#..", "##...##", ".#...#.", "..#.#..", ".#.#.#.", ".#...#."]
            p.sprite(x - 3, gy + 3, art, {"#": self.ink(night)["muted"]})

    def today_mark(self, p, x, y, night):
        """The fuse's burning end."""
        A.fuse_spark(p, x, y, night, motion=False)

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor: a ball in red, blue or gold under Uncle Sam's hat, their initials on it; a bot is a
        skyrocket with an aerial on its nose."""
        if not person.get("initials"):
            A.rocket(p, cx - 2, cy + 8, night, "white", stick=False)
            p.vline(cx, cy - 8, cy - 4, RAMP["coal"][4] if night else RAMP["coal"][3])
            p.halo(cx + 0.5, cy - 8.5, 2.2, 2.2, RAMP["gold"][4], (0.25, 0.4))
            p.px(cx, cy - 9, RAMP["gold"][5])
            return
        name = ("red", "navy", "gold")[i % 3]
        Rm = RAMP[name]
        lo, hi = {"red": (1, 4), "navy": (1, 5), "gold": (3, 6)}[name]   # so the initials keep 4.5:1
        sphere(p, cx + 0.5, cy + 0.5, 7.2, Rm, lo=lo, hi=hi)
        ini = str(person["initials"])[:2]
        if name == "gold":
            p.text(cx - 3, cy - 1, ini, RAMP["coal"][0], "35")
        else:
            p.text(cx - 3, cy - 1, ini, C["white"], "35", shadow=Rm[0])
        A.top_hat(p, cx - 6, cy - 17, 13, 12, night)

    def commit_bar(self, p, x, y, w, fill, night):
        """A contributor's share, in the flag's red and white stripes."""
        R, W = RAMP["red"], RAMP["cloth"]
        p.box(x, y, w + 2, 4, self.wire_ink(night))
        for xx in range(fill):
            red = (xx // 2) % 2 == 0
            p.px(x + 1 + xx, y + 1, R[4] if red else W[6])
            p.px(x + 1 + xx, y + 2, R[2] if red else W[4])

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """A pleated prize rosette of white, red and blue, from the seal's rim out (see `art.seal_rosette`)."""
        A.seal_rosette(p, cx, cy, r0 - 1, r1, night)

    def seal_mark(self, p, x, y, night):
        A.star5(p, x + 4, y, 7, "gold", night)

    def placard_board(self, p, night):
        """A painted porch sign: planks with a grain, lit on their top-left faces, gold nails at the corners,
        and a fan of bunting hung from its top."""
        A.paper(p, night, 3, 5, p.w - 6, p.h - 8, uid="pl")
        if night:
            A.stars(p, 8, 10, p.w - 8, p.h - 32, 24, seed=9, twinkling=False, faint=True)
        Wd = RAMP["wood"]
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
                    p.px(xx, yy, Wd[t])
        p.hline(0, w, 2, Wd[4])
        p.vline(0, 2, h - 2, Wd[4])
        p.hline(0, w, h - 3, Wd[1])
        p.vline(w - 1, 2, h - 2, Wd[1])
        p.hline(0, w, h - 2, Wd[0])
        p.box(3, 5, w - 6, h - 10, Wd[0])
        p.hline(4, w - 4, 6, X["shade_ink"] + ":0.18")
        p.vline(4, 7, h - 6, X["shade_ink"] + ":0.18")
        for (nx, ny) in ((1, 3), (w - 3, 3), (1, h - 5), (w - 3, h - 5)):
            p.px(nx, ny, RAMP["gold"][4])
            p.px(nx + 1, ny, RAMP["gold"][2])
        A.half_fan(p, 128, 4, 11, night)

    def placard_mark(self, p, x, y, night):
        """None: the fan on the board is the placard's ornament."""

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """The flag's trim along the badge's top, kept inside its shape: a row of the union's blue with a
        white star every four pixels, over a row of red and white stripes two pixels long."""
        N, R, W = RAMP["navy"], RAMP["red"], RAMP["cloth"]
        for x in range(w):
            if inside(x, 0, w, s["h"], s["corner"]):
                p.px(x, 0, W[6] if (x + seed) % 4 == 2 else N[2])
            if inside(x, 1, w, s["h"], s["corner"]):
                p.px(x, 1, R[3] if (x // 2) % 2 == 0 else W[5])

    def badge_label(self):
        return (RAMP["navy"][2], C["white"])

    def badge_gold(self):
        return (RAMP["gold"][3], C["coal"])

    def badge_states(self):
        # Yellow is drawn in the ember's orange, so it stands apart from the gold label, with dark letters.
        return {"green": (RAMP["green"][2], C["white"]), "yellow": (RAMP["ember"][4], C["coal"]),
                "red": (RAMP["red"][3], C["white"]), "slate": (C["slate"], C["white"])}

    def badge_swatches(self):
        """The flag's red in its stripes, its blue, the night's blue with its stars and white with a blue
        edge, as the preview's palette row has them; then gold and a paler tan, the ember's orange, the
        lawn's green, a lighter blue, a dark red, the violet, the slate grey and the wood's brown."""
        R, N, G = RAMP["red"], RAMP["navy"], RAMP["gold"]
        return {"red": (R[3], C["white"], "stripes"), "navy": (N[3], C["white"], None),
                "stars": (N[1], C["white"], "stars"), "white": (C["white"], C["ink"], "outline"),
                "gold": (G[4], C["coal"], None), "bronze": (RAMP["bronze"][5], C["coal"], None),
                "ember": (RAMP["ember"][4], C["coal"], None), "green": (RAMP["green"][3], C["white"], None),
                "blue": (N[4], C["white"], None), "maroon": (R[2], C["white"], None),
                "violet": (X["violet"], C["white"], None), "slate": (C["slate"], C["white"], None),
                "wood": (RAMP["wood"][4], C["white"], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        """Stripes: every other pair of rows a shade darker, the flag's stripes. Stars: white and gold points
        on the night's blue, kept out of the letters' rows."""
        if pattern == "stripes" and ((y - TOP) // 2) % 2 == 1:
            return RAMP["red"][2]
        if pattern == "stars" and (x * 7 + y * 13) % 23 == 0 and y not in text_rows:
            return C["white"] if (x + y) % 2 else RAMP["gold"][5]
        return c

    def badge_outline(self, pattern):
        return RAMP["navy"][3] if pattern == "outline" else None

    def badge_shine(self, c, y, h):
        """Plastic's gloss: the trim lights its top, and its foot is shaded a step."""
        try:
            return step(c, -1) if y == h - 1 else c
        except KeyError:
            return c

    def plate_colours(self, mode):
        R, N, G = RAMP["red"], RAMP["navy"], RAMP["gold"]
        if mode == "day":
            return dict(paper=C["paper"], dot=C["grid"], frame=N[3], block=N[3], ink=C["ink"], letters=C["white"])
        if mode == "night":
            return dict(paper=N[0], dot=C["grid_n"], frame=R[4], block=R[3], ink=X["body_night"],
                        letters=C["white"])
        return dict(paper=G[3], dot=G[2], frame=C["coal"], edge=G[2], ink=C["coal"])

    def plate_edge(self, block):
        return step(block, -1)


SET = IndependenceDay()
