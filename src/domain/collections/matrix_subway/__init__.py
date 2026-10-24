# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Subway set: the station in the July heat, July's design in the Matrix collection, drawn in the collection's
hand.

Every sheet is a station wall of glazed subway tile in a running bond, pale celadon by day and teal-black after hours,
a border of bottle-green tile down each side and a band of terracotta and ochre tile along the foot; along a header's
top runs a mosaic frieze of ochre set with lozenges of terracotta and cobalt, stopping either side of the month's
mark. Titles are the station's name laid in mosaic, tessera by tessera in terracotta set in dark grout, their glaze
catching the light and their shadow cast on the tile; in a moving header the terminal's beam passes down them on the
hand's period, and after hours the fluorescent light glints on them. Every wide header stands under the light from the
street, falling through the gratings in shafts slanting across the wall behind the title, dust turning in them.

An H1 is the platform: at the left the tunnel's mouth in its mosaic arch rising nearly the sheet's height, a signal
burning in it, and the train coming up the tunnel head on, nearer and nearer, its two headlights blazing phosphor,
their glare spilling out over the tile and their light thrown along the platform's edge; at the right a fan turning
against the heat on a steel column, the station clock with its second hand stepping round, a poster lit from behind
with the code falling down it, a bench, a fluorescent tube overhead that flickers after hours, and a lone figure in a
long dark coat waiting at the yellow line, his coat stirring in the train's wind as a sheet of newspaper tumbles along
the platform toward him. An H2 is the way down from the street: the stair rising the header's height to its arched way
out, its side walled in bottle-green tile under a band of mosaic, the July sun pouring in and down the flight by day,
a green globe burning on each newel post and lighting the steps after hours, and a woman in a red summer dress coming
down it to the platform. An H3's hero is the token booth, rising the strip's full height under its sign lit along its
roof, the clerk at its glass, the turnstiles before it, a bank of as many as three where the words leave room, and a
sign of black enamel hung over it on a taller strip; after hours its tube lights the glass from inside and throws its
light over the floor. On a phone the H1's whole station stands across the width under its words, and the H2's stair
and the H3's booth stand under theirs whatever they say.

