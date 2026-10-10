# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Juneteenth set: a cookout and Galveston on the Gulf, June 19.

Titles are painted like the Juneteenth flag, blue above and red below a white
arc of horizon, with here and there a glint like its bursting star. A ribbon in
the red, black and green flown beside the flag frames every sheet, and little
flags and pennants hang across the top. Headers stand on a lawn or a beach: the
flag flying over a barbecue pit, a table in the shade of a live oak, a brick
chapel and palms by the water. By day the paper is warm white under a June sun;
by night the sky is deep blue, with string lights, fireflies and fireworks.
"""
from __future__ import annotations

import math
import random

from ..designs import NARROW, Holiday
from ..designs.badges import inside
from ..pixel import GLYPHS, LX, LZ, Paint
from . import art as A
from .palette import C, CONFETTI, NIGHT_SKY, RAMP, TOKENS, X, step

# The flag's paint on a title: the white arc a band higher across the middle third of a line, so the horizon
# rises across the title the way the flag's arc does.
FOIL = Paint("foil", A.foil_fill, variant=lambda mid: 2 if 1 / 3 <= mid <= 2 / 3 else 3)
# A contributor's pin by their place in the roster: its ramp, the tone of its face and its letters.
PINS = (("red", 3, C["white"]), ("gold", 4, RAMP["coal"][0]), ("green", 3, C["white"]))


class Juneteenth(Holiday):
    key = "juneteenth"
    name = "Juneteenth"
    tokens = frozenset(TOKENS)
    phone_scene_rows = 46      # the flag's pole on a phone, its motto set beside the flag

    # ---- colour and paper
    def ink(self, night):
        """The flag's blue for tags and day accents, its gold for night accents; `shadow`, a deep blue, is what
        a check casts, as a title's gold shadow is its own (see `title_text`)."""
        B = RAMP["blue"]
        return dict(
            title=B[5] if night else B[2], shadow=B[2] if night else B[1],
            body=X["body_night"] if night else C["ink"], muted=X["muted_night"] if night else X["muted_day"],
            rule=X["night_rule"] if night else X["rule_day"], accent=RAMP["gold"][5] if night else B[3],
            tag=B[3], tag_ink=C["white"],
            fill=X["node_night"] if night else C["white"], dim=X["dim_night"] if night else X["dim_day"],
        )

    def lit(self, night):
        """Painted like the flag, every band a tone lighter by night so it reads on the sky."""
        return dict(paint=FOIL, night=night)

    def paper(self, p, night, uid="p"):
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        if not night:
            return C["paper"]
        return NIGHT_SKY[min(len(NIGHT_SKY) - 1, int(y * len(NIGHT_SKY) / p.h))]

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        A.stars(p, x0, y0, x1, y1, n, seed=seed, twinkling=twinkling, faint=faint, avoid=avoid)

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The paper, or by night the June sky over the Gulf and its stars, one for every twelve pixels across
        (half as many on a drawing made lighter to fit its budget)."""
        self.paper(p, night)
        if night:
            self.stars(p, 6, 16, p.w - 6, int(y1 * 0.7), n=p.w // (24 if p.lite else 12), seed=seed,
                       twinkling=motion, avoid=avoid)

    def frame(self, p, night, webs=False):
        """The red, black and green ribbon; along the top and foot of a wide header by night its stars light
        up in turn."""
        A.tricolor_frame(p, night, chase=webs and p.w > NARROW)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """Little Juneteenth flags and red, black and green pennants on a cord a row under the frame, swagged
        forty pixels a span across a sheet and 34 on a phone."""
        wide = p.w > NARROW
        A.flag_garland(p, x0, x1, y - 1, span=40 if wide else 34, sag=4 if wide else 3, night=night)

    def tag(self, p, x, y, w, h, night):
        """The flag's blue block a tag's white letters sit on: lit along its top, shaded along its foot."""
        B = RAMP["blue"]
        p.rect(x, y, w, h, B[3])
        p.hline(x, x + w, y, B[4])
        p.hline(x, x + w, y + h - 1, B[2])

    def title_text(self, p, x, y, s, night, scale):
        """Letters painted like the flag, glinting here and there like its star. By day a gold shadow lies under
        them and a deep blue edge runs round them, which the white of the arc needs to read on the paper."""
        k = self.ink(night)
        if not night:
            A.title_edge(p, x, y, s, scale, RAMP["blue"][0], RAMP["gold"][4])
        w = p.text(x, y, s, k["title"], "57", scale, **self.lit(night))
        if not p.lite:
            A.title_glints(p, x, y, s, scale)
        return w

    # ---- the headers' scenes
    def section_mark(self, p, x, y, night):
        A.star5(p, x, y, 5, "gold", night)

    def strip_mark(self, p, x, y, night):
        A.star5(p, x - 2, y - 4, 7, "gold", night)
        A.nova_glint(p, x + 9, y - 5, L=p.twinkle(2))

    def scene(self, design, p, rule, night, motion):
        if design == "H1":
            return self._cookout(p, rule, night, motion)
        if design == "H2":
            return self._galveston(p, rule, night, motion)
        A.lawn(p, 352, 410, rule - 3, rule, seed=4, night=night)
        A.flag_on_pole(p, 356, rule - 59, rule - 1, 40, 25, night, motion)
        A.sign(p, 372, rule - 1, "JUNE 19", night)
        A.glass_of_red(p, 363, rule - 1, night)
        for (sx, sr) in ((357, 3), (389, 5)):
            A.contact(p, sx, rule - 1, sr)
        if night:
            A.fireflies(p, 354, 408, rule - 20, rule - 5, 4, night, seed=9, motion=motion)
        A.show(p, [(318, 22, 10, "gold", "nova", 0)], night, motion, dur=6.0, start=0.1)
        return [(352, 410)]

    def _cookout(self, p, rule, night, motion):
        """H1's cookout: on the left the flag over the barbecue pit, smoke rising from its stack and split post
        oak beside it; on the right the table in the shade of a live oak, with red drink, watermelon and a red
        velvet cake, and a red ice chest by the trunk; by night string lights and fireflies, and fireworks."""
        A.lawn(p, 5, 66, rule - 3, rule, seed=2, night=night)
        A.lawn(p, 342, 410, rule - 3, rule, seed=6, night=night)
        A.flag_on_pole(p, 8, rule - 81, rule - 1, 38, 23, night, motion)
        sx, sy = A.smoker(p, 22, rule - 1, night, motion=motion)
        A.smoke(p, sx, sy, sy - 22, night, motion=motion, drift=6, dur=5.6)
        A.woodpile(p, 51, rule - 1, night)
        under = A.live_oak(p, 334, 411, rule - 1, 400, night, top=max(20, rule - 77), bottom=rule - 41)
        top = A.picnic_table(p, 348, rule - 1, 40, night)
        A.drink_jar(p, 351, top, night, motion=motion)
        A.glass_of_red(p, 363, top, night)
        A.watermelon_slices(p, 368, top, 2, night)
        A.red_velvet_cake(p, 381, top, night)
        A.ice_chest(p, 390, rule - 1, night)
        for (sx, sr) in ((9, 3), (33, 11), (57, 7), (368, 14), (396, 6), (403, 5)):
            A.contact(p, sx, rule - 1, sr)
        if night:
            A.string_lights(p, 352, 398, under + 1, 4, night, motion)
            A.fireflies(p, 8, 64, rule - 34, rule - 6, 7, night, seed=3, motion=motion)
            A.fireflies(p, 356, 398, under + 7, rule - 14, 3, night, seed=5, motion=motion)
        A.show(p, [(84, 24, 10, "gold", "nova", 0), (314, 24, 9, "red", "peony", 0)], night, motion, dur=9.0)
        return [(5, 62), (350, 410)]

    def _galveston(self, p, rule, night, motion):
        """H2's Galveston, where the order was read: the Gulf behind the dune with a sailboat on the swell, a
        brick chapel, the flag flying and palms along the seawall. By day the sun is high, clouds drift and
        gulls wheel over the water; by night fireworks go up over it, their light on the water."""
        if not night:
            if p.clear_of_words(292, 16, 309, 33):
                A.sun(p, 300, 24, 5)
            A.cloud(p, 322, 34, 20)
            A.cloud(p, 384, 22, 14)
        A.gulf(p, 312, 410, rule - 32, rule - 4, night, motion)
        A.sailboat(p, 361, rule - 29, night, L=p.layer("bob1", ("bob", (0, 0, 1, 1, 1, 0), 3.6)) if motion else "base")
        A.dune(p, 306, 330, rule - 26, rule - 3, night)
        A.sand(p, 296, 410, rule - 4, rule, night=night)
        A.chapel(p, 316, rule - 1, night)
        A.flag_on_pole(p, 350, rule - 64, rule - 1, 30, 19, night, motion)
        A.palm(p, 390, rule - 1, 34, night, lean=1, seed=2)
        A.palm(p, 403, rule - 1, 26, night, lean=-1, seed=5)
        for (sx, sr) in ((328, 13), (351, 3), (391, 3), (404, 3)):
            A.contact(p, sx, rule - 1, sr)
        if not night:
            A.gulls(p, [(A.wavy(380, 20, 262, 14, 30, 2, 1.0) + [(-40, -40)] * 6, 9.0),
                        (A.wavy(300, 44, 402, 30, 26, 2, 1.2) + [(-40, -40)] * 6, 8.0)], motion)
        A.show(p, [(372, rule - 80, 12, "gold", "nova", 26), (398, rule - 64, 8, "red", "peony", 16)], night, motion,
               dur=10.0)
        return [(294, 410)]

    def scene_narrow(self, design, p, y, night):
        if design == "H1":
            A.lawn(p, 5, 70, y - 3, y, seed=7, night=night)
            A.lawn(p, 104, NARROW - 5, y - 3, y, seed=9, night=night)
            if p.clear_of_words(6, y - 47, 38, y - 23):          # the flag and its pole's ball, a pixel round
                A.flag_on_pole(p, 8, y - 46, y - 1, 26, 16, night, False)
            A.smoker(p, 26, y - 1, night, motion=False)
            A.woodpile(p, 55, y - 1, night)
            top = A.picnic_table(p, 110, y - 1, 36, night)
            A.drink_jar(p, 112, top, night, motion=False)
            A.watermelon_slices(p, 124, top, 2, night)
            A.hibiscus(p, 152, y - 1, night)
            A.glass_of_red(p, 168, y - 1, night)
            for (sx, sr) in ((9, 3), (37, 11), (61, 7), (128, 13), (157, 5)):
                A.contact(p, sx, y - 1, sr)
        elif design == "H2":
            # The flag on a short pole and a glass of red drink, standing on SECTION A-A's line at the right.
            if p.clear_of_words(146, y - 17, NARROW - 4, y + 6):
                A.flag_on_pole(p, 150, y - 14, y + 5, 16, 9, night, False)
                A.glass_of_red(p, 170, y + 5, night)
        else:
            # A gold star and a glint beside the title, level with its letters, which stand at row 26.
            A.star5(p, 152, 31, 7, "gold", night)
            A.nova_glint(p, 164, 29, L="near")

    def rule_decor(self, p, x0, x1, y, seed, night):
        """Confetti lying along the rule, sparser along an element's rule under its tag."""
        A.confetti_on(p, x0, x1, y, seed=seed, night=night, gap=(4, 12) if y == 20 else (3, 9))

    def finish(self, p, night):
        A.lamplight(p, night)

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        """A little flag on a stick and a gold star: standing on the title block's lower rule, or on a phone
        at the top of the notes."""
        if p.w == NARROW:
            A.little_flag(p, x + 2, y - 5, y + 7, night)
            A.star5(p, x + 12, y - 3, 5, "gold", night)
        else:
            A.little_flag(p, x, y + 1, p.h - 4, night)
            A.star5(p, x + 9, y + 6, 5, "gold", night)

    def heart(self, p, x, y):
        A.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        """A bar striped in the flag's blue and red by turns, `period` pixels a stripe: lit along the top,
        shaded along the bottom."""
        B, R = RAMP["blue"], RAMP["red"]
        for yy in range(y0, y0 + h):
            f = (yy - y0) / max(1, h - 1)
            band = 0 if f < 0.2 else (1 if f < 0.7 else 2)
            for xx in range(x0, x0 + w):
                blue = ((xx - x0) // period) % 2 == 0
                p.px(xx, yy, (B[5], B[4], B[3])[band] if blue else (R[5], R[4], R[3])[band])

    def link_colours(self, night):
        if night:
            return X["node_night"], X["night_rule"], X["body_night"], RAMP["dusk"][2]
        return C["white"], X["rule_day"], C["ink"], X["dim_day"]

    def link_top(self, p, x0, x1, y, seed, night):
        """A strip of red over green along the button's top edge, a white star stitched on every four pixels."""
        R, G = RAMP["red"], RAMP["green"]
        k = -1 if night else 0
        for xx in range(x0 - 1, x1 + 1):
            p.px(xx, y, C["white"] if (xx + seed) % 4 == 1 else R[4 + k])
            p.px(xx, y + 1, G[3 + k])

    def link_icon(self, index, night, ink):
        """No icon: the set's links carry their label and nothing else, so the icon's room stays empty."""
        return [], {}

    # ---- the elements
    def card_bevel(self, night):
        return (RAMP["dusk"][3], RAMP["dusk"][0]) if night else (C["white"], X["dim_day"])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A strip of red, black and green down the icon cell's edge with a white star across it, a gold star
        on the lid and confetti along it."""
        R, G, K = RAMP["red"], RAMP["green"], RAMP["coal"]
        k = -1 if night else 0
        for yy in range(y + 1, y + h - 1):
            for i, c in enumerate((R[3 + k], K[1], G[3 + k])):
                p.px(x + 10 + i, yy, c)
        for (a, b) in A.BURST3:
            p.px(x + 10 + a, y + h // 2 - 1 + b, RAMP["linen"][5] if night else C["white"])
        if lid:
            A.star5(p, x + 9, y - 5, 5, "gold", night)
        A.confetti_on(p, x + (15 if lid else 3), x + w - 2, y, seed=x + y, night=night, gap=(5, 14))

    def wire_ink(self, night):
        return RAMP["linen"][4] if night else self.ink(night)["body"]

    def wire_lights(self, p, cells, night, seed):
        """Confetti caught along the wire where it runs level, above it and below it by turns."""
        run = sorted((x, y) for (x, y, d) in cells[4:-6] if d == "h")
        for i, (x, y) in enumerate(run[::5]):
            fam = CONFETTI[(i + seed) % len(CONFETTI)]
            p.px(x, y - 1 if i % 2 else y + 1, A.confetti_colour(fam, night, i % 3 != 1))

    def dashes(self, night):
        B = RAMP["blue"]
        return [B[5], X["muted_night"]] if night else [B[3], RAMP["red"][3]]

    def ornament(self, kind, p, x, y, night):
        """The cookout at the schematic's foot: a table under a gingham cloth with a jar of red drink and
        watermelon on it, and the barbecue pit beside it, its embers lighting nothing further."""
        if kind != "schematic":
            return (0, 0)
        if p is not None:
            top = A.picnic_table(p, x, y + 23, 36, night)
            A.drink_jar(p, x + 2, top, night, motion=False)
            A.watermelon_slices(p, x + 14, top, 2, night)
            A.smoker(p, x + 40, y + 23, night, motion=False, light=False)
        return (67, 23)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as a tall glass of red drink, hibiscus steeped and sweetened, poured to its count:
        silver walls bright on the left, the drink lit on its left with ice at its top, a bubble or two rising."""
        R, S, Ln = RAMP["red"], RAMP["silver"], RAMP["linen"]
        k = -1 if night else 0
        for xx in range(bx, bx + bw):
            nx = 2 * (xx - bx + 0.5) / bw - 1
            lam = max(0.0, nx * LX + math.sqrt(1 - nx * nx) * LZ)
            for yy in range(base - v, base):
                if xx in (bx, bx + bw - 1):
                    c = S[6 + k] if xx == bx else S[3 + k]
                elif yy < base - v + 2:
                    c = Ln[6 + k] if (xx + yy) % 3 else S[5 + k]
                else:
                    c = R[max(1, min(6, round(2.8 + 2.2 * lam) + k))]
                p.px(xx, yy, c)
        if bw >= 5 and v >= 6:
            rnd = random.Random(bx * 31 + v)
            for _ in range(v // 6):
                p.px(bx + rnd.randint(2, bw - 3), base - rnd.randint(3, v - 3), R[6 + k])
        edge = self.wire_ink(night)
        p.vline(bx - 1, base - v, base, edge)
        p.vline(bx + bw, base - v, base, edge)
        p.hline(bx, bx + bw, base - v - 1, edge)

    def peak_mark(self, p, x, y, night):
        """A gold star beside the busiest week's count, on whichever side is clear."""
        if p.clear_of_words(x - 2, y - 3, x + 7, y + 5):
            A.star5(p, x - 1, y - 2, 7, "gold", night)
        else:
            A.star5(p, p.words[-1][0] - 9, y - 2, 7, "gold", night)

    def dial_ring(self, p, arc, night):
        """The upper half of a clock's face, its hours the dial's ticks, set a little outside the dial's radius
        so its figures sit clear inside it."""
        (x0, cy), (x1, _) = arc[0], arc[-1]
        cx, r = round((x0 + x1) / 2), round((x1 - x0) / 2 + 1.5)
        A.clock_ring(p, cx, round(cy), r - 5, r + 3, night)

    def dial_tick(self, p, x, y, night):
        """No tick of its own: the clock's face carries its hours."""

    def dial_hub(self, p, cx, cy, night):
        """A gold boss at the hub, and a gold star at the tip of the hand, the hand's farthest pixel."""
        accent = self.ink(night)["accent"]
        hand = [q for q, c in p.layers["base"].items()
                if c == accent and abs(q[0] - cx) <= 40 and cy - 40 <= q[1] <= cy]
        if hand:
            tx, ty = max(hand, key=lambda q: (q[0] - cx) ** 2 + (q[1] - cy) ** 2)
            A.star5(p, tx - 2, ty - 2, 5, "gold", night)
        G = RAMP["gold"]
        for (dx, dy, t) in ((0, 0, 6), (-1, 0, 5), (1, 0, 4), (0, -1, 5), (0, 1, 3)):
            p.px(cx + dx, cy + dy - 1, G[t])

    def material(self, i, xx, yy, y0, y1, lift, night):
        """Cloths for a Juneteenth dress by turns: the flag's blue, the flag's red, a woven stripe of red, gold
        and green, and white linen, each lit along its top."""
        B, R, G, Gd, Ln = (RAMP[n] for n in ("blue", "red", "green", "gold", "linen"))
        kind = i % 4
        if kind == 0:
            c = B[4] if (xx + yy) % 4 else B[3]
        elif kind == 1:
            c = R[4] if (xx + yy) % 4 else R[3]
        elif kind == 2:
            c = (R[4], Gd[4], G[4])[(xx // 2) % 3] if (yy - y0) % 4 != 3 else Gd[3]
        else:
            c = Ln[5] if ((xx + yy) // 3) % 2 == 0 else Ln[4]
        return step(c, lift)

    def counter_cell(self, q, ox, oy, night):
        """One counter's tile on a flip clock, 11 by 15, in the flag's deep blue: its upper leaf a shade lighter
        than its lower, split by the hinge across its middle, lit along its top edge."""
        B, K = RAMP["blue"], RAMP["coal"]
        for yy in range(15):
            for xx in range(11):
                c = B[1] if yy < 7 else B[0]
                if yy == 0:
                    c = B[3]
                if yy == 7:
                    c = K[0]
                if xx == 10 or yy == 14:
                    c = K[1]
                q.px(ox + xx, oy + yy, c)
        q.px(ox, oy + 7, RAMP["gold"][4])
        q.px(ox + 9, oy + 7, RAMP["gold"][4])

    def counter_ink(self, night, dim):
        return RAMP["blue"][3] if dim else RAMP["linen"][6]

    def timeline_line(self, p, x0, x1, y, night):
        """The cord the releases hang from, as the garland's: pale, lit along its top, darker underneath."""
        Ln = RAMP["linen"]
        k = -1 if night else 0
        for x in range(x0, x1):
            p.px(x, y, Ln[5 + k] if x % 4 else Ln[6 + k])
            p.px(x, y + 1, Ln[3 + k])

    def release(self, p, x, gy, kind, night, i=0):
        """A release hanging from the cord like a flag on the garland: a little Juneteenth flag, a bigger one
        for a big release, a gold bead for a patch, a flag drawn in outline for one still to come, not yet
        raised, and for the repository's creation a new gold star."""
        hook = RAMP["linen"][2 if night else 3]
        if kind == "minor":
            G = RAMP["gold"]
            p.px(x, gy + 2, hook)
            p.px(x, gy + 3, G[5])
            p.px(x + 1, gy + 3, G[3])
            return
        p.px(x + 1, gy + 2, hook)
        if kind == "big":
            A.juneteenth_flag(p, x - 5, gy + 3, 13, 9, False, motion=False)
        elif kind == "major":
            for (a, b), c in A.mini_flag_cells(False).items():
                p.px(x - 2 + a, gy + 3 + b, c)
        elif kind == "made":
            A.star5(p, x - 1, gy + 3, 5, "gold", night)
        else:
            p.box(x - 2, gy + 3, 7, 5, self.ink(night)["muted"])

    def today_mark(self, p, x, y, night):
        A.sparkle(p, x + 2, y, big=True, warm=True)

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor as a celebration pin in their colour, their initials on it; a bot as a silver pin with
        the icon the kit draws for it."""
        if not person.get("initials"):
            icon = GLYPHS[7].get(person.get("icon") or "package", GLYPHS[7]["package"])
            A.pin(p, cx, cy, "silver", 4, night, icon=icon)
            return
        fam, face, letters = PINS[i % len(PINS)]
        A.pin(p, cx, cy, fam, face, night, initials=str(person["initials"])[:2], letters=letters)

    def commit_bar(self, p, x, y, w, fill, night):
        """A contributor's share, striped in the flag's blue and red."""
        B, R = RAMP["blue"], RAMP["red"]
        p.box(x, y, w + 2, 4, self.wire_ink(night))
        for xx in range(fill):
            blue = (xx // 2) % 2 == 0
            p.px(x + 1 + xx, y + 1, B[5] if blue else R[5])
            p.px(x + 1 + xx, y + 2, B[3] if blue else R[3])

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """The flag's star round the seal: a ring blue above and red below a white arc, in the white outline
        of a bursting nova of twelve points."""
        A.nova_seal(p, cx, cy, r0, night)

    def placard_board(self, p, night):
        """A Juneteenth card: the red, black and green ribbon round it, little flags along its top and a gold
        star at its foot, on the paper or the night sky."""
        A.paper(p, night, 3, 5, p.w - 6, p.h - 8, uid="pl")
        if night:
            A.stars(p, 8, 10, p.w - 8, p.h - 32, 24, seed=9, twinkling=False, faint=True)
        A.tricolor_frame(p, night, 0, 2, p.w, p.h - 4, uid="plq")
        A.flag_garland(p, 90, 170, 5, 40, 3, night)
        A.star5(p, p.w - 18, p.h - 34, 7, "gold", night)

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """Confetti along the badge's top, kept inside its shape: squares and strips two rows deep, red, white,
        gold, blue and green by turns, some face up and some turned, a pixel or two apart."""
        fams = ("red", "linen", "gold", "blue", "green", "linen")
        x, i = 1 + seed % 2, 0
        while x < w - 2:
            R = RAMP[fams[(i + seed) % len(fams)]]
            lit, dark = (R[6], R[4]) if R is RAMP["linen"] else (R[5], R[3])
            shape = (((0, 0, lit), (1, 0, dark)) if i % 3 == 0 else
                     ((0, 1, lit), (1, 1, lit)) if i % 3 == 1 else ((0, 0, dark), (0, 1, lit)))
            for (dx, dy, c) in shape:
                if inside(x + dx, dy, w, s["h"], s["corner"]):
                    p.px(x + dx, dy, c)
            x += 3 + (1 if (i * 7 + seed) % 3 == 0 else 0)
            i += 1

    def badge_label(self):
        return (RAMP["blue"][1], C["white"])

    def badge_gold(self):
        return (RAMP["gold"][4], C["coal"])

    def badge_states(self):
        # Yellow is the gold of a June sun, as the label is, with dark letters.
        return {"green": (RAMP["green"][2], C["white"]), "yellow": (RAMP["gold"][4], C["coal"]),
                "red": (RAMP["red"][3], C["white"]), "slate": (C["slate"], C["white"])}

    def badge_swatches(self):
        # The approved palette row (blue, red, green, gold, linen, confetti and starlight), and for the families
        # it leaves out the flag's lit red for orange, a violet, brick, a dusk, a slate grey and an oak brown.
        return {"blue": (RAMP["blue"][3], C["white"], None), "red": (RAMP["red"][3], C["white"], None),
                "green": (RAMP["green"][3], C["white"], None), "gold": (RAMP["gold"][4], C["coal"], None),
                "linen": (RAMP["linen"][5], C["ink"], "outline"),
                "confetti": (RAMP["blue"][2], C["white"], "confetti"),
                "starlight": (RAMP["dusk"][1], C["white"], "stars"),
                "ember": (RAMP["red"][4], C["white"], None), "violet": (X["violet"], C["white"], None),
                "brick": (RAMP["brick"][4], C["white"], None), "dusk": (RAMP["dusk"][5], C["white"], None),
                "slate": (C["slate"], C["white"], None), "oak": (RAMP["oak"][3], C["white"], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        if y in text_rows:
            return c
        if pattern == "confetti" and (x * 5 + y * 11) % 13 == 0:
            return (RAMP["gold"][5], RAMP["red"][5], RAMP["green"][5])[(x + y) % 3]
        if pattern == "stars" and (x * 7 + y * 13) % 23 == 0:
            return C["white"] if (x + y) % 2 else RAMP["gold"][5]
        return c

    def badge_outline(self, pattern):
        return RAMP["blue"][3] if pattern == "outline" else None

    def badge_shine(self, c, y, h):
        """Plastic's foot shaded a step; the confetti along its top stands for its gloss."""
        try:
            return step(c, -1) if y == h - 1 else c
        except KeyError:
            return c

    def plate_colours(self, mode):
        B, Gd, Ln = RAMP["blue"], RAMP["gold"], RAMP["linen"]
        if mode == "day":
            return dict(paper=C["paper"], dot=C["grid"], frame=B[3], block=B[3], ink=C["ink"], letters=C["white"])
        if mode == "night":
            return dict(paper=RAMP["dusk"][1], dot=C["grid_n"], frame=Gd[4], block=Gd[4], ink=X["body_night"],
                        letters=C["ink"])
        return dict(paper=Ln[4], dot=Ln[3], frame=C["coal"], edge=Ln[3], ink=C["coal"])

    def plate_edge(self, block):
        return step(block, -1)


SET = Juneteenth()
