# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Mosaic set: the gold of a Byzantine mosaic in August, laid tile by tile.

Every sheet is a mosaic laid in tesserae, drawn in the medieval collection's hand (see `collections.hand`). By day
its ground is a burnished gold, small tiles of close golds set in irregular courses with fine grout between them, a
tile here and there catching the light, and behind every word the tiles calm to an even field of gold within the
hand's band; in a moving header a slow sheen crosses the gold, the tiles catching the light in turn as it passes,
and single tiles glitter. By night the ground is a vault of quiet lapis sown with small gold stars, lit only by its
own lamps, which burn on the hand's flame, and in a moving header the tiles nearest each lamp glint in its light. A
jewelled band of white, red and green tesserae frames every sheet, with a cut stone in a gold cell at each corner,
and along a header's top runs the wave scroll in two blues on white, a crest centred under the month's mark, its
crests catching the light crest by crest in a wide moving header; no star and no glittering tile comes near the
mark. Titles are built tile by tile, deep blue on gold by day and gold glowing on the blue by night, a glint running
through them one tile at a time once in the hand's twelve seconds.

An H1 is the apse: under its arch two peacocks perch on the rim of a marble fountain, one bent to drink and one with
its head up, their trains hanging with their eyes, the vine rising behind them into the conch with its leaves and
its grapes, and a lamp crown hung from the arch's crown. In a moving header the birds take turns to drink, the jet's
drops sparkle as they fall and the eyes of the trains glint. Beyond it the palace's arcade stands with its curtains
drawn back to its columns, the empress in its middle arch as the mosaic shows her, crowned in gold and jewels with
strings of pearls beside her face, a broad jewelled collar on her shoulders, her cloak of purple falling to its hem
embroidered in gold and a bowl of gold in her hands, and a lady in each of the others in her veil and her silk
patterned in gold, all of them with the mosaic's large dark eyes and their faces on the hand's three skins. Where
the words leave rows between them the court walks to the palace in procession, in robes of purple, white and gold
with jewelled collars, and where they leave its full height clear the palace's door stands at its left, its curtain
drawn aside on the dark of the hall and a small fountain before it; where they leave the rows beside the apse too,
the port the court sets out from stands there, its lighthouse on its mole at the harbour's mouth, ships on the water
and the city's walls, towers, roofs and gold dome running on to its gate. By night the lamp crown and a lamp in each
arch burn with warm pools on the gold, their light laid on the birds, the vine, the marble and the faces near them
and kept inside the walls they hang in, and the lighthouse burns over the city's lit windows. An H2 is a peacock
large beside its title, drawn larger than the strip's to stand in front of its fan, the fan of its crest over its
head and its tail half open in a fan of eyes, which glint in turn in a moving header as the light crosses them; the
port with its lighthouse, its walls and its ships stands beyond it where the words leave room. An H3 is a fountain
with a dove on each end of its rim under a lamp crown, and as much of its court as the words leave room for: a
peacock facing it, or a pair of them either side of it, their trains trailing along the ground, and where the band
runs wide, the vine growing out of a vase in a peopled scroll, birds pecking at the grapes in its scrolls under
hanging oil lamps. On a phone the apse, the court and the palace stand under the words, the peacock beside the title
where it leaves room and else under the words in rows of its own, and the fountain under the words between its pair
of peacocks. The marks beside a title are a dove and a star of gold tesserae, and the vine runs along every rule
where no word lies near. A footer stands on a floor mosaic, a guilloche plaited in garnet and blue round its chain
of dark eyes along its foot, rising in a band of opus sectile, roundels of porphyry and squares of serpentine in
white marble, wherever a cell leaves it room; and where the cells leave room the doves of Pliny drink at their bowl,
an oil lamp standing beside them or hung over them, cold by day and lit by night. A link is a plaque of white marble
with its icon inlaid in gold on lapis.

