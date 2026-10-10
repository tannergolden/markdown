# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Stronghold set: a castle's wall and its heraldry.

Every sheet is dressed limestone, battlemented along the top with a round tower at each corner, and a line
of heraldic pennants waves across it, pausing at the top centre where the month's mark hangs. Titles are carved
into the stone, and by night the carving is inlaid with gold; a glint passes along the title's gold now and then.
Headers stand on a castle above its moat, a gatehouse with its portcullis and drawbridge, or the great keep with
its curtain wall and gate: clouds drift and a hawk soars by day; by night the windows are candlelit, torches burn
and light the stone, a crescent moon hangs over the wall and a dragon crosses the sky trailing flame. A phone's
H1 has the whole stronghold across its width under the words, and its H2 and H3 stand their heroes under the words
across the phone, whatever the words say: the gatehouse at its full height with the knight riding to its gate, and
the great keep with its wall and gate, the knight riding to it from the watchtower. The footer stands on
the wall's footing, which rises where its cells leave it room, with the stronghold's banner hung on the wall
between two torches; links are shields hung on battlements; badges are iron-banded plates; and the elements are
built of stone, rope, pennants, shields, helms and wax. The design is drawn in the medieval collection's hand
(`collections.hand`): its words in the hand's inks, its stone within the hand's grounds, its fires on the hand's
flame and its moon the hand's.
"""
from __future__ import annotations

from ...holidays.designs import WIDE
from ...holidays.designs.badges import inside
from ...holidays.pixel import Pix, sphere, tube
from ..hand import CollectionSet
from . import art as A
from .palette import C, NIGHT_SKY, RAMP, TINCTURES, TOKENS, X, step

LINK_SPRITES = ("tower", "crown", "fleur", "swords")
# The tinctures a contributor's shield and plume come in, by turns.
AVATARS = ("gules", "azure", "vert", "purpure")
SHEET_RULE = 20   # the row an element's sheet rules off its tag and title at
KEEP_X = 354      # where an H3's great keep and its wall begin: two units clear of the furthest its words reach
KEEP_MOST = 120   # the most rows over the water the great keep rises: enough for the tallest strip


class Stronghold(CollectionSet):
    collection = "medieval"
    key = "medieval-stronghold"
    name = "Stronghold"
    # What the design is, in words, for the page that shows the collection.
    tagline = (
        "Castle stone: carved titles, waving pennants, torches and a dragon by night.")
    about = (
        "Every sheet is a wall of dressed limestone, warm by day and moonlit blue-grey by night, battlemented "
        "along its top with open crenels and a round tower at each corner, while a line of red, gold, blue and "
        "white pennants ripples across it in the wind. Titles are carved into the stone, the cut's lit wall "
        "catching the light along each stroke, and by night the carving is inlaid with gold, a glint passing along "
        "it now and then. The headers stand on a castle on its crag above the moat, its drawbridge down on its "
        "chains, on a gatehouse with a half-lowered portcullis, or on the great keep, its parapet on corbels and "
        "its banner flying over the curtain wall and its gate. On a phone the whole stronghold stands across the "
        "width under the words, the watchtower, the castle and a mounted knight on the far bank; a section's "
        "phone stands the gatehouse there at its full height, the knight riding to its gate, and a strip's the "
        "great keep with its wall and gate, the knight riding to it from the watchtower. Clouds drift "
        "and a hawk soars by day, and by night candlelight flickers in the windows, torches throw their light onto "
        "the stone and shiver on the water, a crescent moon hangs over the wall and a dragon crosses the sky "
        "trailing flame before it dives behind the keep. The footer stands on the wall's footing, rising where "
        "the cells leave it room, and the stronghold's banner of the gold lion hangs on the wall between two "
        "torches, burning by night. The links are battlemented shields with a bevelled face and a bold charge, and "
        "the badges are iron-banded plates with blackened-iron labels. The elements carry the heraldry through: "
        "stone tablets riveted with iron, courses of stone, a riveted dial with a steel boss, pennants on a knotted "
        "rope with a jewelled crown at today, plumed great helms over shields in four tinctures, a red wax seal "
        "with a gold lion, and oak inn signs hanging from a riveted bracket.")
    tokens = frozenset(TOKENS)

    # ---- drawing lighter
    def canvas(self, w, h):
        """A new drawing. One made lighter to fit its budget thins only texture a reader does not miss at 1x
        (see `art.THIN`), so the canvas itself stays at full weight: a title keeps its glow, and the last pass
        still lights the stone and lays the towers' courses."""
        p = Pix(w, h)
        if self._lite:
            A.THIN.add(p)
        return p

    # ---- colour and paper
    def ink(self, night):
        S, Sl, G, R = RAMP["stone"], RAMP["slate"], RAMP["gold"], RAMP["gules"]
        return dict(
            title=G[3] if night else X["recess"], shadow=Sl[5] if night else S[6],
            body=C["ink_n"] if night else C["ink"], muted=X["muted_night"] if night else X["muted_day"],
            rule=Sl[3] if night else S[3], accent=G[4] if night else R[2],
            tag=R[2], tag_ink=G[4],
            fill=C["fill_n"] if night else C["fill"], dim=X["dim_night"] if night else X["dim_day"],
        )

    def lit(self, night):
        """By night the carved letters are inlaid with gold that glows faintly; by day they are bare stone.
        (`title_text` draws the cut round them first.)"""
        if night:
            return dict(paint=A.INLAY, glow=(RAMP["gold"][4], (0.14,)), night=True)
        return dict(night=False)

    def paper(self, p, night, uid="p"):
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        if not night:
            return C["paper"]
        return NIGHT_SKY[min(len(NIGHT_SKY) - 1, int(y * len(NIGHT_SKY) / p.h))]

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        """Fewer stars than the kit asks for: the sky over a wall is busy enough with its towers."""
        A.stars(p, x0, y0, x1, y1, max(4, round(n * 0.6)), seed=seed, twinkling=twinkling, faint=faint, avoid=avoid)

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The wall, by night under its stars, kept off the month's mark's box at the top centre; by day, across a
        wide header, clouds drifting behind everything. A still drawing leaves them where they lie; a phone's
        header has none."""
        super().sky(p, night, y1, seed=seed, motion=motion, avoid=(*avoid, A.mark_box(p)))
        if not night and p.w == WIDE:
            A.clouds(p, 4, 23, p.w - 4, min(y1, 64), 7, seed=seed + 11, motion=motion)

    def frame(self, p, night, webs=False):
        """The border: corner towers on a header, and on a footer (the one short sheet) a plinth at the foot."""
        A.frame(p, night, towers=webs, plinth=not webs and p.h < 60)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """Pennants along a cord across the sheet. The cord sags two rows at the most, so the lowest pennant
        hangs two rows clear of the title's dimension."""
        A.pennants(p, x0 + 3, x1 - 3, y, sag=min(sag, 2), span=span, spacing=spacing, night=night, seed=seed)

    def tag(self, p, x, y, w, h, night):
        """The gules block a tag's gold letters sit on: lit along its top, shaded along its foot. The ribbon
        under a certificate's seal, the one tag set low on its sheet, is a banner with forked tails, as long
        as its column has room for them."""
        R = RAMP["gules"]
        p.rect(x, y, w, h, R[2])
        p.hline(x, x + w, y, R[4])
        p.hline(x, x + w, y + h - 1, R[0])
        if y >= 30 and h >= 9:
            tail = min(5, x - 6, (100 if p.w == WIDE else 88) - 2 - (x + w))
            if tail >= 3:
                A.banner_tails(p, x, y, w, h, night, tail=tail)

    def title_text(self, p, x, y, s, night, scale):
        """Letters carved into the stone: the cut's wall that turns from the light dark along each stroke's
        upper left, the wall that catches it lit along the lower right, and the floor of the cut a shade
        lighter than that shaded wall. By day a hairline of gold inlay runs along the lit edge; by night the
        whole cut is inlaid with gold, glowing faintly, with a glint here and there that twinkles."""
        k = self.ink(night)
        S, Sl, G = RAMP["stone"], RAMP["slate"], RAMP["gold"]
        lit = self.lit(night)
        if night:
            # The shaded wall would be lost on the night stone, and a glow is half a pixel at the smallest size.
            A.carve(p, x, y, s, scale, None, Sl[5])
            if scale < 3:
                lit.pop("glow", None)
        else:
            A.carve(p, x, y, s, scale, S[0], C["white"], hair=G[3])
        at = len(p.uses["base"])
        w = p.text(x, y, s, k["title"], "57", scale, **lit)
        A.as_line(p, at, x, y, s, scale)
        if scale >= 2:
            A.glints(p, x, y, s, scale, night)
        return w

    # ---- the headers' scenes
    def section_mark(self, p, x, y, night):
        """The shield and swords beside SECTION A-A, from two rows above the words to four under them: two
        clear of the title's foot above and of the tagline below."""
        A.section_mark(p, x, y, night)

    def strip_mark(self, p, x, y, night):
        """The achievement beside a strip's title, raised so that its shield's foot stays two rows clear of
        the tagline under the title."""
        A.arms(p, x, y - 11, night)

    def _sky_life(self, p, box, night, motion, hawk, moon=None, dragon=None):
        """What lives in the sky over a scene, where no word stands: a hawk soaring by day; by night the
        moon and a dragon crossing, diving out of sight behind the castle."""
        if not p.clear_of_words(*box):
            return
        if night:
            if moon:
                A.moon(p, *moon)
            if dragon:
                start, hide, clip, toward = dragon
                A.dragon(p, start, hide, clip, motion=motion, toward=toward)
        else:
            cx, cy, rx, ry, seed = hawk
            A.hawk(p, cx, cy, rx, ry, motion=motion, seed=seed)

    def scene(self, design, p, rule, night, motion):
        g = rule - 1
        if design == "H1":
            # The castle's towers stand within x 56 and the guard's within x 355 and 413; each side is built
            # to the rows its words leave free.
            spans = []
            room = self._room(p, 4, 56, g, 76, 26)
            if room:
                spans.append(A.castle(p, 5, g, night, motion, phase=0, room=room))
            room = self._room(p, 355, 413, g, 76, 24)
            if room:
                spans.append(A.guard(p, 357, g, night, motion, phase=2, room=room))
            self._sky_life(p, (22, 14, 70, 36), night, motion, hawk=(44, 22, 12, 4, 4),
                           dragon=((34, 12), (50, g - 15), (4, 10, 78, g - 1), 1), moon=None)
            if night and p.clear_of_words(370, 17, 396, 42):
                A.moon(p, 382, 29, 7)
            return spans
        if design == "H2":
            spans = []
            room = self._room(p, 305, 401, g, 70, 20)
            if room:
                spans.append(A.gatehouse(p, 353, g, night, motion, phase=0, room=room))
            self._sky_life(p, (294, 14, 411, 34), night, motion, hawk=(352, 24, 22, 5, 7),
                           dragon=((336, 16), (341, g - 18), (294, 13, 411, g - 1), -1), moon=(304, 38, 6))
            return spans
        # The great keep at the strip's right, its banner's head kept two rows under the pennants, and the curtain
        # wall and its gate where the words leave the room to its left.
        x1 = WIDE - 4
        room = self._room(p, x1 - A.KEEP_W - 4, x1, g, min(KEEP_MOST, g - 15), A.KEEP_LEAST)
        if not room:
            return []
        x0 = KEEP_X
        left = self._room(p, x0, x1 - A.KEEP_W - 4, g, room, 24)
        return [A.great_keep(p, x0, x1, g, night, motion, phase=1, room=room, left=left)]

    @staticmethod
    def _room(p, x0, x1, g, most, least):
        """The rows free of words above the water's surface at row g between x0 and x1, `most` at the most,
        keeping three rows of margin above and two beside; None when fewer than `least` are free."""
        for room in range(most, least - 1, -1):
            if p.clear_of_words(x0 - 2, g - room - 3, x1 + 2, g + 3):
                return room
        return None

    PHONE_SCENE = 60    # the rows a phone's H1 gives its stronghold under its words and its notes

    def h1_narrow(self, h, night):
        """A phone's H1, its stronghold given PHONE_SCENE rows under the words and the notes set under them, however
        many notes there are."""
        self.phone_scene_rows = self.PHONE_SCENE + 4 + 10 * len(self.said(h))
        try:
            return super().h1_narrow(h, night)
        finally:
            del self.phone_scene_rows

    def scene_narrow(self, design, p, y, night):
        """A phone's H1 scene, built to the rows its words leave free over it: the stronghold across the whole width
        under the words (`art.phone_castle`), the hawk soaring over it by day and the moon by night; where fewer rows
        are free than its smallest build needs, nothing stands. A phone's H2 and H3 stand their heroes under their
        words instead (see `scene_under`)."""
        if design == "H1":
            g = y - 1
            room = self._room(p, 5, p.w - 5, g, self.PHONE_SCENE - 2, A.PHONE_LEAST)
            span = room and A.phone_castle(p, g, night, room)
            if span:
                A.MOATS[p] = [span]
                self._sky_life(p, (8, g - room - 2, 60, g - room + 14), night, False,
                               hawk=(40, g - room + 6, 10, 3, 4), moon=(16, g - room + 7, 5))

    # ---- a phone's hero under its words
    # The rows a phone's H2 and H3 ask for under their words, whatever the words: room for the gatehouse at its full
    # height with its banners flying, and for the great keep drawn to a phone's width, both kept clear of the words
    # over them whether those end in a note or in a line.
    UNDER = {"H2": 63, "H3": 62}
    HERO_LEAST = 44     # the fewest rows over the water a phone's hero stands in: the hand's least for it

    def phone_rows(self, design, title_w):
        """The rows a phone's H2 or H3 leaves under its words for its hero, whatever the words say: a hero at its full
        height would reach into the pennants beside the words, so it always stands under them (see
        `scene_under`)."""
        return self.UNDER[design]

    def scene_under(self, design, p, y0, y1, night):
        """A phone's hero under its words, across the phone, standing on the rule at y1 and built to the rows free
        over it: on H2 the gatehouse at its full height with its keep's tower, its sentry and its banners, the
        knight riding to its gate (`art.phone_gate`); on H3 the great keep with its curtain wall, its gate and its
        drum tower, the watchtower and its sentry at the left and the knight riding between them
        (`art.phone_keep`). Over the knight a hawk soars by day, and by night the moon hangs, and on H2 the dragon
        flies toward the gatehouse breathing fire, where no word comes within two units of them. By night the
        torches burn and light the stone and the water. The rule's ivy keeps off the moat."""
        g = y1 - 1
        if design == "H2":
            room = self._room(p, 5, p.w - 5, g, A.GATE_FULL, self.HERO_LEAST)
            if room:
                A.MOATS[p] = [A.phone_gate(p, g, night, room)]
                self._sky_life(p, (6, g - room, 66, g - 38), night, False, hawk=(36, g - room + 12, 10, 3, 7),
                               moon=(20, g - room + 12, 6), dragon=((62, g - room + 6), None, None, 1))
        else:
            room = self._room(p, 5, p.w - 5, g, A.KEEP_PHONE, self.HERO_LEAST)
            if room:
                A.MOATS[p] = [A.phone_keep(p, g, night, room)]
                self._sky_life(p, (40, g - room, 100, g - 38), night, False, hawk=(70, g - room + 12, 10, 3, 4),
                               moon=(64, g - room + 12, 6))

    def rule_decor(self, p, x0, x1, y, seed, night):
        """Ivy along a rule, sparser on a sheet's own rule under its tag and title, and none where the moat of a
        phone's scene under its words, or of its H1's stronghold, lies on the rule."""
        every = (34, 60) if y <= SHEET_RULE else (22, 44)
        for a, b in self._spans(x0, x1, A.MOATS.get(p, ())):
            A.ivy(p, a, b, y, seed=seed if a == x0 else seed + a, night=night, every=every)

    def finish(self, p, night):
        """The last pass: by night the torches' light on the stone near them; then every tower's body laid as a
        pattern of its courses, and the letters a title's line now places let go of, which look the same in
        fewer bytes (see `art.lay_courses` and `art.unplaced_letters`)."""
        if night:
            A.lamplight(p)
        A.lay_courses(p)
        A.unplaced_letters(p)

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        """A torch in its iron bracket at the corner of the closing notes, lit by night."""
        A.sconce(p, x + 2, y - 1, night, phase=1)

    def _footed(self, p, night, last=False):
        """A footer once its cells are laid: the footing of the wall along its foot, rising where the cells leave it
        room, and the stronghold's banner hung on the wall between its torches where they leave it free (see
        `art.footing`): on a title block only after its `last` cell, the way back up."""
        after = max((b[2] for b in p.words), default=0) + 4 if last else 0
        A.footing(p, night, self.ink(night)["rule"], after=after)
        return p

    def f1(self, ft, night):
        return self._footed(super().f1(ft, night), night, last=True)

    def f2(self, ft, night):
        return self._footed(super().f2(ft, night), night)

    def f1_narrow(self, ft, night):
        return self._footed(super().f1_narrow(ft, night), night, last=True)

    def f2_narrow(self, ft, night):
        return self._footed(super().f2_narrow(ft, night), night)

    def heart(self, p, x, y):
        A.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        """A field chequy gules and or, lit along the top and shaded along the foot."""
        A.chequy(p, x0, y0, w, h, period)

    def link_colours(self, night):
        """A gules face in a rim of iron by day and of gold by night, gold letters, and shade along the foot."""
        R, I, G = RAMP["gules"], RAMP["iron"], RAMP["gold"]
        if night:
            return R[1], G[3], G[4], R[0]
        return R[2], I[1], G[4], R[0]

    def link_top(self, p, x0, x1, y, seed, night):
        """The button finished as a shield hung on a battlement: merlons along its top in the rim's metal,
        and its face bevelled, lit along the top and down the left, shaded down the right."""
        fill, edge, _, shade = self.link_colours(night)
        lit = step(fill, 1)
        for xx in range(x0, x1):
            k = (xx - x0) % 4
            if k != 3:
                p.px(xx, y - 2, edge)
                p.px(xx, y - 1, lit if k == 1 else edge)
        p.hline(1, p.w - 1, y + 1, lit)
        p.vline(1, y + 1, y + 9, lit)
        p.vline(p.w - 2, y + 2, y + 9, shade)

    def link_icon(self, index, night, ink):
        return A.ICONS[LINK_SPRITES[index % len(LINK_SPRITES)]], A.icon_pal(night, ink)

    # ---- the elements
    def card_bevel(self, night):
        return (RAMP["slate"][4], RAMP["slate"][0]) if night else (C["white"], RAMP["stone"][4])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A card as a stone tablet: a dressed slab right of its icon's cell, an iron band riveted down the
        cell's edge, and an iron plate riveted over each corner."""
        I = RAMP["iron"]
        A.tablet_card(p, x, y, w, h, night)
        for yy in range(y + 1, y + h - 1):
            p.px(x + 10, yy, I[4])
            p.px(x + 11, yy, I[6] if (yy - y) % 3 == 2 else I[3])
            p.px(x + 12, yy, I[1])

    def wire_ink(self, night):
        return RAMP["wood"][3] if night else RAMP["wood"][4]

    def wire_lights(self, p, cells, night, seed):
        """The wire as a rope, with bunting along it: a small pennant every twelfth pixel, in the tinctures by
        turns, hanging under a level rope and beside an upright one."""
        A.rope_over(p, cells, night)
        for i, (x, y, d) in enumerate(cells[5:-7]):
            if i % 12:
                continue
            tincture = TINCTURES[(i // 12 + seed) % len(TINCTURES)]
            key = ("bunting", tincture, d, night)
            if key not in p.syms:
                R = RAMP[tincture]
                k = -1 if night else 0
                if d == "h":
                    cells_ = {(-1, 1): R[5 + k], (0, 1): R[4 + k], (1, 1): R[3 + k], (-1, 2): R[4 + k],
                              (0, 2): R[3 + k], (0, 3): R[3 + k]}
                else:
                    cells_ = {(-1, -1): R[5 + k], (-2, -1): R[4 + k], (-3, -1): R[3 + k], (-1, 0): R[4 + k],
                              (-2, 0): R[3 + k], (-1, 1): R[3 + k]}
                p.symbol(key, cells_)
            p.use(key, x, y)

    def dashes(self, night):
        return [RAMP["gules"][4 if night else 3], RAMP["gold"][4 if night else 3]]

    def ornament(self, kind, p, x, y, night):
        """A knight's achievement in a free corner of the schematic: a helm over a shield with crossed swords."""
        if kind == "schematic":
            if p is not None:
                A.arms(p, x, y + 10, night)
                A.helm(p, x + 7, y, "gules", night)
            return (26, 36)
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as courses of stone blocks stood up from the base line."""
        A.courses(p, bx, base - v, bw, v, night)

    def peak_mark(self, p, x, y, night):
        A.crown(p, x, y + 1, night)

    def dial_ring(self, p, arc, night):
        """A riveted iron ring bent over the dial."""
        I = RAMP["iron"]
        k = -1 if night else 0

        def colour(s, o, lam, x, y):
            if int(s) % 7 == 3 and abs(o) < 0.45:
                return I[6 + k]
            return I[max(1, min(5, round(1.6 + 3.4 * lam) + k))]
        tube(p, arc, 2.6, colour, outline=I[0])

    def dial_tick(self, p, x, y, night):
        p.px(x, y, RAMP["gold"][4])
        p.px(x + 1, y + 1, RAMP["gold"][1])

    def dial_hub(self, p, cx, cy, night):
        """A shield boss: a steel dome on a gold base."""
        sphere(p, cx + 0.5, cy - 0.5, 3.0, RAMP["argent"], lo=1, hi=6)
        G = RAMP["gold"]
        for i, xx in enumerate(range(cx - 4, cx + 5)):
            p.px(xx, cy + 2, G[5] if i < 3 else G[4] if i < 7 else G[2])

    def material(self, i, xx, yy, y0, y1, lift, night):
        """Fields of the arms by turns: chequy gules and or, bendy azure and argent, vert semy of gold,
        barry purpure and argent, and ermine."""
        R, G, Az, Ar, V, P, I = (RAMP[n] for n in ("gules", "gold", "azure", "argent", "vert", "purpure", "iron"))
        kind = i % 5
        if kind == 0:
            c = R[3] if ((xx // 3) + (yy // 3)) % 2 == 0 else G[3]
        elif kind == 1:
            c = Ar[5] if (xx + yy) % 6 < 2 else Az[2]
        elif kind == 2:
            c = G[4] if (xx % 6 == 2 and yy % 4 == 1) or (xx % 6 == 5 and yy % 4 == 3) else V[2]
        elif kind == 3:
            c = Ar[4] if (yy - y0) % 4 < 2 else P[2]
        else:
            c = I[1] if (xx * 7 + yy * 5) % 13 == 0 else Ar[6]
        return step(c, lift)

    def counter_cell(self, q, ox, oy, night):
        A.tablet(q, ox, oy, night)

    def counter_ink(self, night, dim):
        """A numeral cut into the tablet, inlaid with gold by night; a leading nought cut shallower."""
        if night:
            return RAMP["slate"][5] if dim else RAMP["gold"][3]
        return RAMP["stone"][3] if dim else RAMP["stone"][1]

    def timeline_line(self, p, x0, x1, y, night):
        """The rope the releases stand on, up to today, with a knot every so often."""
        if x1 - x0 >= 3:
            tube(p, [(x0, y + 1.5), (x1, y + 1.5)], 1.6, A.rope_colour(night), outline=RAMP["wood"][0])
            for x in range(x0 + 13, x1 - 4, 26):
                A.knot(p, x, y + 1, night)

    def release(self, p, x, gy, kind, night, i=0):
        """A pennant on a pole for a release, a square banner for a big one, a smaller pennant for a patch,
        an outlined one for a release still to come, and a tower for the repository's founding."""
        tincture = TINCTURES[i % len(TINCTURES)]
        if kind == "minor":
            R = RAMP[tincture]
            k = -1 if night else 0
            p.vline(x, gy - 5, gy + 1, RAMP["iron"][4 + k])
            for j in range(3):
                for dx in range(1, 5 - j):
                    p.px(x + dx, gy - 5 + j, R[max(0, (5 if j == 0 else 4 if dx < 4 - j else 3) + k)])
        else:
            A.pennant_flag(p, x, gy, tincture, night, kind=kind)
        if kind in ("major", "big", "minor"):
            A.knot(p, x, gy + 1, night)     # the pole lashed to the rope

    def today_mark(self, p, x, y, night):
        """A crown, 7 by 6, over the rope's end at today."""
        A.crown_big(p, x - 3, y - 7, night)

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor: a heater shield in their tincture, a small gold charge in its chief and their
        initials on it, under a great helm with a plume of the same tincture; a bot is a steel shield with a
        cross under a helm with its visor shut."""
        G, Ar, I = RAMP["gold"], RAMP["argent"], RAMP["iron"]
        k = -1 if night else 0
        bot = not person.get("initials")
        name = "argent" if bot else AVATARS[i % len(AVATARS)]
        R = RAMP[name]
        for j in range(15):
            half = 7 if j < 9 else 7 - (j - 8)
            for xx in range(cx - half, cx + half + 1):
                u = (xx - cx + half) / max(1, 2 * half)
                t = 5 if u < 0.1 else 4 if u < 0.5 else 3 if u < 0.9 else 1
                if j == 0:
                    t = min(6, t + 1)
                p.px(xx, cy - 7 + j, R[max(0, t + k)])
            p.px(cx - half - 1, cy - 7 + j, R[0])
            p.px(cx + half + 1, cy - 7 + j, R[0])
        p.px(cx, cy + 8, R[0])
        if bot:
            for j in range(1, 11):
                p.px(cx, cy - 7 + j, I[3])
            for xx in range(cx - 4, cx + 5):
                p.px(xx, cy - 4, I[3])
            A.helm(p, cx - 5, cy - 18, "argent", night)
            p.hline(cx - 2, cx + 3, cy - 15, I[1])
            return
        A.charge(p, cx - 3, cy - 6, i, night)
        ini = str(person["initials"])[:2]
        if name == "gules":
            p.text(cx - 3, cy - 1, ini, G[4 + k], "35", shadow=R[0])
        else:
            p.text(cx - 3, cy - 1, ini, Ar[6], "35", shadow=R[0])
        A.helm(p, cx - 5, cy - 18, name, night)

    def commit_bar(self, p, x, y, w, fill, night):
        """A contributor's share, chequy gules and or."""
        p.box(x, y, w + 2, 4, self.wire_ink(night))
        A.chequy(p, x + 1, y + 1, fill, 2, period=2)

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """Red wax round the seal's pressed centre."""
        A.wax(p, cx, cy, r0, r1, night)

    def seal_mark(self, p, x, y, night):
        A.fleur(p, x + 2, y, night)

    def placard_board(self, p, night):
        A.inn_sign(p, night)

    def placard_mark(self, p, x, y, night):
        A.shield(p, x, y - 4, "azure", night, charge="cross")

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """The set's touch over a badge, kept inside its shape and off its letters: an iron band riveted
        along the top, a rivet at each corner, the plate's lower edge in shadow, and the two blocks bevelled
        as plates, lit along their top and left, shaded along their foot and right, with a seam between the
        label's iron and the painted enamel of the value."""
        I = RAMP["iron"]
        h = s["h"]
        ty = self._text_y(s)
        text_rows = range(ty - 1, ty + (7 if s["font"] == "57" else 5) + 1)

        def ins(x, y):
            return 0 <= x < w and 0 <= y < h and inside(x, y, w, h, s["corner"])
        # Where the label's block ends: the first change of colour along a row under the letters.
        row = h - 2 if (h - 2) % 4 != 2 else h - 3
        first = next((x for x in range(w) if ins(x, row)), 0)
        edge = next((x for x in range(first + 1, w) if ins(x, row) and p.get(x, row) != p.get(first, row)), w)
        if edge == w and p.get(first, row) not in (self.badge_label()[0], self.badge_gold()[0]):
            edge = 0                                    # a value and no label: enamel from end to end
        for y in range(h):
            for x in range(w):
                if not ins(x, y):
                    continue
                if y <= 1:
                    rivet = (x in (1, w - 2) or x % 8 == 4) and ins(x, 0) and ins(x, 1)
                    p.px(x, y, (I[6] if rivet else I[4]) if y == 0 else (I[1] if rivet else I[2]))
                    continue
                if y == h - 1:
                    p.px(x, y, I[1])
                    continue
                c = p.get(x, y)
                try:
                    if y == 2 and y not in text_rows:
                        p.px(x, y, step(c, 1))
                    elif y == h - 2 and x not in (1, w - 2):
                        p.px(x, y, step(c, -1))
                    elif not ins(x - 1, y) or x == edge:
                        p.px(x, y, step(c, 1))
                    elif not ins(x + 1, y) or x == edge - 1:
                        p.px(x, y, step(c, -1))
                except KeyError:
                    pass
        for x in (1, w - 2):
            if ins(x, h - 2) and ins(x, h - 1):
                p.px(x, h - 2, I[6])

    def badge_label(self):
        return (RAMP["iron"][1], RAMP["argent"][5])

    def badge_gold(self):
        return (RAMP["gold"][2], RAMP["iron"][0])

    def badge_states(self):
        return {"green": (RAMP["vert"][2], C["white"]), "yellow": (RAMP["gold"][4], RAMP["iron"][0]),
                "red": (RAMP["gules"][3], C["white"]), "slate": (RAMP["iron"][4], C["white"])}

    def badge_swatches(self):
        R, G, Az, Ar, V, P, I, W = (RAMP[n] for n in ("gules", "gold", "azure", "argent", "vert", "purpure", "iron",
                                                       "wood"))
        return {"gules": (R[3], C["white"], None), "tenne": (RAMP["tenne"][3], I[0], None), "or": (G[3], I[0], None),
                "vert": (V[2], C["white"], None), "azure": (Az[2], C["white"], None),
                "purpure": (P[2], C["white"], None), "argent": (Ar[6], I[1], "ermine"),
                "sable": (I[1], C["white"], None), "steel": (I[4], C["white"], None), "oak": (W[2], C["white"], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        if pattern == "ermine" and (x * 7 + y * 13) % 23 == 0 and y not in text_rows:
            return RAMP["iron"][1]
        return c

    def badge_outline(self, pattern):
        return RAMP["argent"][3] if pattern == "ermine" else None

    def badge_shine(self, c, y, h):
        try:
            return step(c, 1) if y == 2 else step(c, -1) if y == h - 1 else c
        except KeyError:
            return c

    def plate_colours(self, mode):
        """A plate is an iron plate: blackened iron pitted with rivets by day, the same iron blued by
        moonlight at night, the value painted on it in gules with gold letters; a live plate is brass."""
        G, R, I, Sl, A_ = RAMP["gold"], RAMP["gules"], RAMP["iron"], RAMP["slate"], RAMP["argent"]
        if mode == "day":
            return dict(paper=I[1], dot=I[2], frame=I[3], block=R[2], ink=A_[5], letters=G[4])
        if mode == "night":
            return dict(paper=Sl[1], dot=Sl[2], frame=Sl[5], block=R[2], ink=C["ink_n"], letters=G[4])
        return dict(paper=G[3], dot=G[2], frame=I[0], edge=G[1], ink=I[0])

    def plate_edge(self, block):
        return step(block, -1)


SET = Stronghold()
