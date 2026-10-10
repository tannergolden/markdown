# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The New Year's Day set: the last minutes of the old year, and the first morning of the new one.

Titles are gold foil; a theatre's marquee of bulbs frames every sheet, streamers are swagged across the
top and confetti lies along every rule. Headers stand on snow: a tall clock with its hands together at
twelve beside champagne on ice, and the year in gold foil balloons; a city with the tower the ball drops
from; a bottle that pops its cork beside two flutes. By night the city's windows are lit, the ball comes
down its mast, the year lights on its roof and fireworks answer it. By day the paper is soft white and the
first sunrise of the year comes up behind the towers, with no fireworks in its sky.

The year is never written in: it is the year of the New Year's Day the set is handed (`day`), whatever its
figures, or with none the sample's.
"""
from __future__ import annotations

from functools import partial

from ..designs import NARROW, Holiday
from ..designs.badges import inside
from . import art as A
from .palette import C, CONFETTI, NIGHT_SKY, RAMP, TOKENS, X, step

SAMPLE_YEAR = 2027          # the year drawn when the set is not told its day, as in the shared checks
YEAR_ROOM = (358, 409)      # the columns the year's balloons may take in H1: right of the words, to the frame
HEAD_RULE = 20              # the row an element's head is ruled at, where the confetti lies sparser
LINK_SPRITES = ("star", "balloon", "flute", "hat")


class NewYearsDay(Holiday):
    key = "new-years-day"
    name = "New Year's Day"
    tokens = frozenset(TOKENS)

    @property
    def year(self) -> str:
        """The year the set celebrates, as its figures: the year of the New Year's Day it is handed."""
        return str(self.day.year if self.day else SAMPLE_YEAR)

    # ---- colour and paper
    def ink(self, night):
        """The set's colours. `shadow` is the gold a check mark's shadow takes; a title's own shadow is in
        `lit`."""
        return dict(
            title=X["accent_night"] if night else RAMP["midnight"][2],
            shadow=RAMP["gold"][2] if night else RAMP["gold"][1],
            body=X["body_night"] if night else C["ink"], muted=X["muted_night"] if night else X["muted_day"],
            rule=X["night_rule"] if night else X["rule_day"], accent=X["accent_night"] if night else X["accent_day"],
            tag=RAMP["gold"][4], tag_ink=C["ink"],
            fill=X["node_night"] if night else C["white"], dim=X["dim_night"] if night else X["dim_day"],
        )

    def lit(self, night):
        """Gold foil over the letters, a tone lighter by night so it reads on the sky. By day `title_text`
        sets a midnight edge round them and a silver shadow under them first."""
        return dict(paint=A.FOIL, night=night)

    def paper(self, p, night, uid="p"):
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        if not night:
            return C["paper"]
        return NIGHT_SKY[min(len(NIGHT_SKY) - 1, int(y * len(NIGHT_SKY) / p.h))]

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        A.stars(p, x0, y0, x1, y1, n, seed=seed, twinkling=twinkling, faint=faint, avoid=avoid)

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The paper, or by night the midnight sky with a star for every 12 units across (half as many on a
        drawing made lighter), twinkling if it moves, kept out of the boxes the words take."""
        self.paper(p, night)
        if night:
            self.stars(p, 6, 16, p.w - 6, int(y1 * 0.7), n=p.w // (24 if p.lite else 12), seed=seed,
                       twinkling=motion, avoid=avoid)

    def frame(self, p, night, webs=False):
        A.marquee_frame(p, night)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """Streamers swagged across the top, hung a row higher than a garland: on a wide sheet a swag every
        45 units sagging 5, on a phone every 34 sagging 4."""
        span, sag = (45, 5) if x1 - x0 > NARROW else (34, 4)
        A.streamers(p, x0, x1, y - 1, span, sag, night)

    def tag(self, p, x, y, w, h, night):
        """The gold block a tag's dark letters sit on: lit along its top, shaded along its foot."""
        G = RAMP["gold"]
        p.rect(x, y, w, h, G[4])
        p.hline(x, x + w, y, G[5])
        p.hline(x, x + w, y + h - 1, G[3])

    def title_text(self, p, x, y, s, night, scale):
        """Letters of gold foil: by day with a midnight edge round them and a silver shadow under them, by
        night none, the gold reading on the sky; and here and there a glint where the foil catches the
        light, twinkling in a moving file (a drawing made lighter, and letters too small to carry one, go
        without)."""
        k = self.ink(night)
        if not night:
            A.edged(p, x, y, s, scale, shadow=RAMP["silver"][4], edge=RAMP["midnight"][1])
        w = p.text(x, y, s, k["title"], "57", scale, **self.lit(night))
        if scale >= 2 and not p.lite:
            A.glints(p, x, y, s, scale)
        return w

    # ---- the headers' scenes
    def section_mark(self, p, x, y, night):
        A.star5(p, x - 1, y, "gold", night, reuse=False)

    def strip_mark(self, p, x, y, night):
        A.star5(p, x - 1, y - 3, "gold", night, reuse=False)
        A.sparkle(p, x + 8, y - 5, L=p.twinkle(2))

    def scene(self, design, p, rule, night, motion):
        """The celebration each header stands on (see `_midnight`, `_city` and `_cork`); and by night, in a
        moving file, the marquee's bulbs flare in turn round the frame."""
        if night and motion:
            A.marquee_chase(p)
        if design == "H1":
            return self._midnight(p, rule, night, motion)
        if design == "H2":
            return self._city(p, rule, night, motion)
        return self._cork(p, rule, night, motion)

    def _midnight(self, p, rule, night, motion):
        """H1: on the left a tall clock at midnight, a bunch of balloons over champagne on ice and two flutes
        poured; on the right the year in gold balloons riding the air over a popper and a party hat; confetti
        falling, and by night fireworks over both."""
        string = RAMP["silver"][3 if night else 4]
        A.snow(p, 5, 60, rule - 3, rule, seed=2, night=night)
        A.snow(p, 354, 410, rule - 3, rule, seed=6, night=night)
        A.grandfather_clock(p, 16, rule - 1, night, motion=motion)
        bunch = ((29, rule - 58, "rose"), (37, rule - 62, "gold"), (45, rule - 56, "teal"))
        riding = A.bobbing(p, motion, "bob1", (0, 1, 2, 2, 1, 0), 3.4)
        for (bx, by, fam) in bunch:
            A.balloon(p, bx, by, fam, night, L=riding, string=0)
        for (bx, by, _) in bunch:                               # their ribbons, gathered down to the bucket
            for j in range(by + 10, rule - 19):
                curl = (j // 3) % 2 if bx != 37 else 0
                p.px(bx + curl + round((31 - bx) * (j - by - 10) / max(1, rule - 29 - by)), j, string)
        A.ice_bucket(p, 25, rule - 1, night)
        A.flute(p, 41, rule - 1, night, motion=motion, phase=0)
        A.flute(p, 47, rule - 1, night, motion=motion, phase=1, fill=0.55)
        # The year, whatever its figures, as large as fits between the words and the frame.
        year = self.year
        face = A.year_face(year, YEAR_ROOM[1] - YEAR_ROOM[0])
        yx = YEAR_ROOM[1] - A.year_width(year, *face)
        mids, foot = A.year_balloons(p, yx, rule - 46, night, L=A.bobbing(p, motion), strings=0, face=face,
                                     year=year)
        for sx in mids:                                         # their ribbons, down to where they are tied
            for j in range(foot, rule - 1):
                p.px(sx + (j // 3) % 2, j, string)
        A.party_popper(p, 370, rule - 1, night)
        A.party_hat(p, 397, rule - 1, "teal", night)
        for (sx, sr) in ((16, 7), (30, 7), (43, 3), (49, 3), (372, 4), (397, 5)):
            A.contact(p, sx, rule - 1, sr)
        A.show(p, [(36, 30, 10, "gold", "peony", 14), (392, 24, 11, "rose", "willow", 0),
                   (62, 16, 7, "teal", "ring", 0)], night, motion, dur=9.0, room=partial(self._rise, p))
        A.flurries(p, [(42, 14, rule - 1, -6, 7.0, 0.0), (366, 12, rule - 1, 8, 8.2, 0.5)], night, motion)
        return [(5, 60), (354, 410)]

    def _city(self, p, rule, night, motion):
        """H2: on the right the city, and above it the tower the ball drops from, two flutes raised in front.
        By day the first sunrise of the year comes up behind the towers. By night their windows are lit, the
        ball comes down in the last seconds of the year, the year lights on the roof as it lands, and
        fireworks go up to answer it. A building that would reach a word is cut down to clear it."""
        if not night:
            A.sunrise(p, 393, rule - 17, 10)
            A.clouds(p, [(371, rule - 31, 30), (381, rule - 24, 22)], night)
        A.skyline(p, 296, 374, rule - 2, night, seed=3, lo=12, hi=28, taper=(True, False), sun_x=393,
                  landmarks=((314, "crown", 22), (361, "deco", 18)), clear=partial(self._clear, p))
        A.skyline(p, 374, 410, rule - 2, night, seed=8, lo=6, hi=14, taper=(False, False), sun_x=393)
        A.ball_drop(p, 350, rule - 2, night, motion=motion, dur=12.0, year=self.year)
        A.snow(p, 294, 410, rule - 3, rule, seed=3, night=night)
        shadows = []
        for x, phase, fill in ((301, 0, 0.7), (307, 1, 0.6)):
            if p.clear_of_words(x - 1, rule - 18, x + 6, rule):
                A.flute(p, x, rule - 1, night, motion=motion, phase=phase, fill=fill)
                shadows.append(x + 2)
        for sx in shadows:
            A.contact(p, sx, rule - 1, 3)
        A.show(p, [(318, 34, 11, "gold", "peony", 16), (392, 28, 12, "rose", "willow", 14)], night, motion,
               dur=12.0, start=0.34, room=partial(self._rise, p))
        A.flurries(p, [(318, 14, rule - 1, -8, 7.6, 0.0), (396, 12, rule - 1, -10, 8.8, 0.45)], night, motion)
        return [(294, 410)]

    def _cork(self, p, rule, night, motion):
        """H3: a bottle of champagne that pops its cork now and then, beside two flutes and a party hat; by day
        a leaf of the calendar turned to the first of January, by night a sparkler and a firework that blooms
        as the cork pops."""
        A.snow(p, 352, 410, rule - 3, rule, seed=4, night=night)
        if night:
            A.sparkler(p, 358, rule - 1, 13, night, motion=motion, lean=-2)
        else:
            A.calendar_page(p, 355, rule - 17, night)
        A.champagne_bottle(p, 372, rule - 1, night, motion=motion)
        A.flute(p, 384, rule - 1, night, motion=motion, phase=0)
        A.flute(p, 390, rule - 1, night, motion=motion, phase=1, fill=0.55)
        A.party_hat(p, 403, rule - 1, "rose", night)
        for (sx, sr) in ((375, 5), (386, 3), (392, 3), (403, 5)):
            A.contact(p, sx, rule - 1, sr)
        A.show(p, [(392, 24, 9, "gold", "peony", 0)], night, motion, dur=6.0, start=A.SHOW_SPAN,
               room=partial(self._rise, p))
        A.flurries(p, [(372, 12, rule - 1, -8, 6.4, 0.2)], night, motion)
        return [(352, 410)]

    @staticmethod
    def _clear(p, x0, y0, x1, y1) -> bool:
        """Whether a box touches no word, and neither a title nor the dimension drawn over it."""
        if not p.clear_of_words(x0, y0, x1, y1):
            return False
        titles = [b for b in p.words if b[3] - b[1] >= 16]      # the lines set at twice the face or larger
        return all(x1 <= b[0] or x0 >= b[2] or y1 <= b[1] - 12 or y0 >= b[3] for b in titles)

    def _rise(self, p, x, y, r, kind):
        """How far below a burst at (x, y) its trail first shows: all the way where nothing lies under it,
        nearer where a word does; None when the burst would reach a word, so it is left out."""
        if not self._clear(p, *A.burst_box(x, y, r, kind)):
            return None
        near = round(r * 0.45) + 3                              # where the trail shows just before the break
        for rise in range(r + 7, near - 1, -1):
            if self._clear(p, x - 1, y + near, x + 2, y + rise + 6):
                return rise
        return None

    def scene_narrow(self, design, p, y, night):
        """On a phone: H1's party on the rule at `y`; H2's star beside SECTION A-A, and a toast that stands
        on the figures' rule once it is drawn (see `rule_decor`); H3's star and glint beside the title."""
        if design == "H1":
            self._party(p, y, night)
        elif design == "H2":
            if p.clear_of_words(NARROW - 21, y - 3, NARROW - 14, y + 4):
                A.star5(p, NARROW - 20, y - 2, "silver" if night else "gold", night, reuse=False)
            p.toast = True
        else:
            sy = max(y - 17, 29)                                # level with the title's upper half
            if p.clear_of_words(154, sy - 3, NARROW - 6, sy + 6):
                A.star5(p, 156, sy, "gold", night, reuse=False)
                A.sparkle(p, 166, sy - 2, L="near")

    def _party(self, p, y, night):
        """A phone's H1: champagne on ice and two flutes on the left, a popper, a party hat and a bottle of
        champagne on the right, each standing on the rule where no word is in its way."""
        A.snow(p, 5, 40, y - 3, y, seed=7, night=night)
        A.snow(p, 140, NARROW - 5, y - 3, y, seed=9, night=night)
        base, shadows = y - 1, []
        if p.clear_of_words(7, y - 20, 23, y):
            A.ice_bucket(p, 9, base, night)
            shadows.append((14, 7))
        for x, fill in ((24, 0.7), (30, 0.55)):
            if p.clear_of_words(x - 1, y - 18, x + 6, y):
                A.flute(p, x, base, night, motion=False, fill=fill)
                shadows.append((x + 2, 3))
        if p.clear_of_words(143, y - 17, 156, y):
            A.party_popper(p, 146, base, night)
        if p.clear_of_words(155, y - 13, 165, y):
            A.party_hat(p, 160, base, "teal", night)
            shadows.append((160, 5))
        if p.clear_of_words(165, y - 24, 174, y):
            A.champagne_bottle(p, 166, base, night, motion=False)
            shadows.append((169, 5))
        for (sx, sr) in shadows:
            A.contact(p, sx, base, sr)

    def rule_decor(self, p, x0, x1, y, seed, night):
        """Confetti lying along a rule, sparser along an element's head; a phone's H2 has its toast stand on
        the figures' rule first."""
        if getattr(p, "toast", False):
            p.toast = False
            for x, fill in ((150, 0.7), (156, 0.55)):
                if p.clear_of_words(x - 1, y - 17, x + 6, y):
                    A.flute(p, x, y, night, motion=False, fill=fill)
            if p.clear_of_words(164, y - 12, 174, y):
                A.party_hat(p, 169, y, "rose", night)
        A.confetti_on(p, x0, x1, y, seed=seed, night=night, gap=(4, 12) if y == HEAD_RULE else (3, 9))

    def finish(self, p, night):
        A.lamplight(p, night)

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        """A party hat and a foil star at the end of the notes: on a wide block the hat stands on the frame's
        inner rule; on a phone's the two sit up by the notes' label."""
        if p.w > NARROW:
            A.party_hat(p, x + 4, p.h - 4, "rose", night)
            A.star5(p, x + 10, p.h - 15, "gold", night, reuse=False)
        else:
            A.party_hat(p, x + 7, y + 6, "rose", night)
            A.star5(p, x + 13, y - 4, "gold", night, reuse=False)

    def heart(self, p, x, y):
        A.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        A.stripe_bar(p, x0, y0, w, h, period)

    def link_colours(self, night):
        if night:
            return X["node_night"], X["night_rule"], X["body_night"], RAMP["coal"][2]
        return C["white"], X["rule_day"], C["ink"], X["dim_day"]

    def link_top(self, p, x0, x1, y, seed, night):
        """A strip of marquee along the button's top edge: gold, a bulb lit every four pixels."""
        G, M, Ch = RAMP["gold"], RAMP["midnight"], RAMP["champagne"]
        k = -1 if night else 0
        for xx in range(x0 - 1, x1 + 1):
            p.px(xx, y, G[5 + k] if (xx + seed) % 4 == 2 else G[4 + k])
            p.px(xx, y + 1, Ch[6] if (xx + seed) % 4 == 1 else M[2])

    def link_icon(self, index, night, ink):
        return A.ICONS[LINK_SPRITES[index % len(LINK_SPRITES)]], A.icon_pal(night)

    # ---- the elements
    def card_bevel(self, night):
        return (RAMP["coal"][3], RAMP["coal"][0]) if night else (C["white"], X["dim_day"])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A strip of gold foil for the icon cell's edge with a glint in it, a foil star on the lid, and
        confetti along the lid."""
        G = RAMP["gold"]
        k = -1 if night else 0
        for yy in range(y + 1, y + h - 1):
            glint = (yy - y) % 9 == 4
            for i, t in enumerate((5, 4, 3)):
                p.px(x + 10 + i, yy, G[(6 if glint and i == 0 else t) + k])
        if lid:
            A.star5(p, x + 9, y - 5, "gold", night)
        A.confetti_on(p, x + (15 if lid else 3), x + w - 2, y, seed=x + y, night=night, gap=(5, 14))

    def wire_ink(self, night):
        return RAMP["champagne"][4] if night else self.ink(night)["body"]

    def wire_lights(self, p, cells, night, seed):
        """Confetti caught along a wire where it runs level, a piece every fifth pixel, above it and below by
        turns."""
        run = sorted((x, y) for (x, y, d) in cells[4:-6] if d == "h")
        for i, (x, y) in enumerate(run[::5]):
            fam = CONFETTI[(i + seed) % len(CONFETTI)]
            p.px(x, y - 1 if i % 2 else y + 1, A.confetti_colour(fam, night, i % 3 != 1))

    def dashes(self, night):
        return [RAMP["gold"][4 if night else 3], X["muted_night"] if night else RAMP["midnight"][3]]

    def ornament(self, kind, p, x, y, night):
        if kind == "schematic":
            if p is not None:
                A.champagne_on_ice(p, x, y, night)
            return A.ON_ICE
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        A.champagne_glass(p, bx, base, bw, v, night, self.wire_ink(night))

    def peak_mark(self, p, x, y, night):
        A.star5(p, x - 1, y - 1, "gold", night, reuse=False)

    def dial_ring(self, p, arc, night):
        """The upper half of a clock's face, eight pixels deep inside the ring the kit's arc runs along, its
        hours the dial's ticks."""
        (xa, ya), (xb, _) = arc[0], arc[-1]
        r = round((xb - xa) / 2 + 1.5)
        A.clock_ring(p, round((xa + xb) / 2), round(ya), r - 8, r, night)

    def dial_tick(self, p, x, y, night):
        """None: the clock's face carries its own hours."""

    def dial_hub(self, p, cx, cy, night):
        """A gold boss the hand turns on."""
        G = RAMP["gold"]
        for (dx, dy, t) in ((0, 0, 6), (-1, 0, 5), (1, 0, 4), (0, -1, 5), (0, 1, 3)):
            p.px(cx + dx, cy + dy - 1, G[t])

    def material(self, i, xx, yy, y0, y1, lift, night):
        """Four cloths for a party by turns: gold sequins, silver lamé, midnight velvet and rose glitter."""
        G, S, M, R = (RAMP[n] for n in ("gold", "silver", "midnight", "rose"))
        kind = i % 4
        if kind == 0:
            c = (G[5], G[4], G[3])[((xx % 3) + ((yy - y0) % 3)) % 3]
        elif kind == 1:
            c = S[5] if ((xx + yy) // 2) % 2 == 0 else S[4]
        elif kind == 2:
            c = M[3] if (xx + yy * 3) % 7 else M[4]
        else:
            c = R[5] if (xx * 5 + yy * 3) % 11 == 0 else R[3]
        return step(c, lift)

    def counter_cell(self, q, ox, oy, night):
        A.flip_tile(q, ox, oy)

    def counter_ink(self, night, dim):
        return RAMP["coal"][5] if dim else RAMP["champagne"][6]

    def timeline_line(self, p, x0, x1, y, night):
        A.twine(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        A.party_light(p, x, gy, kind, night, i, unlit=self.ink(night)["muted"])

    def today_mark(self, p, x, y, night):
        A.sparkle(p, x + 2, y, big=True, warm=True)

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor as a party guest in their colour under a paper hat; a bot as a little alarm clock."""
        if not person.get("initials"):
            A.alarm_clock(p, cx, cy, night)
            return
        A.guest(p, cx, cy, ("rose", "gold", "teal")[i % 3], str(person["initials"])[:2], night)

    def commit_bar(self, p, x, y, w, fill, night):
        """A contributor's share, striped like a streamer, gold and midnight."""
        G, M = RAMP["gold"], RAMP["midnight"]
        p.box(x, y, w + 2, 4, self.wire_ink(night))
        for xx in range(fill):
            bright = (xx // 2) % 2 == 0
            p.px(x + 1 + xx, y + 1, G[5] if bright else M[4])
            p.px(x + 1 + xx, y + 2, G[3] if bright else M[2])

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """A seal of gold foil folded into a starburst round the disc."""
        A.foil_seal(p, cx, cy, r0 + 2, night)

    def placard_board(self, p, night):
        """A marquee's sign: its bulbs round the card and streamers swagged along its top."""
        A.paper(p, night, 3, 5, p.w - 6, p.h - 8, uid="pl")
        if night:
            A.stars(p, 8, 10, p.w - 8, p.h - 32, 24, seed=9, twinkling=False, faint=True)
        A.marquee_frame(p, night, 0, 2, p.w, p.h - 4, uid="plq")
        A.streamers(p, 90, 170, 5, 40, 4, night)

    def placard(self, d, night):
        """The placard, and a party hat standing at its foot where the description leaves it room."""
        p = super().placard(d, night)
        if p.clear_of_words(182, 54, 192, 68):
            A.party_hat(p, 187, 67, "teal", night)
        return p

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """Confetti along the badge's top two rows, kept inside its shape: squares and strips of gold, rose,
        teal, silver and violet by turns, some face up and some turned, a pixel or two apart."""
        fams = ("gold", "rose", "teal", "silver", "gold", "violet")
        x, i = 1 + seed % 2, 0
        while x < w - 2:
            R = RAMP[fams[(i + seed) % len(fams)]]
            lit, dark = (R[6], R[4]) if fams[(i + seed) % len(fams)] == "silver" else (R[5], R[3])
            shape = (((0, 0, lit), (1, 0, dark)) if i % 3 == 0 else ((0, 1, lit), (1, 1, lit)) if i % 3 == 1
                     else ((0, 0, dark), (0, 1, lit)))
            for (dx, dy, c) in shape:
                if inside(x + dx, dy, w, s["h"], s["corner"]):
                    p.px(x + dx, dy, c)
            x += 3 + (1 if (i * 7 + seed) % 3 == 0 else 0)
            i += 1

    def badge_label(self):
        return (RAMP["midnight"][3], C["white"])

    def badge_gold(self):
        return (RAMP["gold"][4], C["coal"])

    def badge_states(self):
        # Green is drawn in teal and red in rose, and yellow in champagne so it stands apart from the gold
        # label, with dark letters.
        return {"green": (RAMP["teal"][2], C["white"]), "yellow": (RAMP["champagne"][4], C["coal"]),
                "red": (RAMP["rose"][3], C["white"]), "slate": (C["slate"], C["white"])}

    def badge_swatches(self):
        return {"midnight": (RAMP["midnight"][3], C["white"], None), "dusk": (RAMP["midnight"][5], C["white"], None),
                "gold": (RAMP["gold"][4], C["coal"], None), "silver": (RAMP["silver"][4], C["coal"], None),
                "slate": (C["slate"], C["white"], None), "champagne": (RAMP["champagne"][5], C["ink"], "outline"),
                "confetti": (RAMP["midnight"][2], C["white"], "confetti"),
                "starlight": (RAMP["violet"][1], C["white"], "stars"), "violet": (RAMP["violet"][3], C["white"], None),
                "rose": (RAMP["rose"][3], C["white"], None), "dawn": (RAMP["dawn"][4], C["coal"], None),
                "ember": (RAMP["dawn"][2], C["white"], None), "teal": (RAMP["teal"][4], C["coal"], None),
                "bottle": (RAMP["bottle"][4], C["white"], None), "bronze": (RAMP["gold"][1], C["white"], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        if y in text_rows:
            return c
        if pattern == "confetti" and (x * 5 + y * 11) % 13 == 0:
            return (RAMP["gold"][5], RAMP["rose"][5], RAMP["teal"][5])[(x + y) % 3]
        if pattern == "stars" and (x * 7 + y * 13) % 23 == 0:
            return C["white"] if (x + y) % 2 else RAMP["gold"][5]
        return c

    def badge_outline(self, pattern):
        return RAMP["midnight"][3] if pattern == "outline" else None

    def badge_shine(self, c, y, h):
        """Plastic's gloss: its foot a step darker, the confetti taking its top."""
        try:
            return step(c, -1) if y == h - 1 else c
        except KeyError:
            return c

    def plate_colours(self, mode):
        G, M = RAMP["gold"], RAMP["midnight"]
        if mode == "day":
            return dict(paper=C["paper"], dot=C["grid"], frame=M[3], block=M[3], ink=C["ink"], letters=C["white"])
        if mode == "night":
            return dict(paper=M[1], dot=C["grid_n"], frame=G[4], block=G[4], ink=X["body_night"], letters=C["ink"])
        return dict(paper=G[4], dot=G[3], frame=C["coal"], edge=G[2], ink=C["coal"])

    def plate_edge(self, block):
        return step(block, -1)


SET = NewYearsDay()