The elements are the mosaic's own stones: plaques of white marble in rims of gold tesserae for a schematic's cards,
on wires of gold tiles; columns of stacked tesserae with marble capitals for the histogram; a gold sun disc for the
dial, its hand the gnomon's shadow; counters in tesserae on marble; the vine for the time line, grapes at its
releases and a peacock at today; portraits in mosaic with jewelled diadems for the roster, a dove for a bot; a
porphyry roundel for the seal with its check in gold tesserae; and a panel inlaid in cut marble for a placard. A
badge is a plaque of tesserae in a gold rim, its label in deep blue tiles and its message in a stone.
"""
from __future__ import annotations

from ...holidays.designs.badges import inside
from ..hand import CollectionSet
from . import art as A
from .palette import C, RAMP, TOKENS, X, step

GOLD, LAPIS, TILE = RAMP["gold"], RAMP["lapis"], RAMP["tile"]


class Mosaic(CollectionSet):
    collection = "medieval"
    key = "medieval-mosaic"
    name = "Mosaic"
    tagline = (
        "A Byzantine mosaic in burnished August gold that glitters as the light crosses it, where peacocks drink at a "
        "marble fountain and the empress's court stands in the palace arcade.")
    about = (
        "Every sheet is a mosaic of small tesserae: by day a field of burnished gold tiles in irregular courses with "
        "fine grout, calming to an even gold behind every word, and by night a vault of quiet lapis sown with small "
        "gold stars. A jewelled band of white, red and green tiles frames it with a cut stone at each corner, and a "
        "running wave scroll in two blues on white crowns every header, a crest of it under the month's mark. Titles "
        "are built tile by tile, deep blue on gold by day and glowing gold on blue by night, with a glint that runs "
        "through them one tile at a time. The H1 is an apse where two peacocks drink from a marble fountain under a "
        "hanging lamp crown, the vine and its grapes climbing behind them, and beyond it a palace arcade where the "
        "empress stands as the mosaic shows her, crowned in gold and pearls with a bowl of gold in her hands, between "
        "her ladies in silks patterned in gold, her court walking to the palace door in procession where the words "
        "leave room, out of the port of the city when there is room for that too. The faces of the court are laid in "
        "three skins, with the mosaic's large dark eyes. In a moving header the peacocks take turns to drink, the "
        "fountain sparkles, the eyes of their trains glint, single tiles of the gold glitter and a slow sheen crosses "
        "it, the tiles catching the light in turn. By night the only light is the lamps', bronze crowns and small oil "
        "lamps burning with warm pools on the gold, the tiles nearest them glinting. The H2 is a peacock with the fan "
        "of its crest and its tail half open, the port and its lighthouse beyond it where there is room, and the H3 a "
        "fountain with doves on its rim, between a pair of peacocks and beside the vine's peopled scroll where the "
        "words leave room. Footers stand on a floor mosaic, a guilloche plaited in garnet and blue that rises into "
        "opus sectile where it can, and wherever the cells leave room the doves of Pliny drink at their bowl with an "
        "oil lamp beside them, lit by night. Links are marble plaques with gold icons, badges are tesserae plaques "
        "rimmed in gold, and the elements are made of the mosaic's stones, from columns of tesserae with marble "
        "capitals to a sun disc dial and a porphyry seal.")
    tokens = frozenset(TOKENS)

    # ---- colour and paper
    def ink(self, night):
        return dict(
            title=GOLD[4] if night else LAPIS[3], shadow=LAPIS[0] if night else TILE[1],
            body=self.hand.body[night], muted=self.hand.muted[night],
            rule=X["rule_night"] if night else X["rule_day"], accent=GOLD[5] if night else X["accent_day"],
            tag=LAPIS[2], tag_ink=GOLD[5],
            fill=C["fill_n"] if night else C["fill"], dim=X["dim_night"] if night else X["dim_day"],
        )

    def paper(self, p, night, uid="p"):
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        return A.bg_at(p, night, y)

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        """The vault's gold stars, fewer than the kit's, and on a sheet that is not a header fewer still (see
        `art.stars`)."""
        A.stars(p, x0, y0, x1, y1, max(4, round(n * (0.22 if faint else 0.5))), seed=seed, twinkling=twinkling,
                faint=faint, avoid=avoid)

    def roundel(self, p, margin=2):
        """The box the month's mark takes at the top centre of a header, `margin` units wider all round (see
        `mark_box`): the stars and the glitter keep out of it, with the mark and without it, so that nothing of the
        sky is cut at its edge."""
        return self.mark_box(p, margin)

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The sheet behind a header: by day the gold ground, its tiles glittering in a moving header and a slow
        sheen crossing it; by night the vault and its stars, and in a moving header the tiles by each lamp glinting
        in its light (see `finish`). Neither a star nor a glittering tile lies in the box the month's mark takes."""
        self.paper(p, night)
        avoid = [*avoid, self.roundel(p)]
        if night:
            self.stars(p, 6, 16, p.w - 6, int(y1 * 0.8), n=p.w // 9, seed=seed, twinkling=motion, avoid=avoid)
        elif motion:
            A.sheen(p, A.SCROLL_FOOT + 1, p.h)
            A.glitter(p, 6, 15, p.w - 6, y1 - 2, n=max(4, p.w // 40), seed=seed, avoid=avoid)

    def frame(self, p, night, webs=False):
        """The jewelled band round a sheet; a footer (the sheet framed without webs on the banners' paper) stands on
        the floor mosaic instead along its foot (see `art.floor`)."""
        A.frame(p, night, header=webs, footer=not webs and getattr(p, "sheet", "") == "p")

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """The running wave scroll along a header's top, between its corner stones, a crest centred under the month's
        mark, with it and without it."""
        A.scroll(p, 7, p.w - 7, night, motion=p.w > 200 and getattr(p, "moving", False), centre=p.w // 2)

    def tag(self, p, x, y, w, h, night):
        """A block of deep blue tesserae a tag's gold letters sit on, its upper edge lit."""
        p.rect(x, y, w, h, LAPIS[2])
        p.hline(x, x + w, y, LAPIS[4])
        p.hline(x, x + w, y + h - 1, LAPIS[0])
        if night:
            p.box(x - 1, y - 1, w + 2, h + 2, GOLD[2], notch=True)

    def title_text(self, p, x, y, s, night, scale):
        return A.tesserae_title(p, x, y, s, night, scale, motion=getattr(p, "moving", False))

    # ---- the headers' scenes
    @staticmethod
    def _reach(p, x0, top, foot, step=1, limit=None):
        """How far right from x0 (or left, with a negative `step`) the rows from `top` to `foot` run clear of words,
        two units of margin kept; at most to `limit`."""
        x = x0
        while (limit is None or (x < limit if step > 0 else x > limit)) and \
                p.clear_of_words(x - 2, top - 2, x + 3, foot + 1):
            x += step
        return x

    def scene(self, design, p, rule, night, motion):
        foot = rule - 1
        top = A.SCROLL_FOOT + 3
        spans = []
        if design == "H1":
            x1 = self._reach(p, 7, top, foot, limit=7 + 54)
            if x1 - 7 >= 30:
                spans.append(A.apse(p, 7, x1 - 1, top, foot, night, motion))
            # the palace's three bays as wide as the words leave them, a column narrower at the least; its
            # capitals reach a column out past its left, which keeps two from every word
            x0 = self._reach(p, p.w - 8, top, foot, step=-1, limit=p.w - 8 - 3 * A.BAY - A.COLUMN - 2)
            bay = min(A.BAY, (p.w - 10 - x0 - A.COLUMN) // 3)
            w = 3 * bay + A.COLUMN
            if bay >= A.BAY - 1:
                px0 = p.w - 8 - w
                spans.append(A.palace(p, px0, w, top, foot, night, motion, bay=bay))
                room = self._rows(p, spans[0][1] + 2 if spans else 8, px0 - 3, foot, 50, 36)
                if room:
                    # the door the court comes to, its curtain drawn aside and its fountain before it, where the
                    # words leave the palace's full height clear at its left
                    door = px0 - (A.DOOR_W - A.COLUMN)
                    if p.clear_of_words(door - 3, top + 10, px0, foot + 1) and door - (spans[0][1] + 2) > 3 * A.STEP:
                        A.doorway(p, door, top, foot, night)
                        spans.append((door - 2, px0))
                        px0 = door
                    left = spans[0][1] + 3 if spans[0][0] < 60 else 8
                    end = self._reach(p, px0 - 4, foot - room, foot, step=-1, limit=left)
                    span = A.procession(p, end + 2, px0 - 3, foot - 3, night, room)
                    if span:
                        spans.append(span)
            if spans and spans[0][0] < 60:
                harbour = self._harbour(p, spans, foot, night, motion)
                if harbour:
                    spans.append(harbour)
        elif design == "H2":
            spans += self._court_garden(p, top, foot, night, motion)
        else:
            spans += self._basin(p, top, foot, night, motion)
        for (a, b) in spans:
            A.clear_stars(p, a, 0, b, rule)
        return spans

    def _harbour(self, p, spans, foot, night, motion):
        """Between the apse and the words, where they leave it the rows, the port the court sets out from: its
        lighthouse on its mole beside the apse at the harbour's mouth, ships on the water, and the city's walls with
        their towers, roofs and dome running on to the city's gate, under the title where it stands clear of it, as far
        as the procession, which leaves the gate for the palace. Returns the span it covers, or None where the words
        leave it too little room."""
        x0 = spans[0][1] + 3
        walking = [a for (a, b) in spans[1:] if a > x0]
        limit = min(walking) - 1 if walking else p.w // 2
        # the lighthouse and the dome stand tall beside the apse; the walls, the towers and their roofs lie low
        if not p.clear_of_words(x0 - 2, foot - 43, x0 + 44, foot + 1):
            return None
        x1 = self._reach(p, x0 + 44, foot - 26, foot, limit=limit)
        if x1 - x0 < 100:
            return None
        wall = foot - 19                                 # the city walls' top row

        def room(xa, xb):
            h = 0
            while h < 40 and p.clear_of_words(xa - 2, wall - h - 3, xb + 2, wall):
                h += 1
            return h
        return A.port(p, x0, x1, foot - 41, foot, night, motion=motion, mouth="left", room=room)

    def _court_garden(self, p, top, foot, night, motion):
        """The right of an H2: the peacock large beside the title, its tail half open behind it, standing on the
        green ground, as large as the words leave it room."""
        x0 = self._reach(p, p.w - 8, top, foot, step=-1, limit=200) + 2
        if p.w - 8 - x0 < 50:
            return []
        x0 = max(x0, p.w - 8 - 112)
        R = min(64, p.w - 8 - (x0 + A.SHOWING_RUMP[0]) - 2,
                foot - 3 - (len(A.SHOWING) - A.SHOWING_RUMP[1]) - top - 2)
        eyes = []
        A.meadow(p, x0, p.w - 7, foot - 3, foot, night)
        A.display_peacock(p, x0, foot - 4, night, motion=motion, R=R, eyes=eyes)
        if motion:
            top_y = foot - 4 - len(A.SHOWING) + 1
            A.eye_glints(p, eyes, night, fan=(x0 + A.SHOWING_RUMP[0], top_y + A.SHOWING_RUMP[1]))
        hang = x0 + 4
        A.lamp_crown(p, hang, A.SCROLL_FOOT + 1, night, phase=2, chain=max(2, foot - 4 - len(A.SHOWING) - 30 - 14))
        spans = [(x0 - 1, p.w - 6)]
        left = self._reach(p, x0 - 4, top + 22, foot, step=-1, limit=8)
        if x0 - 4 - left >= 70:
            spans.append(A.port(p, left + 2, x0 - 3, foot - 50, foot, night, motion))
        return spans

    def _basin(self, p, top, foot, night, motion):
        """The right of an H3, as much of it as the words leave clear, on the green ground: the fountain with a dove
        on each end of its rim, one drinking, a lamp crown hung over it; where the room runs wider a pair of peacocks
        standing either side of it, facing it, their trains trailing behind them along the ground, or one of them
        where there is room for one; and where it runs wider still the vine growing out of a vase beside them in a
        peopled scroll, birds pecking at the grapes in its scrolls and small oil lamps hung over it, lit by night.
        Everything keeps two units from every word."""
        x0 = self._reach(p, p.w - 8, top + 10, foot, step=-1, limit=8) + 2
        x1 = p.w - 8                                    # the last column a scene takes
        if x1 - x0 < 33:
            return []
        ground = foot - 4
        tall = ground - top >= 40                       # rows for a standing peacock under its crest
        train = min(A.TRAIN_MAX, (x1 + 1 - x0) // 2 - A.PAIR_REACH)
        pair = tall and train >= A.TRAIN_MIN
        if pair:
            cx = x1 + 1 - A.PAIR_REACH - train
            left = cx - A.PAIR_REACH - train
        else:
            cx = x1 - 15
            train = cx - A.PAIR_REACH - x0              # what a single peacock left of the fountain has room for
            if not tall or train < 2:
                cx, train = x1 - 22, None
            left = cx - 16 if train is None else cx - A.PAIR_REACH - train
        stem_h = 10 if train is not None else max(4, min(14, ground - top - 30))
        chain = max(2, ground - 5 - stem_h - 11 - 9 - A.SCROLL_FOOT - 1 - 15 - 3)
        light = (cx + 0.5, A.SCROLL_FOOT + 1 + chain + 9, 30)
        spans = [(left - 1, p.w - 6)]
        A.meadow(p, left - 2, p.w - 7, foot - 3, foot, night)
        if pair:
            A.peacock_pair(p, cx, ground, night, motion=motion, train=train, lamps=[light])
        elif train is not None:
            eyes: list = []
            A.standing_peacock(p, cx - A.PAIR_REACH - 3, ground, night, train=train, eyes=eyes)
            if motion:
                A.eye_glints(p, eyes, night)
        A.basin_fountain(p, cx, ground, night, motion=motion, stem_h=stem_h)
        A.lamp_crown(p, cx - 7, A.SCROLL_FOOT + 1, night, phase=1, chain=chain)
        R = 10
        if pair and left - 3 - x0 >= 66 and ground - top >= 2 * R + 26:
            rx = left - 11
            vine = A.vine_scroll(p, (rx, ground), rx - x0, R, night, mid=ground - R - 11)
            if vine:
                box, scrolls = vine
                spans.append((box[0] - 1, box[2] + 1))
                for i, (sx, sy, side) in enumerate(scrolls):
                    if side > 0 and i:
                        A.hanging_lamp(p, round(sx), A.SCROLL_FOOT + 1, round(sy) - R - 8, night, phase=i % 3)
        return spans

    # ---- the phones
    # A phone's H1: the apse and the palace under the words, its notes set over them, ten rows more for each note so
    # the most a page can say still leaves them their rows (see `h1_narrow`).
    _scene_rows = 58

    @property
    def phone_scene_rows(self):
        return self._scene_rows

    def h1_narrow(self, h, night):
        """A phone's H1, its apse and palace given ten rows more for each note it sets, so they keep their size under
        the most a page can say."""
        self._scene_rows = 58 + 10 * len(self.said(h))
        try:
            return super().h1_narrow(h, night)
        finally:
            self._scene_rows = 58
    PHONE_ROWS = {"H2": 58, "H3": 46}   # the rows the peacock, and the fountain and its pair, take under the words
    _under = None           # the header being laid out again with those rows

    def scene_narrow(self, design, p, y, night):
        """A phone's scenes, built to the rows its words leave free: on H1 the apse, the palace and between them as
        many of the court as fit, across the rows under the words; on H2 the peacock with its tail half open beside
        the title where the room runs wide, and where it cannot stand there the header is laid out again with rows
        under its words for it (`scene_under`). An H3's fountain and its pair of peacocks always stand under the
        words, for no strip's title leaves them their height beside it (see `phone_rows`)."""
        if design == "H1":
            p.stood = bool(self._phone_court(p, y - 1, night))
        elif design == "H2":
            p.stood = bool(self._phone_peacock(p, 40, A.SCROLL_FOOT + 3, p.w - 6, y + 8, night, beside=True))

    def _phone_court(self, p, foot, night):
        """The apse, the court and the palace across a phone's H1, as tall as its rows allow."""
        room = A.SCROLL_FOOT + 3
        top = max(room, next((t for t in range(room, foot - 30) if p.clear_of_words(4, t - 2, p.w - 4, foot + 1)),
                             foot - 30))
        rows = foot - top
        if rows < 40:
            return None
        spans = [A.apse(p, 6, 6 + 48, top, foot, night, motion=False)]
        w = 3 * A.BAY + A.COLUMN
        if rows >= 54:
            px0 = p.w - 7 - w
            spans.append(A.palace(p, px0, w, top, foot, night, motion=False))
            if px0 - (A.DOOR_W - A.COLUMN) - 3 - 56 >= 3 * A.STEP:
                px0 -= A.DOOR_W - A.COLUMN
                A.doorway(p, px0, top, foot, night)
            if px0 - 3 - 56 >= A.STEP:
                A.procession(p, 57, px0 - 3, foot - 3, night, rows)
        p.held = [(4, p.w - 4)]
        for (a, b) in spans:
            A.clear_stars(p, a, 0, b, foot + 1)
        return spans

    def _phone_peacock(self, p, x0, top, x1, foot, night, beside=False):
        """The peacock with its tail half open on its ground in the box x0 to x1 and `top` to `foot`, as large as the
        rows clear of words allow, keeping two units from them; beside the words, only where it fits whole."""
        for R in range(min(40, foot - top - 12), 21, -2):
            bx = x1 - 8 - A.SHOWING_RUMP[0] - R
            if bx < x0:
                continue
            box_top = foot - 4 - len(A.SHOWING) + 1 + A.SHOWING_RUMP[1] - R - 3
            if box_top < A.SCROLL_FOOT + 2:
                continue
            if p.clear_of_words(bx - 2, box_top - 2, x1 + 2, foot + 1):
                A.meadow(p, bx - 2, x1, foot - 3, foot, night)
                A.display_peacock(p, bx, foot - 4, night, motion=False, R=R)
                A.clear_stars(p, bx - 2, 0, x1, foot + 1)
                return (bx - 3, x1 + 1)
        return None

    def h2_narrow(self, h, night):
        """A phone's H2, laid out as the kit lays it out; where its peacock found no room beside the words, laid out
        again with rows under them for it (see `phone_rows`)."""
        return self._phone("H2", super().h2_narrow, h, night)

    def h3_narrow(self, h, night):
        """A phone's H3, laid out with rows under its words for its fountain and its pair of peacocks (see
        `phone_rows`)."""
        return super().h3_narrow(h, night)

    def _phone(self, design, draw, h, night):
        p = draw(h, night)
        if getattr(p, "stood", False):
            return p
        self._under = design
        try:
            return draw(h, night)
        finally:
            self._under = None

    def phone_rows(self, design, title_w):
        """The rows a phone's H2 or H3 leaves under its words for its scene. An H3 always leaves them, so its fountain
        and its pair of peacocks stand as tall as the composition asks a phone's hero to stand; an H2 leaves none as
        the kit lays it out, so a peacock that stands beside the words stays there, and only where none could is it
        laid out again with these."""
        return self.PHONE_ROWS[design] if design == "H3" or self._under == design else 0

    def scene_under(self, design, p, y0, y1, night):
        """The scene under a phone's words, from the last of them at row y0 down to the rule at y1: on an H2 the
        peacock with its tail half open and, where it leaves room, the lighthouse on its mole; on an H3 the fountain
        with its doves on its taller shaft and the pair of peacocks either side of it facing it, their trains trailing
        along the ground, as the wide strip has them, some forty rows tall in all."""
        foot = y1 - 1
        p.stood = True
        p.held = [(4, p.w - 4)]
        if design == "H2":
            span = self._phone_peacock(p, 6, y0 + 3, p.w - 6, foot, night)
            if span and span[0] - 6 >= 60:
                A.port(p, 7, span[0] - 3, y0 + 4, foot, night, motion=False)
        else:
            ground, cx = foot - 4, p.w // 2
            A.meadow(p, 6, p.w - 6, foot - 3, foot, night)
            A.peacock_pair(p, cx, ground, night, motion=False, train=min(A.TRAIN_MAX, cx - A.PAIR_REACH - 6))
            A.basin_fountain(p, cx, ground, night, motion=False, stem_h=14, jet=8)
        A.clear_stars(p, 4, y0, p.w - 4, y1)

    def strip_mark(self, p, x, y, night):
        """A dove perched beside a strip's title."""
        A.dove(p, x, y, night)

    def section_mark(self, p, x, y, night):
        """A single gold tessera star after SECTION A-A, from a row above the words to one under them."""
        A.star_mark(p, x, y, night)

    @staticmethod
    def _rows(p, x0, x1, foot, most, least):
        """The rows free of words over the ground at row `foot` between x0 and x1 at its right end, `most` at the
        most; None when fewer than `least`."""
        for room in range(most, least - 1, -1):
            if p.clear_of_words(x1 - 14, foot - room - 2, x1 + 2, foot + 1):
                return room
        return None

    def rule_decor(self, p, x0, x1, y, seed, night):
        """The vine scroll running along a header's rule wherever no scene stands on it and no word lies near; under
        an element's tag, a plain rule."""
        if y > 24 and not getattr(p, "held", None):
            A.running_vine(p, x0, x1, y, night)

    def finish(self, p, night):
        """The last pass: in a moving header by night the tiles by each lamp glinting in its light; the tiles calmed
        behind every word; on an instruments sheet the dial's hand made the gnomon's shadow, and on a certificate the
        seal's check laid in gold tesserae; by night the lamps' light laid into what stands near them."""
        if night and getattr(p, "moving", False):
            A.lamp_glints(p)
        A.calm(p, night)
        k = self.ink(night)
        if getattr(p, "dial", None):
            A.gnomon(p, night, k["accent"])
        if getattr(p, "seal", None):
            A.gold_check(p, night, k["accent"], k["shadow"])
        if night:
            A.lamplight(p)

    def _finish(self, p, night):
        self.finish(p, night)

    def h1(self, h, night, motion):
        return self._moving(super().h1, h, night, motion)

    def h2(self, h, night, motion):
        return self._moving(super().h2, h, night, motion)

    def h3(self, h, night, motion):
        return self._moving(super().h3, h, night, motion)

    _motion = False

    def canvas(self, w, h):
        p = super().canvas(w, h)
        p.moving = self._motion
        return p

    def _moving(self, draw, h, night, motion):
        self._motion = motion
        try:
            return draw(h, night, motion)
        finally:
            self._motion = False

    # ---- the footers
    def _floored(self, p, night):
        """A footer once its cells are laid: its words calmed, the floor mosaic along its foot and its mark at the
        corner of its notes, and by night the lamp's light on what stands near it."""
        A.calm(p, night)
        A.floor(p, night, self.ink(night)["rule"])
        if night:
            A.lamplight(p)
        return p

    def f1(self, ft, night):
        return self._floored(super().f1(ft, night), night)

    def f2(self, ft, night):
        return self._floored(super().f2(ft, night), night)

    def f1_narrow(self, ft, night):
        return self._floored(super().f1_narrow(ft, night), night)

    def f2_narrow(self, ft, night):
        return self._floored(super().f2_narrow(ft, night), night)

    def heart(self, p, x, y):
        R = RAMP["red"]
        art = [".54.43.", "5443321", "4433221", ".33221.", "..221..", "...1..."]
        p.sprite(x, y, art, {str(i): R[i] for i in range(7)})

    def bar(self, p, x0, y0, w, h, period=5):
        for x in range(x0, x0 + w):
            for y in range(y0, y0 + h):
                p.px(x, y, LAPIS[3] if ((x - x0) // period) % 2 == 0 else GOLD[4])

    def link_colours(self, night):
        """A plaque of white marble, its dark edge and its letters (see `link_top`)."""
        return RAMP["pearl"][6], A.K, C["ink"], RAMP["pearl"][4]

    def link_top(self, p, x0, x1, y, seed, night):
        """The button finished as a plaque of white marble in a gold rim, its icon inlaid in gold on lapis."""
        A.plaque(p, p.w, night)

    def link_icon(self, index, night, ink):
        return A.link_icon(index, night)

    # ---- the elements
    def card_bevel(self, night):
        return (C["fill_n"], LAPIS[0]) if night else (C["white"], RAMP["pearl"][4])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A card as a plaque of white marble in a rim of gold tesserae, its icon inlaid in gold on lapis."""
        A.mosaic_card(p, x, y, w, h, night, seed, self.ink(night)["body"])

    def wire_ink(self, night):
        return GOLD[3] if not night else GOLD[2]

    def wire_lights(self, p, cells, night, seed):
        """The wire as a line of gold tesserae with a garnet where it bends."""
        A.gold_wire(p, cells, night)

    def dashes(self, night):
        return [LAPIS[3] if not night else GOLD[3], GOLD[4] if not night else LAPIS[4]]

    def ornament(self, kind, p, x, y, night):
        """The gold vase the vine grows from in a free corner of the schematic."""
        if kind == "schematic":
            if p is not None:
                A.stamp(p, x, y, A.VASE, {"K": A.K, "Y": GOLD[6], "G": GOLD[4], "g": GOLD[2], "o": GOLD[1],
                                         "r": RAMP["red"][3]})
            return (15, 14)
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as a column of tesserae with a marble capital, in a stone by turns."""
        n = getattr(p, "bars", 0)
        p.bars = n + 1
        A.column_bar(p, bx, base, bw, v, night, i=n)

    def peak_mark(self, p, x, y, night):
        """A gold star beside the busiest week's count."""
        A.stamp(p, x, y, A.STARS[1], {"Y": GOLD[4], "y": GOLD[5], "W": GOLD[6]} if night else
                {"Y": LAPIS[3], "y": LAPIS[2], "W": GOLD[5]})

    def dial_ring(self, p, arc, night):
        """The dial as a sun disc of gold tesserae (see `art.sun_disc`)."""
        A.sun_disc(p, arc, night)

    def dial_tick(self, p, x, y, night):
        p.px(x, y, A.K)

    def dial_hub(self, p, cx, cy, night):
        """The gnomon's foot: a pin of bronze on a boss of gold."""
        k = -1 if night else 0
        A.stamp(p, cx - 2, cy - 2, [".KKK.", "KYGgK", "KGgoK", ".KKK."],
                {"K": A.K, "Y": GOLD[6 + k], "G": GOLD[4 + k], "g": GOLD[2 + k], "o": GOLD[1]})

    def material(self, i, xx, yy, y0, y1, lift, night):
        return A.stone_matter(i, xx, yy, y0, y1, lift, night)

    def counter_cell(self, q, ox, oy, night):
        A.marble_cell(q, ox, oy, night)

    def counter_ink(self, night, dim):
        """A numeral laid in lapis tesserae on the marble; a leading nought in grey."""
        return RAMP["stone"][3] if dim else LAPIS[3]

    def timeline_line(self, p, x0, x1, y, night):
        """The vine the releases hang from, up to today."""
        if x1 - x0 >= 2:
            A.vine_line(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        A.grape_release(p, x, gy, kind, night, i)

    def today_mark(self, p, x, y, night):
        """A small peacock perched on the vine at today."""
        A.today_peacock(p, x, y, night)

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor as a portrait in mosaic with a jewelled diadem, robed in their own colour; a bot as a dove."""
        A.portrait(p, cx, cy, i, night, bot=not person.get("initials"))

    def commit_bar(self, p, x, y, w, fill, night):
        A.tile_bar(p, x, y, w, fill, night)

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """The seal's roundel of porphyry set with stones (see `art.jewelled_ring`); the check the layout sets in its
        disc is laid again in gold tesserae when the sheet is finished (see `art.gold_check`)."""
        A.jewelled_ring(p, cx, cy, r0, r1, night)
        p.seal = (cx, cy)

    def seal_mark(self, p, x, y, night):
        A.star_mark(p, x + 4, y - 1, night)

    def placard_board(self, p, night):
        """A panel inlaid in cut marble over the whole card (see `art.inlaid_panel`)."""
        p.sheet, p.night = "pl", night
        A.inlaid_panel(p, night)

    def placard_mark(self, p, x, y, night):
        A.disc(p, x, y - 2, RAMP["porphyry"], night)

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """The set's touch over a badge, kept inside its shape and off its letters: a rim of gold tesserae round it,
        lit along its top and left and shaded along its foot and right, a seam of gold where the label meets the
        value, and the grout of the tiles along the top row of its blocks where the letters leave room."""
        h = s["h"]
        ty = self._text_y(s)
        text_rows = range(ty - 1, ty + (7 if s["font"] == "57" else 5) + 1)

        def ins(x, y):
            return 0 <= x < w and 0 <= y < h and inside(x, y, w, h, s["corner"])
        row = h - 2 if (h - 2) % 4 != 2 else h - 3
        first = next((x for x in range(w) if ins(x, row) and ins(x, row - 1)), 0)
        edge = next((x for x in range(first + 2, w) if ins(x, row) and p.get(x, row) != p.get(x - 1, row)
                     and p.get(x, row - 1) != p.get(x - 1, row - 1)), w)
        for y in range(h):
            for x in range(w):
                if not ins(x, y):
                    continue
                if y == 0 or not ins(x - 1, y):
                    p.px(x, y, GOLD[5] if (x // 2) % 2 else GOLD[4])
                elif y == h - 1 or not ins(x + 1, y):
                    p.px(x, y, GOLD[2])
                elif x == edge:
                    p.px(x, y, GOLD[3])
                elif y == 1 and y not in text_rows and (x % 3 == 2):
                    try:
                        p.px(x, y, step(p.get(x, y), -1))
                    except KeyError:
                        pass

    def badge_label(self):
        """Deep blue tesserae, gold letters."""
        return (LAPIS[2], GOLD[5])

    def badge_gold(self):
        """A live badge's label: the deep gold of the ground's tesserae."""
        return (GOLD[3], A.K)

    def badge_states(self):
        """The stones a live badge shows its state in: green serpentine, a pale gold, red porphyry and grey marble."""
        return {"green": (RAMP["green"][2], C["white"]), "yellow": (GOLD[5], A.K),
                "red": (RAMP["porphyry"][3], C["white"]), "slate": (RAMP["stone"][2], C["white"])}

    def badge_swatches(self):
        """The stones and glass a written colour takes the nearest of."""
        R = RAMP
        return {"jasper": (R["red"][3], C["white"], None), "amber": (R["flame"][3], A.K, None),
                "ochre": (R["earth"][4], A.K, None),
                "gold": (GOLD[4], A.K, "tiles"), "serpentine": (R["green"][2], C["white"], None),
                "lapis": (LAPIS[5], C["white"], None), "porphyry": (R["purple"][3], C["white"], None),
                "marble": (R["pearl"][6], A.K, "veins"), "basalt": (LAPIS[0], C["white"], None),
                "grey": (R["stone"][2], C["white"], None), "earth": (R["earth"][2], C["white"], None),
                "teal": (R["teal"][2], C["white"], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        """Gold laid in tiles with their grout, and white marble with its grey veins, kept off the letters' rows."""
        if y in text_rows:
            return c
        if pattern == "tiles" and (x % 4 == 3 or y % 4 == 3):
            return GOLD[3]
        if pattern == "veins" and (x + 2 * y) % 9 == 0:
            return RAMP["pearl"][4]
        return c

    def badge_outline(self, pattern):
        return RAMP["pearl"][3] if pattern == "veins" else None

    def badge_shine(self, c, y, h):
        try:
            return step(c, 1) if y == 2 else step(c, -1) if y == h - 2 else c
        except KeyError:
            return c

    def plate_colours(self, mode):
        """A plate is a panel of gold tesserae by day, of lapis by night, its value on a block of lapis with gold
        letters by day and of porphyry with white by night; a live plate is gold."""
        if mode == "day":
            return dict(paper=TILE[5], dot=TILE[2], frame=A.K, block=LAPIS[2], ink=C["ink"], letters=GOLD[5])
        if mode == "night":
            return dict(paper=LAPIS[1], dot=LAPIS[3], frame=GOLD[3], block=RAMP["porphyry"][3], ink=C["ink_n"],
                        letters=C["white"])
        return dict(paper=GOLD[4], dot=GOLD[3], frame=A.K, edge=GOLD[1], ink=A.K)

    def plate_edge(self, block):
        return step(block, -1)


SET = Mosaic()
