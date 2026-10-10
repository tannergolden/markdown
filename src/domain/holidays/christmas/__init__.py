# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Christmas set: a snowy winter sheet under a string of lights.

Titles wear a cap of snow; a rod striped like a candy cane frames every sheet
and a string of lights twinkles across the top. Headers stand in the snow: a
lit fir hung with baubles, a snowman, presents and a candy cane, with snow
falling at two depths and, by night, a crescent moon. Snow rests on every
rule and along the top two rows of every badge. By day the paper is ice with
a dot grid; by night a winter sky with its stars.
"""
from __future__ import annotations

import math
import random

from ..designs import NARROW, WIDE, Holiday
from ..designs.badges import inside
from ..pixel import LX, LZ, Pix, sphere, tube
from . import art as A
from .palette import BULBS, C, NIGHT_SKY, RAMP, TOKENS, X, near, step

LINK_SPRITES = ("gift", "star", "tree", "bell")
# The glass a release's bauble is blown in, by turns; the ribbons a schematic's cards are tied with; and the
# baubles a contributor's avatar is, under a Santa hat. Each is the name of a ramp.
BAUBLES = ("red", "gold", "cyan", "pink", "silver")
RIBBONS = ("red", "gold", "red")
AVATARS = ("red", "gold", "pine")
SHEET_RULE = 20   # the row an element's sheet rules off its tag and title at


class Christmas(Holiday):
    key = "christmas"
    name = "Christmas"
    tokens = frozenset(TOKENS)

    # ---- colour and paper
    def ink(self, night):
        return dict(
            title=C["gold3"] if night else C["pine1"], shadow=C["red1"] if night else C["red2"],
            body=C["snow"] if night else C["pine0"], muted=C["snow3"] if night else X["muted_day"],
            rule=C["pine4"] if night else C["pine2"], accent=RAMP["red"][5] if night else C["red2"],
            tag=C["red2"], tag_ink=C["white"],
            fill=C["pine1"] if night else C["white"], dim=X["dim_night"] if night else C["snow2"],
        )

    def lit(self, night):
        """A bevel down the title's left edges and along its foot, and by night a gold glow."""
        if night:
            return dict(bevel=(RAMP["gold"][5], RAMP["gold"][2]), glow=(C["gold3"], (0.18,)), night=True)
        return dict(bevel=(RAMP["pine"][3], RAMP["pine"][0]), night=False)

    def paper(self, p, night, uid="p"):
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        if not night:
            return C["ice"]
        return NIGHT_SKY[min(len(NIGHT_SKY) - 1, int(y * len(NIGHT_SKY) / p.h))]

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        A.stars(p, x0, y0, x1, y1, n, seed=seed, twinkling=twinkling, faint=faint, avoid=avoid)

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The paper, or by night the sky and its stars; and across a wide header snow falling at two
        depths, fewer flakes on a short strip. A drawing made lighter to fit its budget keeps half the
        flakes behind it and none in front. The file holds them still when the header does (see
        `art.fall`); a phone's header has none."""
        super().sky(p, night, y1, seed=seed, motion=motion, avoid=avoid)
        if p.w == WIDE:
            flakes = (36 if y1 < 80 else 60) // (2 if p.lite else 1)
            A.fall(p, 4, 4, p.w - 4, y1, flakes, night, seed=seed + 20, avoid=avoid, near=not p.lite)

    def frame(self, p, night, webs=False):
        A.candy_frame(p, night)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """A string of lights, a bulb every nine pixels as the set hangs them."""
        A.lights(p, x0, x1, y, sag=sag, span=span, spacing=9, night=night, seed=seed)

    def tag(self, p, x, y, w, h, night):
        """The holly-red block a tag's white letters sit on: lit along its top, shaded along its foot."""
        R = RAMP["red"]
        p.rect(x, y, w, h, C["red2"])
        p.hline(x, x + w, y, R[4])
        p.hline(x, x + w, y + h - 1, R[1])

    def title_text(self, p, x, y, s, night, scale):
        """Bevelled letters with snow settled on them, lit by the theme."""
        k = self.ink(night)
        return p.text(x, y, s, k["title"], "57", scale, shadow=k["shadow"], finish=A.snow_on_letters(night),
                      **self.lit(night))

    # ---- the headers' scenes
    def section_mark(self, p, x, y, night):
        A.holly(p, x, y - 2)

    def strip_mark(self, p, x, y, night):
        A.holly(p, x - 1, y - 4)

    def scene(self, design, p, rule, night, motion):
        """H1: a lit fir on the left, a snowman and presents on the right, the moon by night; H2: a tall
        fir over its presents on a bank of snow; H3: a small fir and a candy cane. A lit tree pools its
        light on the snow by night, and by day what stands in the snow casts a shadow (see `finish`)."""
        if design == "H1":
            if night and p.clear_of_words(57, 17, 88, 48):     # the moon, with room round it
                A.moon(p, 72, 32, 7)
            A.tree(p, 34, rule, 46, night, seed=3)
            if p.clear_of_words(354, rule - 31, 377, rule):
                A.snowman(p, 355, rule - 30, night)
            A.gift(p, 381, rule - 11, 11, 10, "red", "gold")
            A.gift(p, 396, rule - 7, 9, 6, "pine", "red")
            p.lamps.append(("pool", 34.5, rule - 0.5, 34, 4.5) if night else ("shadow", 360, 392, rule - 0.5))
            return [(31, 38)]
        if design == "H2":
            A.tree(p, 356, rule, 86, night, seed=9)
            A.gift(p, 317, rule - 12, 14, 11, "red", "gold")
            A.gift(p, 379, rule - 7, 10, 6, "pine", "red")
            A.gift(p, 393, rule - 10, 12, 9, "gold", "red")
            A.snowbank(p, 312, 409, rule - 3, rule, seed=3, night=night)
            p.lamps.append(("pool", 356.5, rule - 1.5, 52, 5.5) if night else ("shadow", 330, 409, rule - 1.5))
            return [(312, 409)]
        A.tree(p, 392, rule, 28, night, seed=13)
        A.candy(p, 366, rule - 16, 16)
        return []

    def scene_narrow(self, design, p, y, night):
        if design == "H1":
            A.tree(p, 22, y, 30, night, seed=8)
            A.snowman(p, NARROW - 32, y - 30, night)
        elif design == "H2":
            if p.clear_of_words(139, y - 32, 175, y + 8):
                A.tree(p, 160, y + 7, 36, night, seed=11)
        elif p.clear_of_words(149, y - 26, 172, y + 2):
            A.tree(p, 160, y + 1, 26, night, seed=14)

    def rule_decor(self, p, x0, x1, y, seed, night):
        """Snow resting on a rule, icicles hanging under it; on a header's rule a few glints that twinkle
        where no word is near. A sheet's own rule, under its tag and title, has none."""
        sheet = y <= SHEET_RULE
        A.snowcap(p, x0, x1, y, seed=seed, night=night, icicles=0.25 if sheet else 0.3,
                  glints=0.0 if sheet else 1.0, reach=2)

    def finish(self, p, night):
        """The last pass, over the snow the scene stands in: a lit tree's light pooled round its foot by
        night, and by day the shadow the presents and the snowman cast."""
        for kind, *at in p.lamps:
            if kind == "pool":
                A.light_pool(p, *at, night)
            elif kind == "shadow":
                A.ground_shadow(p, *at, night)

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        A.holly(p, x - 2, y - 3)

    def heart(self, p, x, y):
        A.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        """A stick of candy lying flat, striped red and white on the diagonal."""
        A.candy_bar(p, x0, y0, w, h, period)

    def link_colours(self, night):
        if night:
            return C["pine1"], C["pine4"], C["white"], RAMP["pine"][2]
        return C["white"], C["pine2"], C["pine1"], RAMP["pine"][0]

    def link_top(self, p, x0, x1, y, seed, night):
        if night:
            p.hline(x0, x1, y + 1, RAMP["pine"][3])
        A.snowcap(p, x0, x1, y, seed=seed, night=night)

    def link_icon(self, index, night, ink):
        return A.ICONS[LINK_SPRITES[index % len(LINK_SPRITES)]], A.icon_pal(night, ink)

    # ---- the elements
    def card_bevel(self, night):
        return (RAMP["pine"][3], RAMP["pine"][0]) if night else (C["white"], RAMP["snow"][3])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A card wrapped as a present: a ribbon down its icon cell's edge, a bow on its lid and snow on
        the lid beside it."""
        Rb = RAMP[RIBBONS[seed % len(RIBBONS)]]
        for yy in range(y + 1, y + h - 1):
            for i, t in enumerate((5, 4, 2)):
                p.px(x + 10 + i, yy, Rb[t])
        A.bow(p, x + 7, y - 3, "m", Rb)
        A.snowcap(p, x + 17, x + w - 2, y, seed=x + y, night=night)

    def wire_ink(self, night):
        return C["snow2"] if night else C["pine0"]

    def wire_lights(self, p, cells, night, seed):
        """A string of lights along the wire, a bulb every ninth pixel in each colour of glass by turns."""
        for i, (x, y, d) in enumerate(cells[5:-7]):
            if i % 9 == 0:
                A.wire_bulb(p, x, y, d, BULBS[(i // 9 + seed) % len(BULBS)], night)

    def dashes(self, night):
        return [C["red3"] if night else C["red2"], C["white"] if night else C["snow3"]]

    def ornament(self, kind, p, x, y, night):
        """A small lit fir in a free corner of the schematic."""
        if kind == "schematic":
            if p is not None:
                A.tree(p, x + 10, y + 26, 24, night, seed=5)
            return (21, 26)
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as a stick of candy stood on end, striped on the diagonal and lit from the left."""
        R, S = RAMP["red"], RAMP["snow"]
        for xx in range(bx, bx + bw):
            nx = 2 * (xx - bx + 0.5) / bw - 1
            lam = max(0.0, nx * LX + math.sqrt(1 - nx * nx) * LZ)
            for yy in range(base - v, base):
                if ((xx + yy) // 3) % 2 == 0:
                    p.px(xx, yy, R[max(2, min(5, round(1.7 + 3.6 * lam)))])
                else:
                    p.px(xx, yy, S[max(2, min(6, round(2.6 + 4.0 * lam)))])
        p.box(bx - 1, base - v - 1, bw + 2, v + 1, self.wire_ink(night))

    def peak_mark(self, p, x, y, night):
        A.star(p, x + 2, y + 4, 2, glow=C["gold3"] if night else None, outline=None if night else RAMP["gold"][2])

    def dial_ring(self, p, arc, night):
        """A wreath bent into a half ring."""
        tube(p, arc, 3.0, A.needles(8), outline=RAMP["pine"][0])

    def dial_tick(self, p, x, y, night):
        A.berry(p, x - 1, y - 1)

    def dial_hub(self, p, cx, cy, night):
        """A brass hub on a red base."""
        sphere(p, cx + 0.5, cy - 0.5, 2.6, RAMP["gold"], lo=2)
        R = RAMP["red"]
        for i, xx in enumerate(range(cx - 4, cx + 5)):
            p.px(xx, cy + 2, R[4] if i < 3 else R[3] if i < 7 else R[2])

    def material(self, i, xx, yy, y0, y1, lift, night):
        """Wrapping papers by turns: candy stripes, pine checks, gold dots and snow."""
        kind = i % 4
        if kind == 0:
            c = C["red2"] if ((xx + yy) // 3) % 2 == 0 else RAMP["red"][5]
        elif kind == 1:
            c = RAMP["pine"][3] if (xx // 2 + yy // 2) % 2 else RAMP["pine"][2]
        elif kind == 2:
            c = RAMP["gold"][4] if (xx + yy) % 4 else RAMP["gold"][3]
        else:
            c = RAMP["snow"][6] if (xx + yy) % 5 else RAMP["snow"][3]
        return step(c, lift)

    def counter_cell(self, q, ox, oy, night):
        """An advent calendar's door: a raised panel framed in red with a brass knob, snow on its top."""
        light, dark = self.card_bevel(night)
        q.rect(ox, oy, 11, 15, self.ink(night)["fill"])
        q.bevel(ox + 1, oy + 1, 9, 13, light, dark)
        q.box(ox, oy, 11, 15, C["red3"] if night else C["red2"])
        q.px(ox + 8, oy + 8, RAMP["gold"][5])
        q.px(ox + 8, oy + 9, RAMP["gold"][2])
        A.snowcap(q, ox, ox + 11, oy, seed=0, night=night)

    def counter_ink(self, night, dim):
        """A door's digit, in a tone a hair off the text's own ink (its muted ink for a leading nought): a
        drawing sets all the letters of one ink together, where that ink is first used, so an ink of their
        own keeps the digits over the doors they are cut into."""
        if night:
            return RAMP["snow"][2] if dim else RAMP["snow"][5]
        return RAMP["green"][1] if dim else RAMP["pine"][1]

    def timeline_line(self, p, x0, x1, y, night):
        """The garland the releases hang from, up to today: a rope of pine needles. A stub too short to
        twist a rope from is left to the line it starts."""
        if x1 - x0 >= 3:
            tube(p, [(x0, y + 1.5), (x1, y + 1.5)], 1.75, A.needles(3, 1, 5))

    def release(self, p, x, gy, kind, night, i=0):
        """A bauble for a release, bigger for a big one; a bulb for a patch; for one still to come an
        empty bauble, outlined; for the repository's creation a present."""
        if kind in ("major", "big"):
            A.ornament(p, x - 3, gy - 1, BAUBLES[i % len(BAUBLES)], big=kind == "big")
        elif kind == "minor":
            A.bulb(p, x - 1, gy + 2, BULBS[i % len(BULBS)], "base", night)
        elif kind == "made":
            A.gift(p, x - 3, gy + 2, 7, 6, "red", "gold")
        else:
            art = ["...y...", "..yyy..", "..o.o..", ".o...o.", "o.....o", "o.....o", "o.....o", ".o...o.", "..o.o.."]
            p.sprite(x - 3, gy - 1, art, {"y": C["gold2"], "o": self.ink(night)["muted"]})

    def today_mark(self, p, x, y, night):
        """A star at the garland's tip."""
        A.star(p, x + 3, y + 1, 2, glow=C["gold3"], outline=None if night else RAMP["gold"][2])

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor: a bauble in their colour under a Santa hat, their initials on it; a bot is a slate
        bauble with a present on it and an aerial lit at its tip."""
        if not person.get("initials"):
            sphere(p, cx + 0.5, cy + 0.5, 7.2, RAMP["slate"], lo=1, hi=5)
            p.sprite(cx - 3, cy - 3, A.ICONS["gift"], A.icon_pal(True))
            p.vline(cx, cy - 10, cy - 7, RAMP["gold"][2])
            p.halo(cx + 0.5, cy - 10.5, 2.4, 2.4, C["gold3"], (0.2, 0.35))
            p.px(cx, cy - 11, RAMP["gold"][5])
            return
        name = AVATARS[i % len(AVATARS)]
        Rm = RAMP[name]
        sphere(p, cx + 0.5, cy + 0.5, 7.2, Rm, lo=1, hi=5)
        ini = str(person["initials"])[:2]
        if name == "gold":       # coal letters on the light bauble, white on the dark ones, each at 4.5:1
            p.text(cx - 3, cy - 1, ini, RAMP["coal"][1], "35")
        else:
            p.text(cx - 3, cy - 1, ini, C["white"], "35", shadow=Rm[1])
        A.santa_hat(p, cx - 6, cy - 17)

    def commit_bar(self, p, x, y, w, fill, night):
        """A contributor's share, striped like a candy cane."""
        p.box(x, y, w + 2, 4, self.wire_ink(night))
        for xx in range(fill):
            red = (xx // 2) % 2 == 0
            p.px(x + 1 + xx, y + 1, RAMP["red"][4] if red else C["white"])
            p.px(x + 1 + xx, y + 2, RAMP["red"][2] if red else X["frost_hi"])

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """A wreath round the seal, from r0 to r1: a ring of pine needles and berries set round it, its
        foot left for the bow."""
        rad = (r0 + r1) / 2 - 0.5
        ring = [(cx + rad * math.cos(math.radians(a)), cy + rad * math.sin(math.radians(a))) for a in range(0, 361, 4)]
        tube(p, ring, (r1 - r0) / 2 - 0.2, A.needles(3), outline=RAMP["pine"][0])
        for a in range(-90, 250, 30):
            if not 60 <= a <= 120:
                ang = math.radians(a)
                A.berry(p, cx + round(rad * math.cos(ang)) - 1, cy + round(rad * math.sin(ang)) - 1)

    def seal_mark(self, p, x, y, night):
        A.bow(p, x + 2, y, "l", RAMP["red"])

    def placard_board(self, p, night):
        """A wooden sign: planks with a grain, lit on their top-left faces, nailed at the corners, with
        snow along the top."""
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
            p.px(nx, ny, RAMP["coal"][4])
            p.px(nx + 1, ny, RAMP["coal"][2])
        A.snowcap(p, 1, w - 1, 2, seed=11, night=night)

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """Snow along the badge's top edge, kept inside its shape: drifts a row deep over a shaded row, in
        the night's colours on a night plate."""
        tmp = Pix(w, s["h"])
        A.snowcap(tmp, 1, w - 1, 1, seed=seed, night=night, cap=1)
        for (x, y), c in tmp.layers["base"].items():
            if inside(x, y, w, s["h"], s["corner"]):
                p.px(x, y, c)

    def badge_label(self):
        return (C["pine1"], C["white"])

    def badge_gold(self):
        return (C["gold2"], C["coal"])

    def badge_states(self):
        # Yellow is drawn in orange, so it stands apart from the gold label, with coal letters.
        return {"green": (C["pine2"], C["white"]), "yellow": (C["orange"], C["coal"]),
                "red": (C["red2"], C["white"]), "slate": (C["slate"], C["white"])}

    def badge_swatches(self):
        return {"holly": (C["red2"], C["white"], None), "candy": (C["red1"], C["white"], "candy"),
                "pine": (C["pine2"], C["white"], None), "gold": (C["gold2"], C["coal"], None),
                "snow": (C["white"], C["pine1"], "outline"), "night": (C["sky2"], C["white"], "stars"),
                "carrot": (C["orange"], C["coal"], None), "glass": (RAMP["cyan"][1], C["white"], None),
                "plum": (RAMP["pink"][1], C["white"], None), "slate": (C["slate"], C["white"], None),
                "wood": (RAMP["wood"][3], C["white"], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        if pattern == "candy" and ((x + y) // 3) % 2 == 0:
            return C["red2"]
        if pattern == "stars" and (x * 7 + y * 13) % 29 == 0 and y not in text_rows:
            return C["gold4"]
        return c

    def badge_outline(self, pattern):
        return C["snow3"] if pattern == "outline" else None

    def badge_shine(self, c, y, h):
        return near(c, 1) if y == 2 else near(c, -1) if y == h - 1 else c

    def plate_colours(self, mode):
        if mode == "day":
            return dict(paper=C["ice"], dot=C["grid"], frame=C["red2"], block=C["red2"], ink=C["pine1"],
                        letters=C["white"])
        if mode == "night":
            return dict(paper=C["sky1"], dot=C["grid_n"], frame=C["white"], block=C["white"], ink=C["white"],
                        letters=C["red2"])
        # A live plate's letters are a shade darker than the preview's coal, so they hold 4.5:1 on its gold dots too.
        return dict(paper=C["gold2"], dot=C["gold1"], frame=C["coal"], edge=RAMP["gold"][1], ink=RAMP["coal"][1])

    def plate_edge(self, block):
        return near(block, -1)


SET = Christmas()