The footers stand on the platform's edge, the yellow line and its concrete lip over the band of tile, rising into a
dado of bottle-green tile where the cells leave it room, and after the last cell the way down to the trains is marked
by a pair of green globes on their posts, or one where a pair has no room, its post cut short where a whole one has
none, burning after hours. The links are enamel station signs hung on steel hooks; the badges carry the frieze along
their tops; and the elements are built of the station: cards glazed and edged in mosaic on green conduit with a signal
lamp where it turns, bars of stacked tile, a clock's steel rim, file types in glazes of their own, enamel number
plates, the releases as stops on a subway map's line with the train at today, contributors as enamel roundels in the
lines' colours, and a ring of mosaic round the seal. The games are played on a board of glazed tesserae in a frame of
terracotta, and the Hall's winners stand on blocks of the wall's tile.
"""
from __future__ import annotations

from ...holidays.designs.badges import inside
from ...holidays.designs.materials import Podium, Stuff
from ...holidays.pixel import measure, tube
from ..hand import CollectionSet
from .. import rain
from . import art as A
from .palette import C, RAMP, TOKENS, X, step

TERRA, BOTTLE, GLAZE = RAMP["terra"], RAMP["bottle"], RAMP["glaze"]
COBALT, OCHRE, STEEL, COAT, ENAMEL = RAMP["cobalt"], RAMP["ochre"], RAMP["steel"], RAMP["coat"], RAMP["enamel"]


class Subway(CollectionSet):
    key = "matrix-subway"
    name = "Subway"
    collection = "matrix"
    tagline = ("The station in the July heat, in glazed tile and mosaic: a train blazing out of the tunnel, the stair "
               "down from the street, and a long coat waiting.")
    about = (
        "A station wall of glazed subway tile in a running bond, pale celadon by day and teal-black after hours, a "
        "border of bottle-green tile down its sides, a band of terracotta and ochre tile along its foot and a mosaic "
        "frieze of ochre set with lozenges of terracotta and cobalt along its top. Titles are the station's name laid "
        "in mosaic, tessera by tessera in dark grout, their glaze catching the light. Shafts of light from the street "
        "gratings slant across the wall behind every title, dust turning in them. The first header is the platform: "
        "the train coming up the tunnel head on under its tall mosaic arch, a signal burning in the dark, its two "
        "headlights blazing and their light thrown along the platform; and across it a fan turning against the heat, "
        "the station clock with its second hand stepping round, a poster lit from behind with the code falling down "
        "it, a bench, a fluorescent tube that flickers after hours, and a lone figure in a long dark coat waiting at "
        "the yellow line as a sheet of newspaper tumbles toward him in the train's wind. A section's header is the "
        "way down from the street, the stair rising to its arched way out with the July sun pouring down it, green "
        "globes on its newel posts and a woman in a red summer dress coming down to the platform; a strip's is the "
        "token booth, its sign lit along its roof and the clerk at its glass beside the turnstiles. On a phone each "
        "scene stands under the words. The footers stand on the platform's edge, the yellow line over the tile, "
        "rising into a dado of green tile where there is room, with a pair of green globes on their posts after the "
        "last cell. The links are enamel station signs, the badges carry the frieze, and the elements are the "
        "station's own: mosaic-edged cards on green conduit, bars of stacked tile, a clock's steel rim, enamel number "
        "plates, the releases as stops on a subway map's line with the train at today, contributors as enamel "
        "roundels and a mosaic ring round the seal; the games are played on glazed tile in a terracotta frame.")
    tokens = frozenset(TOKENS)
    # The train's face in each frame of its arrival, far back in the tunnel, nearer, and at its mouth: (its left, how
    # far its top stands over the ground, its width and height, and its glare's size).
    ARRIVAL = ((22, 32, 14, 18, 0.5), (16, 41, 26, 33, 0.75), (9, 52, 40, 50, 1.2))

    # ---- colour and paper
    def ink(self, night):
        """The words in the hand's two inks; the titles in the mosaic's terracotta."""
        return dict(
            title=TERRA[5] if night else TERRA[2], shadow=TERRA[0] if night else C["grout"],
            body=self.hand.body[night], muted=self.hand.muted[night],
            rule=X["rule_night"] if night else X["rule_day"], accent=TERRA[5] if night else TERRA[2],
            tag=BOTTLE[3] if night else BOTTLE[2], tag_ink=GLAZE[6],
            fill=C["tile_lit_n"] if night else GLAZE[6], dim=X["dim_night"] if night else X["dim_day"],
        )

    def paper(self, p, night, uid="p"):
        p.sheet = uid
        A.wall(p, night, uid=uid)

    def bg_at(self, p, night, y):
        return A.bg_at(p, night, y)

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The tiled wall alone: a station has no sky."""
        self.paper(p, night)

    _foot = False     # set while a footer is drawn, whose footing takes the frame's foot (see `art.footing`)

    def frame(self, p, night, webs=False):
        A.frame(p, night, header=webs, foot=not self._foot)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """The mosaic frieze along the top, stopping either side of the month's mark."""
        A.frieze(p, x0, x1, night, self.mark_box(p), self.marked)

    def tag(self, p, x, y, w, h, night):
        """A tile of bottle-green glaze, a note's number knocked out of it."""
        p.rect(x, y, w, h, BOTTLE[3] if night else BOTTLE[2])
        p.hline(x, x + w, y, BOTTLE[5] if night else BOTTLE[4])

    def title_text(self, p, x, y, s, night, scale):
        """The station's name in mosaic (see `art.mosaic_title`). The drawing keeps each line, for the scan that passes
        down it in a moving header."""
        w = A.mosaic_title(p, x, y, s, scale, night)
        p.titles = getattr(p, "titles", []) + [(x, y, s, scale, w)]
        return w

    # ---- the headers' scenes
    def scene(self, design, p, rule, night, motion):
        """On H1 the light from the street slanting across the wall behind the title, ending above the tagline; the
        platform's edge along the foot, the train coming up the tunnel at the left with its headlights blazing, and at
        the right the tube, the column and its fan, the poster, the clock, the bench and the man waiting, a sheet of
        newspaper tumbling between them; and in a moving header the beam passing down each line of the title on the
        hand's period."""
        if motion:
            for n, (x, y, s, scale, w) in enumerate(getattr(p, "titles", ())):
                rain.scan(p, x, y, s, scale, w, n, self.hand.glint, C["white"])
        g = rule - 1
        spans = []
        titles = getattr(p, "titles", ())
        under = max((y + 7 * scale for x, y, s, scale, w in titles), default=0)
        foot = min([b[1] for b in p.words if b[1] >= under] + [g - 4]) - 2
        A.shafts(p, foot, self.mark_box(p), night, motion)
        A.platform(p, 4, 411, g, night)
        if design != "H1":
            hero = (self._entrance if design == "H2" else self._booth)(p, g, night, motion)
            return [hero] if hero else []
        left = self._left(p, g, night, motion)
        if left:
            spans.append(left)
        right = self._right(p, g, night, motion)
        if right:
            spans.append(right)
        path = self._gust(p, g)
        if path:
            A.newspaper(p, path, night, motion)
        return spans

    def _left(self, p, g, night, motion):
        """The left of an H1: the tunnel's arch rising nearly the sheet's height, and in it the train standing at its
        mouth head on, then for an instant back up the tunnel and coming out again, nearer and nearer, its headlights
        blazing, their glare spilling out over the tile and their light thrown
        along the platform's edge, none of it on a word. Returns the span it covers."""
        if not p.clear_of_words(2, TUNNEL_TOP - 5, 56, g + 1):
            return None
        A.tunnel(p, 7, 50, TUNNEL_TOP, g - 2, night)
        if motion:
            for n, ((x, dy, w, h, size), (t0, t1)) in enumerate(zip(self.ARRIVAL, ((.74, .86), (.86, 1), (0, .74)))):
                L = p.seq(f"tn{n}", t0, t1, A.ARRIVE, keep=n == 2, z=0.4)
                lights = A.train(p, x, g - dy, w, h, night, L)
                glare = p.seq(f"tg{n}", t0, t1, A.ARRIVE, keep=n == 2, z=3)
                A.headlights(p, lights, g, night, motion, clear=True, L=glare, size=size)
        else:
            x, dy, w, h, size = self.ARRIVAL[-1]
            lights = A.train(p, x, g - dy, w, h, night)
            A.headlights(p, lights, g, night, motion, clear=True)
        if p.clear_of_words(8, TUNNEL_TOP + 8, 18, TUNNEL_TOP + 21):
            A.signal(p, 12, TUNNEL_TOP + 10, night, motion)
        if night:
            A.floor_glow(p, 30, g, 70)
        return (1, 56)

    @staticmethod
    def _right(p, g, night, motion):
        """The right of an H1, each thing where the words leave it room: the tube hanging overhead and its cone of
        light, the column and its fan, the lit poster, the clock on its rod, the bench and the man waiting. Returns the
        span it covers."""
        if not p.clear_of_words(358, g - 30, 411, g + 1):
            return None
        light = None
        if p.clear_of_words(354, 10, 384, 20):
            light = A.tube(p, 356, 382, 15, night, motion)
            top = light[1] + 2
            spread = next((s for s in (0.2, 0.15, 0.1, 0.05, 0.0)
                           if all(p.clear_of_words(round(368 - 4 - (y - top) * s) - 3, y, 368, y + 1)
                                  for y in range(round(top), g))), None)
            if spread is not None:
                A.cone(p, 368, top, g - 2, 8, night, motion, spread=spread)
        if p.clear_of_words(372, 9, 384, g + 1):
            A.column(p, 375, 11, g, night)
            if p.clear_of_words(362, 41, 384, 60):
                A.fan(p, 368, 50, night, motion)
        if p.clear_of_words(382, 34, 411, 82):
            A.poster(p, 386, 38, 22, 41, night, motion)
        if p.clear_of_words(385, 9, 410, 36):
            A.clock(p, 397, 23, night, motion, r=9)
        A.bench(p, 383, 409, g, night)
        A.waiting(p, 358, g, night, motion, light=light)
        return (356, 411)

    @staticmethod
    def _gust(p, g):
        """The path a sheet of newspaper tumbles along the platform in the train's wind, from the train toward the man
        waiting, bouncing as it goes, as far as the words leave it room; none if they leave it too little."""
        path = []
        for i, x in enumerate(range(50, 352, 3)):
            y = g - 3 - (1, 2, 3, 2, 1, 0)[i % 6]
            if not p.clear_of_words(x - 2, y - 2, x + 7, g + 1):
                break
            path.append((x, y))
        return path if len(path) >= 30 else []

    @staticmethod
    def _entrance(p, g, night, motion):
        """The right of an H2: the stair down from the street, its foot on the platform and its landing at the frame,
        rising as high as the header lets it; the arched way out at its head, the July sun pouring in through it and
        down the flight by day; the green globes burning on its newel posts and lighting the steps after hours; and
        the woman in the red dress coming down it to the platform, none of it on a word. Returns the span it
        covers."""
        n = max(8, min(14, (g - 40) // A.STEP))
        fx, x2 = 316, p.w - A.EDGE
        x1 = fx + n * A.STEP
        head = A.stair_top(fx, g, n - 1)
        top = max(17, head - 30)
        if not p.clear_of_words(fx - 9, top - 6, p.w, g + 2):
            return None
        A.way_out(p, x1 + 3, x2 - 7, top, head - 1, night)
        st = A.stairs(p, fx, g, n, x2, night)
        for i, (nx, ny) in enumerate(st["newels"]):
            A.globe(p, nx, ny - 5, night, motion, phase=i)
            if night:
                A.lamplit(p, nx, ny + 6, 16, 18, A.STAIR_LIT)
        A.daylight(p, fx, g, x1 + 3, top, head, night)
        path = [(x1 + 6, head - 1), (x1 + 1, head - 1)]
        path += [(fx + i * A.STEP - 1, A.stair_top(fx, g, i) - 1) for i in range(n - 1, -1, -1)]
        A.rider(p, path, night, motion)
        return (fx - 6, p.w - A.EDGE)

    @staticmethod
    def _booth(p, g, night, motion):
        """The right of an H3: the token booth on the platform rising the strip's full height, its sign lit along
        its roof under the frieze, the clerk at its glass; over it, where a strip is taller than the booth, a sign of
        black enamel hung from the ceiling pointing the way to the trains; and before it the turnstiles, a bank of as
        many as three where the words leave them room; after hours the booth's light thrown out over the counter,
        the turnstiles nearest it and the floor. None of it on a word. Returns the span it covers."""
        x = p.w - A.EDGE - A.BOOTH_W - 3
        top = max(16, g - A.BOOTH_HIGH + 1)
        if top < A.SIGN_ROOM:
            top = min(top, 18)          # a gap too short for the sign: the booth grows to the top band instead
        if not p.clear_of_words(x - 4, 12, p.w, g + 2) or g - top + 1 < A.BOOTH_LOW:
            return None
        if top >= A.SIGN_ROOM:
            A.hanging_sign(p, x + 4, x + A.BOOTH_W - 4, 13, 12, night)
        n = 0
        while n < 3 and p.clear_of_words(x - 15 - 13 * n, g - 18, x - 13 * n, g + 2):
            A.turnstile(p, x - 13 - 13 * n, g, night)
            n += 1
        A.booth(p, x, top, g, night, motion)
        return (x - 14 - 13 * max(0, n - 1), p.w - A.EDGE)

    def rule_decor(self, p, x0, x1, y, seed, night):
        """Tesserae let into the rule where no scene stands on it, ochre and terracotta by turns, as the mosaic's
        border runs on along a station's wall (see `art.inlay`)."""
        A.inlay(p, x0, x1, y, night, seed)

    # ---- a phone's scenes: the H1's under its words in the rows it keeps there, the H2's and H3's in rows asked for
    PHONE_H1 = 56     # the rows a phone's H1 station stands in, the tunnel's arch the tallest of it
    UNDER = {"H2": 62, "H3": 62}      # the rows a phone's H2 and H3 ask for under their words for their heroes
    _h1_rows = 0      # the rows a phone's H1 is drawn with, while it is

    @property
    def phone_scene_rows(self):
        """The rows a phone's H1 asks for between its words and its rule (see `h1_narrow`)."""
        return self._h1_rows

    def h1_narrow(self, h, night):
        """A phone's H1, its whole station standing across it under the words, in the rows the tunnel's arch rises
        through, the notes set under the words, however many there are."""
        self._h1_rows = self.PHONE_H1 + 4 + 10 * len(self.said(h))
        try:
            return super().h1_narrow(h, night)
        finally:
            self._h1_rows = 0

    def phone_rows(self, design, title_w):
        """The rows a phone's H2 or H3 asks for under its words, whatever its title: those its hero takes, two clear
        of the last words at least."""
        return self.UNDER.get(design, 0)

    @staticmethod
    def _room(p):
        """Whether a box on a phone lies inside the frame and at least two units clear of every word."""
        def room(x0, y0, x1, y1):
            return x0 >= A.EDGE and x1 <= p.w - A.EDGE and p.clear_of_words(x0 - 2, y0 - 2, x1 + 2, y1 + 2)
        return room

    def scene_narrow(self, design, p, y, night):
        """A phone's H1 scene: the whole station across the phone, standing on the rule at `y` in the rows asked for
        under its words (see `h1_narrow`). A phone's H2 and H3 stand their heroes under their words instead (see
        `scene_under`)."""
        if design == "H1":
            self._phone_station(p, y - 1, night)

    def scene_under(self, design, p, y0, y1, night):
        """The scene in the rows a phone's H2 or H3 asked for under its words, standing on the rule at `y1`: the stair
        down from the street on an H2, the token booth on an H3."""
        g = y1 - 1
        A.platform(p, A.EDGE, p.w - A.EDGE, g, night)
        (self._phone_entrance if design == "H2" else self._phone_booth)(p, g, g - self.UNDER[design] + 3, night)

    def _phone_station(self, p, g, night):
        """The H1's station across a phone, standing on the platform's row g, as the wide H1 has it: the tunnel's arch
        at the left with the train in it coming on, its headlights blazing and their light along the platform's edge;
        the man waiting at the yellow line, the column and its fan, the lit poster, the station clock hung over the
        bench, and the tube over it all."""
        room = self._room(p)
        top = g - self.PHONE_H1 + 1
        A.platform(p, A.EDGE, p.w - A.EDGE, g, night)
        if room(4, top, 54, g):
            A.tunnel(p, 7, 50, top + 3, g - 2, night)
            x, dy, w, h, size = self.ARRIVAL[1]
            lights = A.train(p, x, g - dy, w, h, night)
            A.headlights(p, lights, g, night, False, clear=True, size=size)
            if night:
                A.floor_glow(p, 30, g, 60)
        if room(120, top, p.w - A.EDGE, g):
            light = A.tube(p, 148, p.w - A.EDGE, top + 3, night, False, ceiling=top)
            A.cone(p, 161, light[1] + 2, g - 2, 8, night, False, spread=0.15)
        if room(84, top, 96, g):
            A.column(p, 88, top, g, night)
            A.fan(p, 81, g - 30, night, False)
        if room(100, g - 46, 122, g - 12):
            A.poster(p, 102, g - 44, 16, 28, night, False)
        if room(122, top, 146, g - 16):
            A.clock(p, 133, top + 13, night, False, r=8, ceiling=top)
        A.bench(p, 126, 156, g, night)
        A.waiting(p, 60, g, night, False, light=None)

    def _phone_entrance(self, p, g, top, night):
        """The H2's stair under a phone's words, standing on the platform's row g: its flight rising to the right to
        its landing at the frame, the arched way out at its head with the sun pouring in by day, the globes on its
        newel posts, and the woman in the red dress at its head; at the left the turnstiles she will pass, and the lit
        poster on the wall."""
        room = self._room(p)
        n = (g - top - 20) // A.STEP
        x2 = p.w - A.EDGE
        x1 = x2 - 22
        fx = x1 - n * A.STEP
        head = A.stair_top(fx, g, n - 1)
        if room(fx - 9, top, x2, g):
            A.way_out(p, x1 + 3, x2 - 7, max(top + 4, head - 26), head - 1, night)
            st = A.stairs(p, fx, g, n, x2, night)
            for i, (nx, ny) in enumerate(st["newels"]):
                A.globe(p, nx, ny - 5, night, False, phase=i)
                if night:
                    A.lamplit(p, nx, ny + 6, 16, 18, A.STAIR_LIT)
            A.daylight(p, fx, g, x1 + 3, max(top + 4, head - 26), head, night)
            A.rider(p, [(x1 + 4, head - 1)], night, False)
        if room(14, g - 36, 40, g - 6):
            A.poster(p, 16, g - 34, 20, 26, night, False)
        for tx in (46, 64):
            if room(tx, g - 16, tx + 12, g):
                A.turnstile(p, tx, g, night)

    def _phone_booth(self, p, g, top, night):
        """The H3's token booth under a phone's words, standing on the platform's row g: the booth at the right, its
        sign lit along its roof and the clerk at its glass, the turnstile before it, and at the left the bench and the
        man waiting at the yellow line; after hours the booth's light out over the floor."""
        room = self._room(p)
        x = p.w - A.EDGE - A.BOOTH_W - 4
        btop = max(top, g - A.BOOTH_HIGH + 1)
        if room(x - 1, btop, x + A.BOOTH_W + 1, g):
            A.booth(p, x, btop, g, night, False)
        if room(x - 15, g - 16, x - 1, g):
            A.turnstile(p, x - 14, g, night)
        if room(14, g - 34, 76, g):
            A.bench(p, 40, 70, g, night)
            A.waiting(p, 18, g, night, False, light=None)

    def section_mark(self, p, x, y, night):
        """A token for the turnstile, brass with its cut-out letter, after SECTION A-A."""
        p.sprite(x, y - 1, A.ICONS["token"], A.icon_pal(night, ""))

    def strip_mark(self, p, x, y, night):
        """A green globe on its iron post beside the strip's title, the way down to the trains (see
        `art.globe_post`)."""
        A.globe_post(p, x - 3, y + 6, night)

    def _finish(self, p, night):
        """The last pass, which a drawing made lighter keeps too: the design's last light at full weight only (see
        `finish`), then the file written as lightly as it can be, the same drawing unit for unit, the month's mark
        left as it is drawn (see `Pix.compact`)."""
        if not p.lite:
            self.finish(p, night)
        p.compact(keep=("mark",))

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        """A token for the turnstile, brass with its cut-out letter, in the corner of the closing notes."""
        p.sprite(x + 2, y - 3, A.ICONS["token"], A.icon_pal(night, ""))

    def _footed(self, p, night, last=False):
        """A footer once its cells are laid: the platform's edge along its foot, rising into a dado of tile where the
        cells leave it room, and the way down to the trains, the pair of green globes on their posts, where they
        leave it free (see `art.footing`): on a title block only after its `last` cell, the way back up."""
        after = max((b[2] for b in p.words), default=0) + 4 if last else 0
        A.footing(p, night, after=after)
        return p

    def _tread(self, draw, ft, night, last=False):
        """A footer drawn with its frame's foot left to its footing, then footed (see `_footed`)."""
        self._foot = True
        try:
            p = draw(ft, night)
        finally:
            self._foot = False
        return self._footed(p, night, last=last)

    def f1(self, ft, night):
        return self._tread(super().f1, ft, night, last=True)

    def f2(self, ft, night):
        return self._tread(super().f2, ft, night)

    def f1_narrow(self, ft, night):
        return self._tread(super().f1_narrow, ft, night, last=True)

    def f2_narrow(self, ft, night):
        return self._tread(super().f2_narrow, ft, night)

    def heart(self, p, x, y):
        A.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        """A run of glazed tiles, ochre and cobalt by turns (see `art.scale_tiles`)."""
        A.scale_tiles(p, x0, y0, w, h, period)

    def link_colours(self, night):
        """A station sign of cobalt enamel in a steel rim, its letters white enamel; a tone darker after hours."""
        if night:
            return COBALT[1], STEEL[1], ENAMEL[5], COBALT[0]
        return COBALT[2], COBALT[0], ENAMEL[6], COBALT[1]

    def link_top(self, p, x0, x1, y, seed, night):
        """The button as a station's enamel sign: a hairline of white enamel along the top of its face under its rim,
        its face in shade down its right, hung from two steel hooks over its ends."""
        fill, edge, ink, shade = self.link_colours(night)
        w = p.w
        p.hline(2, w - 2, y + 1, ENAMEL[4] if night else ENAMEL[6])
        p.vline(w - 2, y + 2, y + 9, shade)
        k = -2 if night else 0
        for hx in (4, w - 6):
            p.px(hx, y - 2, A.ramp_at(STEEL, 5 + k))
            p.px(hx + 1, y - 2, A.ramp_at(STEEL, 3 + k))
            p.px(hx, y - 1, A.ramp_at(STEEL, 4 + k))
            p.px(hx + 1, y - 1, A.ramp_at(STEEL, 2 + k))

    def link_icon(self, index, night, ink):
        return A.ICONS[A.LINK_SPRITES[index % len(A.LINK_SPRITES)]], A.icon_pal(night, ink)

    # ---- the elements
    def card_bevel(self, night):
        return (STEEL[4], A.TUNNEL[1]) if night else (C["white"], GLAZE[3])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A card as a panel of glazed tile: its icon's cell glazed, a strip of mosaic down the cell's edge and a
        band of the frieze along the top of a card with a lid (see `art.card_glaze`)."""
        A.card_glaze(p, night, x, y, w, h, lid)

    def wire_ink(self, night):
        return BOTTLE[4] if night else BOTTLE[2]

    def wire_lights(self, p, cells, night, seed):
        """The wire as green conduit clipped to the tile, a signal lamp burning where it turns (see
        `art.wire_lamps`)."""
        A.wire_lamps(p, cells, night)

    def dashes(self, night):
        return [OCHRE[3], TERRA[4]] if night else [OCHRE[4], TERRA[3]]

    def ornament(self, kind, p, x, y, night):
        """A token for the turnstile, brass with its cut-out letter, in a free corner of the schematic."""
        if kind == "schematic":
            if p is not None:
                A.token(p, x, y, night, s=2)
            return (14, 14)
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as a stack of glazed tiles, terracotta and ochre course by course (see
        `art.tile_bar`)."""
        A.tile_bar(p, bx, base, bw, v, night)

    def peak_mark(self, p, x, y, night):
        A.signal_lamp(p, x, y + 1, night)

    def dial_ring(self, p, arc, night):
        """The station clock's rim of steel, lit at its upper left."""
        k = -1 if night else 0

        def colour(s, o, lam, x, y):
            return STEEL[max(1, min(6, round(1.6 + 4.2 * lam) + k))]
        tube(p, arc, 2.0, colour, outline=STEEL[0])

    def dial_tick(self, p, x, y, night):
        """A tessera of ochre at each hour of the clock's rim."""
        k = -1 if night else 0
        p.px(x, y, A.ramp_at(OCHRE, 5 + k))
        p.px(x - 1, y, A.ramp_at(OCHRE, 3 + k))

    def dial_hub(self, p, cx, cy, night):
        """The clock's hub, a boss of steel with a terracotta cap."""
        k = -1 if night else 0
        p.rect(cx - 1, cy - 1, 3, 3, A.ramp_at(STEEL, 4 + k))
        p.px(cx, cy, TERRA[4 + k])
        p.px(cx - 1, cy - 1, A.ramp_at(STEEL, 6 + k))

    def material(self, i, xx, yy, y0, y1, lift, night):
        """Each file type in a glaze of its own, terracotta, cobalt, ochre and bottle green by turns, laid as tiles
        in grout, a tile every five units."""
        k = -1 if night else 0
        R = RAMP[("terra", "cobalt", "ochre", "bottle")[i % 4]]
        if xx % 5 == 0:
            return A.ramp_at(R, 1 + k)
        return step(A.ramp_at(R, 3 + k), lift)

    def counter_cell(self, q, ox, oy, night):
        """A counter's digit on a platform's enamel number plate (see `art.enamel_plate`)."""
        A.enamel_plate(q, ox, oy, night)

    def counter_ink(self, night, dim):
        """The plate's numeral, cobalt on white enamel by day and white on cobalt after hours, a leading nought a
        shade fainter."""
        if night:
            return ENAMEL[3] if dim else ENAMEL[6]
        return COBALT[4] if dim else COBALT[0]

    def timeline_line(self, p, x0, x1, y, night):
        """The releases' line as a subway map draws its lines (see `art.map_line`)."""
        A.map_line(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        """A release as a stop on the line (see `art.stop`)."""
        A.stop(p, x, gy, kind, night)

    def today_mark(self, p, x, y, night):
        """The train at today's end of the line (see `art.little_train`)."""
        A.little_train(p, x, y, night)

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor as an enamel roundel ringed in the colour of a line of the map, their initials on its white
        disc; a bot's roundel carries a token."""
        ink = A.roundel(p, cx, cy, i, night)
        ini = str(person.get("initials") or "")[:2]
        if ini:
            p.text(cx - measure(ini, "35") // 2, cy - 2, ini, ink, "35")
        else:
            A.token(p, cx - 3, cy - 3, night)

    def commit_bar(self, p, x, y, w, fill, night):
        """A contributor's share as the platform's yellow line, its studs catching the light, in a rim of steel."""
        k = -2 if night else 0
        p.box(x, y, w + 2, 4, A.ramp_at(STEEL, 2 + k))
        for xx in range(fill):
            p.px(x + 1 + xx, y + 1, A.ramp_at(RAMP["yellow"], (6 if xx % 3 == 1 else 4) + k))
            p.px(x + 1 + xx, y + 2, A.ramp_at(RAMP["yellow"], 3 + k))

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """A ring of mosaic round the seal (see `art.tesserae_ring`)."""
        A.tesserae_ring(p, cx, cy, r0, r1, night)

    def seal_mark(self, p, x, y, night):
        A.token(p, x + 3, y, night)

    def placard_board(self, p, night):
        """The placard as a panel of the station's wall: the glazed tile in its border of bottle-green tile and its
        band along the foot, the frieze along its top."""
        A.wall(p, night, uid="pl")
        A.frame(p, night)
        A.frieze(p, A.EDGE, p.w - A.EDGE, night, (0, 0, 0, 0), False, top=3)

    def placard_mark(self, p, x, y, night):
        A.token(p, x, y - 4, night)

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """The frieze along a badge's top two rows, kept inside its shape: a line of bottle-green glaze over ochre set
        with tesserae of cobalt and terracotta by turns, the letters under it."""
        h = s["h"]
        for x in range(w):
            if inside(x, 0, w, h, s["corner"]):
                p.px(x, 0, BOTTLE[2])
            if inside(x, 1, w, h, s["corner"]):
                n = (x + seed) % 6
                p.px(x, 1, COBALT[4] if n == 1 else TERRA[4] if n == 4 else OCHRE[4])

    def badge_label(self):
        return (BOTTLE[1], ENAMEL[6])

    def badge_gold(self):
        """A live badge's label in the brass of a token, its letters dark on it."""
        return (OCHRE[4], COAT[0])

    def badge_states(self):
        """Green in the border's bottle glaze, yellow in the platform's safety line, red in the mosaic's
        terracotta and slate in the train's steel."""
        return {"green": (BOTTLE[3], C["white"]), "yellow": (RAMP["yellow"][4], COAT[1]),
                "red": (TERRA[2], C["white"]), "slate": (STEEL[2], C["white"])}

    def badge_swatches(self):
        return {"terra": (TERRA[2], C["white"], "tiles"), "ochre": (OCHRE[4], COAT[0], None),
                "cobalt": (COBALT[2], C["white"], None), "bottle": (BOTTLE[3], C["white"], "tiles"),
                "glaze": (GLAZE[4], COAT[0], None), "steel": (STEEL[2], C["white"], None),
                "yellow": (RAMP["yellow"][4], COAT[1], None), "oak": (RAMP["oak"][3], C["white"], None),
                "coat": (COAT[2], ENAMEL[5], None), "enamel": (ENAMEL[5], COAT[1], "enamel"),
                "concrete": (RAMP["concrete"][3], COAT[0], None), "dress": (RAMP["dress"][3], C["white"], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        """A glazed swatch laid as tiles, the grout between them every fifth unit, above and below its letters."""
        if pattern == "tiles" and x % 5 == 0 and y not in text_rows:
            return step(c, -2)
        return c

    def badge_outline(self, pattern):
        return COBALT[2] if pattern == "enamel" else None

    def badge_shine(self, c, y, h):
        try:
            return step(c, 1) if y == 2 else step(c, -1) if y == h - 1 else c
        except KeyError:
            return c

    def plate_edge(self, block):
        try:
            return step(block, -1)
        except KeyError:
            return block

    def plate_colours(self, mode):
        """A plate's colours: by day the tile, its value on cobalt enamel; after hours the dark tile, its value on
        a token's brass; live, the label in brass."""
        if mode == "day":
            return dict(paper=C["tile"], dot=C["grout"], frame=BOTTLE[2], block=COBALT[2], ink=C["ink"],
                        letters=ENAMEL[6])
        if mode == "night":
            return dict(paper=C["tile_n"], dot=C["grout_n"], frame=BOTTLE[3], block=OCHRE[4], ink=C["body_night"],
                        letters=COAT[0])
        return dict(paper=OCHRE[4], dot=OCHRE[4], frame=COAT[1], edge=OCHRE[2], ink=COAT[0])

    # ---- the games
    def game_squares(self, night):
        """A board of the station's glazed tile, its light squares the wall's celadon and its dark the border's bottle
        green, each laid as tesserae in grout, a tone down after hours, as every board of the year is dimmer after
        dark."""
        return (Stuff(RAMP["glaze"], 5 if night else 6, "tile"), Stuff(RAMP["bottle"], 4 if night else 5, "tile"))

    def game_frame(self, night):
        """A frame of the mosaic's terracotta, laid in tesserae."""
        return Stuff(RAMP["terra"], 3), "tesserae"

    def game_podium(self, night):
        """A podium of the wall's glazed tile, its blocks laid plain."""
        return Podium(Stuff(RAMP["glaze"], 4, "tile"))


TUNNEL_TOP = 22      # the row the tunnel's arch is crowned at, under the frieze


SET = Subway()
