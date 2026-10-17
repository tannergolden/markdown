# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Birthday set: a party for the page's birthday, drawn in pixels for the day.

Titles are piped in strawberry frosting over a line of chocolate, with sprinkles on them; piped icing frames every
sheet, the shell border round a cake, and bunting is hung along the top, its middle pennants spelling HAPPY BIRTHDAY.
The headers stand on a tablecloth, and every one has the cake. H2, the kit's default, is the party: the cake on its
glass stand, a strawberry tier under a drip of cream with rosettes and strawberries on its ledge and a mint tier under
a drip of strawberry, its candles lit, presents stacked beside it, a donkey piñata hung over them and a paper fan
pinned up by the frame. H1 has the piñata over the presents on its left, the top one jumping open now and then in a
burst of sprinkles, and on its right the cake in one tier under a paper fan, a cupcake beside it; H3 the cake in one
tier with a present. Once a loop, in a moving file, a breath sweeps in, the flames bend away from it and go out, smoke
curls up from the wicks, and they are lit again. By day the paper is cream, dotted in the frostings' pastels; by night
the lights are off and the candles light the room.

The cake carries the page's age in gold number candles, as many figures as it has, up to 999, whenever the age is
known: always for a repository, and for a person who gives the year they were born. It is the age of the birthday the
set is handed (`age`), and the sample's when it is handed no day. A person who gives only a month and a day gets five
slim candles, and the page says nothing of how old they are.
"""
from __future__ import annotations

import copy
import datetime as dt

from .. import birthday
from ..holidays.designs import NARROW, Holiday
from ..holidays.designs.badges import inside
from ..holidays.designs.materials import Podium, Stuff
from . import art as A
from .palette import C, NIGHT_SKY, PASTELS, RAMP, TOKENS, X, step

S, CR, MI, LE, LI, SK, FL, PL = (RAMP[n] for n in ("strawberry", "cream", "mint", "lemon", "lilac", "sky", "flame",
                                                    "plum"))
SAMPLE_AGE = 3          # the age the sample's cake carries, as in the shared checks
HEAD_RULE = 20          # the row an element's head is ruled at, where the sprinkles lie sparser


class Birthday(Holiday):
    key = birthday.KEY
    name = birthday.NAME
    tokens = frozenset(TOKENS)
    age: int | None = SAMPLE_AGE

    def on(self, day: dt.date, age: int | None = None) -> "Birthday":
        """This set drawing the birthday on `day`, turning `age`, or with no age when none is known."""
        held = copy.copy(self)
        held.day, held.age = day, age
        return held

    # ---- colour and paper
    def ink(self, night):
        """The set's colours. `shadow` is what a check mark's shadow takes; a title's own is in `title_text`."""
        return dict(
            title=S[5] if night else S[1],
            shadow=PL[1] if night else RAMP["cocoa"][3],
            body=X["body_night"] if night else C["ink"], muted=X["muted_night"] if night else X["muted_day"],
            rule=X["night_rule"] if night else X["rule_day"], accent=S[5] if night else X["accent_day"],
            tag=S[2], tag_ink=C["white"],
            fill=X["node_night"] if night else C["white"], dim=X["dim_night"] if night else X["dim_day"],
        )

    def lit(self, night):
        """Strawberry frosting over the letters, a tone lighter by night so it reads in the dark, and by night the
        candles' glow round them. By day `title_text` pipes a chocolate edge round them and a shadow under them
        first."""
        return dict(paint=A.FROSTING, night=night, glow=(FL[4], (0.16,)) if night else None)

    def paper(self, p, night, uid="p"):
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        if not night:
            return C["paper"]
        return NIGHT_SKY[min(len(NIGHT_SKY) - 1, int(y * len(NIGHT_SKY) / p.h))]

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        A.stars(p, x0, y0, x1, y1, n, seed=seed, twinkling=twinkling, faint=faint, avoid=avoid)

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The paper, or by night the dark room with a light for every 14 units across (half as many on a drawing
        made lighter), twinkling if it moves, kept out of the boxes the words take."""
        self.paper(p, night)
        if night:
            self.stars(p, 6, 20, p.w - 6, int(y1 * 0.7), n=p.w // (28 if p.lite else 14), seed=seed,
                       twinkling=motion, avoid=avoid)

    def frame(self, p, night, webs=False):
        A.icing_frame(p, night)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """Bunting along the top, a swag every 41 units on a wide sheet and 34 on a phone, its middle spelling HAPPY
        BIRTHDAY wherever there is room for it."""
        A.bunting(p, x0, x1, y, night, seed=seed, span=span, sag=sag)

    def tag(self, p, x, y, w, h, night):
        """The raspberry block a tag's white letters sit on: lit along its top, shaded along its foot."""
        p.rect(x, y, w, h, S[2])
        p.hline(x, x + w, y, S[3])
        p.hline(x, x + w, y + h - 1, S[1])

    def title_text(self, p, x, y, s, night, scale):
        """Letters piped in strawberry frosting: by day over a chocolate edge with a shadow under them, by night
        alone, lit by the candles; and on letters big enough to carry them, a few sprinkles (a drawing made lighter
        goes without)."""
        k = self.ink(night)
        if not night:
            A.edged(p, x, y, s, scale, shadow=RAMP["cocoa"][4], edge=RAMP["cocoa"][1])
        return p.text(x, y, s, k["title"], "57", scale, finish=A.title_sprinkles if scale >= 3 else None,
                      **self.lit(night))

    # ---- the headers' scenes
    def section_mark(self, p, x, y, night):
        """A little candle burning, after SECTION A-A."""
        x0, wy = A.slim_candle(p, x, y + 1, 5, "sky", night)
        A.little_flame(p, x0, wy, night)

    def strip_mark(self, p, x, y, night):
        A.cupcake(p, x + 4, y + 1, "lilac", "strawberry", night, "cherry")

    def scene(self, design, p, rule, night, motion):
        """The party each header stands on (see `_presents`, `_cake` and `_little_cake`)."""
        if design == "H1":
            return self._presents(p, rule, night, motion)
        if design == "H2":
            return self._cake(p, rule, night, motion)
        return self._little_cake(p, rule, night, motion)

    def _presents(self, p, rule, night, motion):
        """H1: on the left a donkey piñata hung over three presents stacked, the top one jumping open now and then in
        a burst of sprinkles; on the right a paper fan pinned over the cake, its candles lit, and a cupcake beside it.
        Where the words leave the cake no room, a cupcake with a candle burning stands in for it."""
        base = rule - 1
        A.tablecloth(p, 5, 62, base, night, seed=2)
        A.tablecloth(p, 352, 411, base, night, seed=6)
        if p.clear_of_words(10, 22, 44, 47):
            A.pinata(p, 12, 25, night, L=A.bobbing(p, motion, "bob1", (0, 0, 1, 1, 0, 0, 0, 1), dur=4.4))
        if p.clear_of_words(385, 21, 406, 42):
            A.paper_fan(p, 395, 31, 8, "lilac", night)
        A.surprise(p, 10, base, night, motion)
        if p.clear_of_words(352, base - 18, 364, base):
            A.cupcake(p, 358, base, "lemon", "mint", night, "cherry")
            A.contact(p, 358, base, 5)
        if p.clear_of_words(365, base - 46, 408, base):
            wicks = A.cake(p, 387, base, night, motion, self._age(), tiers=1)
            A.contact(p, 387, base, 8)
            A.light_pool(p, 387, base, 26, 3, night)
            A.blown(p, wicks, night, motion)
        else:
            wick = A.cupcake(p, 394, base, "sky", "strawberry", night, "candle")
            A.flame(p, *wick, night, motion=motion, phase=1)
            A.contact(p, 394, base, 5)
        A.contact(p, 23, base, 14)
        return [(5, 62), (352, 411)]

    def _cake(self, p, rule, night, motion):
        """H2: the cake on its glass stand with its candles lit, presents stacked on its left and a cupcake on its
        right, a donkey piñata hung over the presents and a paper fan pinned up by the frame; in a moving file a
        breath blows the candles out once a loop."""
        base = rule - 1
        A.tablecloth(p, 310, 411, base, night, seed=4)
        if p.clear_of_words(311, 20, 346, 48):
            A.pinata(p, 313, 26, night, L=A.bobbing(p, motion, "bob1", (0, 0, 1, 1, 0, 0, 0, 1), dur=4.4))
        if p.clear_of_words(390, 18, 411, 39):
            A.paper_fan(p, 400, 28, 8, "sky", night)
        A.present(p, 314, base, 20, 14, "sky", "strawberry", night, wrap="dots", bow=False)
        A.present(p, 317, base - 14, 14, 10, "lemon", "lilac", night, wrap="stripes")
        wicks = A.cake(p, 367, base, night, motion, self._age())
        A.cupcake(p, 404, base, "mint", "strawberry", night, "cherry")
        for (sx, sr) in ((324, 11), (367, 9), (404, 5)):
            A.contact(p, sx, base, sr)
        A.light_pool(p, 367, base, 36, 3, night)
        A.blown(p, wicks, night, motion)
        return [(310, 411)]

    def _little_cake(self, p, rule, night, motion):
        """H3: the cake on its stand, its candles lit, and a present beside it; in a moving file a breath blows the
        candles out once a loop."""
        base = rule - 1
        A.tablecloth(p, 350, 411, base, night, seed=5)
        A.present(p, 354, base, 11, 9, "lilac", "strawberry", night, wrap="stripes")
        wicks = A.cake(p, 388, base, night, motion, self._age(), tiers=1)
        for (sx, sr) in ((359, 6), (388, 8)):
            A.contact(p, sx, base, sr)
        A.light_pool(p, 388, base, 26, 3, night)
        A.blown(p, wicks, night, motion)
        return [(350, 411)]

    def _age(self):
        """The age the cake carries: the birthday's when it is known, the sample's when the set is told no day."""
        return self.age if self.day else SAMPLE_AGE

    def scene_narrow(self, design, p, y, night):
        """On a phone: H1's presents and two cupcakes on the rule at `y`; H2's paper fan by the title, and a slice
        of cake that stands on the figures' rule once it is drawn (see `rule_decor`); H3's cupcake beside the
        title. Each stands only where the words leave it room."""
        if design == "H1":
            base = y - 1
            A.tablecloth(p, 5, 42, base, night, seed=7)
            A.tablecloth(p, 138, NARROW - 4, base, night, seed=9)
            if p.clear_of_words(7, y - 24, 38, y):
                A.present(p, 9, base, 14, 10, "mint", "strawberry", night, wrap="dots", bow=False)
                A.present(p, 11, base - 10, 10, 7, "lemon", "lilac", night, wrap="stripes")
                A.contact(p, 16, base, 8)
            if p.clear_of_words(142, y - 22, NARROW - 6, y):
                wick = A.cupcake(p, 150, base, "sky", "strawberry", night, "candle")
                A.flame(p, *wick, night, motion=False)
                A.cupcake(p, 165, base, "lemon", "mint", night, "cherry")
                A.contact(p, 150, base, 5)
                A.contact(p, 165, base, 5)
        elif design == "H2":
            if p.clear_of_words(NARROW - 22, y - 16, NARROW - 6, y + 2):
                A.paper_fan(p, NARROW - 14, y - 7, 7, "sky", night)
            p.treat = True
        else:
            sy = max(y - 4, 30)
            if p.clear_of_words(152, sy - 18, NARROW - 6, sy + 2):
                A.cupcake(p, 162, sy, "lilac", "strawberry", night, "cherry")

    def rule_decor(self, p, x0, x1, y, seed, night):
        """Sprinkles lying along a rule, sparser along an element's head; a phone's H2 has a slice of cake stand on
        the figures' rule first."""
        if getattr(p, "treat", False):
            p.treat = False
            if p.clear_of_words(148, y - 15, 172, y):
                A.cake_slice(p, 149, y - 14, night)
        A.sprinkles_on(p, x0, x1, y, seed=seed, night=night, gap=(5, 14) if y == HEAD_RULE else (3, 9))

    def finish(self, p, night):
        A.lamplight(p, night)

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        """A cupcake at the end of the notes: on a wide block it stands on the frame's inner rule; on a phone's it
        sits up by the notes' label."""
        if p.w > NARROW:
            A.cupcake(p, x + 6, p.h - 4, "lilac", "strawberry", night, "cherry")
        else:
            A.cupcake(p, x + 8, y + 9, "lilac", "strawberry", night, "cherry")

    def heart(self, p, x, y):
        A.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        A.stripe_bar(p, x0, y0, w, h, period)

    def link_colours(self, night):
        if night:
            return X["node_night"], X["night_rule"], X["body_night"], PL[2]
        return C["white"], X["rule_day"], C["ink"], X["dim_day"]

    def link_top(self, p, x0, x1, y, seed, night):
        """A line of piped strawberry along the button's top edge, a bead every three pixels and a sprinkle in it
        here and there."""
        k = A.dim(night)
        for xx in range(x0 - 1, x1 + 1):
            p.px(xx, y, S[5 + k] if (xx + seed) % 3 == 0 else S[4 + k])
            p.px(xx, y + 1, S[3 + k] if (xx + seed) % 7 else A.sprinkle_colour(PASTELS[(xx // 7) % 5], night))

    def link_icon(self, index, night, ink):
        return A.ICONS[A.LINK_ICONS[index % len(A.LINK_ICONS)]], A.icon_pal(night)

    # ---- the elements
    def card_bevel(self, night):
        return (PL[3], PL[0]) if night else (C["white"], X["dim_day"])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A bead of piped strawberry down the icon cell's edge, a sprinkle in it here and there, a candle on the lid
        and sprinkles along it."""
        k = A.dim(night)
        for yy in range(y + 1, y + h - 1):
            p.px(x + 10, yy, S[(5 if (yy - y) % 3 == 1 else 4) + k])
            p.px(x + 11, yy, S[3 + k] if (yy - y) % 6 != 4 else A.sprinkle_colour(PASTELS[(yy + seed) % 5], night))
        if lid:
            wx, wy = A.slim_candle(p, x + 8, y - 6, 5, "sky", night)
            A.little_flame(p, wx, wy, night)
        A.sprinkles_on(p, x + (15 if lid else 3), x + w - 2, y, seed=x + y, night=night, gap=(5, 14))

    def wire_ink(self, night):
        return CR[4] if night else self.ink(night)["body"]

    def wire_lights(self, p, cells, night, seed):
        """Little pennants hung along a wire where it runs level, one every seventh pixel, in the frostings'
        colours by turns."""
        run = sorted((x, y) for (x, y, d) in cells[4:-6] if d == "h")
        k = A.dim(night)
        for i, (x, y) in enumerate(run[::7]):
            R = RAMP[PASTELS[(i + seed) % len(PASTELS)]]
            for j, wd in enumerate((3, 1)):
                for ii in range(wd):
                    p.px(x - wd // 2 + ii, y + 1 + j, R[(5 if ii == 0 else 4) + k])

    def dashes(self, night):
        return [S[4 if night else 3], X["muted_night"] if night else X["muted_day"]]

    def ornament(self, kind, p, x, y, night):
        if kind == "schematic":
            if p is not None:
                A.cake_slice(p, x, y, night)
            return A.SLICE
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        A.candle_bar(p, bx, base, bw, v, night)

    def peak_mark(self, p, x, y, night):
        A.little_flame(p, x, y + 1, night)

    def dial_ring(self, p, arc, night):
        A.piped_ring(p, arc, night)

    def dial_tick(self, p, x, y, night):
        p.px(x, y, A.sprinkle_colour(PASTELS[(x + y) % len(PASTELS)], night))

    def dial_hub(self, p, cx, cy, night):
        """A cherry the hand turns on."""
        A.sphere(p, cx - 0.5, cy - 0.5, 1.8, RAMP["cherry"], lo=2, hi=6)

    def material(self, i, xx, yy, y0, y1, lift, night):
        return A.wrapping(i, xx, yy, y0, lift, night)

    def counter_cell(self, q, ox, oy, night):
        A.gift_cell(q, ox, oy, night)

    def counter_ink(self, night, dim):
        if night:
            return PL[5] if dim else X["body_night"]
        return RAMP["cream"][2] if dim else C["ink"]

    def timeline_line(self, p, x0, x1, y, night):
        """The bunting's twine the releases hang from, up to today."""
        p.hline(x0, x1, y, CR[3] if night else RAMP["cocoa"][4])

    def release(self, p, x, gy, kind, night, i=0):
        A.release(p, x, gy, kind, night, i, unlit=self.ink(night)["muted"])

    def today_mark(self, p, x, y, night):
        A.sparkle(p, x + 2, y, big=True, warm=True)

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor as a sugar cookie iced in their colour with their initials piped on it; a bot as a little
        wind-up robot."""
        if not person.get("initials"):
            A.toy_robot(p, cx, cy, night)
            return
        fam = ("strawberry", "mint", "lemon")[i % 3]
        A.cookie(p, cx, cy, fam, str(person["initials"])[:2], night, C["ink"])

    def commit_bar(self, p, x, y, w, fill, night):
        A.ribbon_bar(p, x, y, w, fill, night, self.wire_ink(night))

    def rosette(self, p, cx, cy, r0, r1, n, night):
        A.frosted_seal(p, cx, cy, r0 + 2, night)

    def seal_mark(self, p, x, y, night):
        wx, wy = A.slim_candle(p, x + 6, y + 2, 4, "sky", night)
        A.little_flame(p, wx, wy, night)

    def placard_board(self, p, night):
        """A party's sign: piped icing round the card and bunting along its top."""
        A.paper(p, night, 3, 5, p.w - 6, p.h - 8, uid="pl")
        if night:
            A.stars(p, 8, 10, p.w - 8, p.h - 32, 24, seed=9, twinkling=False, faint=True)
        A.icing_frame(p, night, 0, 2, p.w, p.h - 4, uid="plq")
        A.bunting(p, 90, 170, 5, night, span=40, sag=4, greet=False)

    def placard(self, d, night):
        """The placard, and a cupcake standing at its foot where the description leaves it room."""
        p = super().placard(d, night)
        if p.clear_of_words(181, 50, 193, 68):
            A.cupcake(p, 187, 67, "lilac", "strawberry", night, "cherry")
        return p

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """Sprinkles along the badge's top two rows, kept inside its shape: rods of two pixels and nonpareils in the
        frostings' colours by turns, a pixel or two apart."""
        x, i = 1 + seed % 2, 0
        while x < w - 2:
            fam = A.SPRINKLE_FAMS[(i + seed) % len(A.SPRINKLE_FAMS)]
            lit, dark = A.sprinkle_colour(fam, False, True), A.sprinkle_colour(fam, False, False)
            shape = (((0, 0, lit), (1, 0, dark)) if i % 3 == 0 else ((0, 1, lit), (1, 1, dark)) if i % 3 == 1
                     else ((0, 0, lit), (0, 1, dark)))
            for (dx, dy, c) in shape:
                if inside(x + dx, dy, w, s["h"], s["corner"]):
                    p.px(x + dx, dy, c)
            x += 3 + (1 if (i * 7 + seed) % 3 == 0 else 0)
            i += 1

    def badge_label(self):
        return (RAMP["cocoa"][2], C["white"])

    def badge_gold(self):
        return (LE[4], C["coal"])

    def badge_states(self):
        # Green is drawn in mint and red in cherry, and yellow in the candles' flame so it stands apart from the
        # lemon label, with dark letters.
        return {"green": (MI[2], C["white"]), "yellow": (FL[4], C["coal"]),
                "red": (RAMP["cherry"][3], C["white"]), "slate": (C["slate"], C["white"])}

    def badge_swatches(self):
        return {"strawberry": (S[2], C["white"], None), "frosting": (S[4], C["coal"], None),
                "cream": (CR[5], C["ink"], "outline"), "cocoa": (RAMP["cocoa"][2], C["white"], None),
                "mint": (MI[4], C["coal"], None), "pistachio": (MI[2], C["white"], None),
                "lemon": (LE[4], C["coal"], None), "lilac": (LI[3], C["white"], None),
                "lavender": (LI[5], C["coal"], None), "sky": (SK[4], C["coal"], None),
                "blueberry": (SK[2], C["white"], None), "cherry": (RAMP["cherry"][3], C["white"], None),
                "flame": (FL[4], C["coal"], None), "plum": (PL[3], C["white"], None),
                "slate": (C["slate"], C["white"], None),
                "sprinkles": (PL[2], C["white"], "sprinkles"), "polka": (S[1], C["white"], "polka")}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        if y in text_rows:
            return c
        if pattern == "sprinkles" and (x * 5 + y * 11) % 13 == 0:
            return (S[5], MI[5], LE[5], SK[5])[(x + y) % 4]
        if pattern == "polka" and (x % 4 == 1 and y % 4 == 1):
            return S[4]
        return c

    def badge_outline(self, pattern):
        return S[2] if pattern == "outline" else None

    def badge_shine(self, c, y, h):
        """Plastic's gloss: its foot a step darker, the sprinkles taking its top."""
        try:
            return step(c, -1) if y == h - 1 else c
        except KeyError:
            return c

    def plate_colours(self, mode):
        if mode == "day":
            return dict(paper=C["paper"], dot=S[6], frame=S[2], block=S[2], ink=C["ink"], letters=C["white"])
        if mode == "night":
            return dict(paper=PL[1], dot=PL[3], frame=S[4], block=S[4], ink=X["body_night"], letters=C["ink"])
        return dict(paper=LE[4], dot=LE[3], frame=C["coal"], edge=LE[2], ink=C["coal"])

    def plate_edge(self, block):
        return step(block, -1)

    # ---- the games
    def game_squares(self, night):
        """A board of strawberry frosting flecked with lemon sprinkles on vanilla satin."""
        return (Stuff(CR, 4 if night else 5, "satin"), Stuff(S, 3, "flecks", LE[5]))

    def game_frame(self, night):
        """A frame striped strawberry and cream, as a birthday candle is."""
        return Stuff(S, 2, "flat", CR[5]), "stripes"

    def game_podium(self, night):
        """A podium of strawberry frosting flecked with sprinkles, tied with a mint ribbon as a present is."""
        return Podium(Stuff(S, 3 if night else 4, "flecks", LE[5]), "ribbon", Stuff(MI, 4))


SET = Birthday()
