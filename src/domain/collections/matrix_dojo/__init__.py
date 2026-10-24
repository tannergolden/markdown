# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Dojo set: the training program, May's design in the Matrix collection, drawn in the collection's hand.

Every sheet is a wall of shoji, honey paper behind a lattice of pale hinoki by day and by night the same paper glowing
deep indigo with the city's light behind it, the kumiko standing out against it in silhouette. Black lacquered beams
frame it with gold fittings at their joints, the edge of a tatami runs along its foot, its black brocade worked in
gold, and along a header's top hangs a shimenawa of twisted straw with its zigzags of white paper, parting either side
of the month's mark. Titles are black lacquer edged in gold leaf, brushed, the dry brush breaking at a stroke's end;
by night they are gold leaf ringed in lacquer, catching the light; and in a moving header the terminal's beam passes
down them on the hand's period. Cherry petals drift across the sky of every header behind its title. An H1 is the
training program: at the left a fighter in a dark gi at the top of a flying kick, his afterimages trailing behind him,
over a byobu laid in gold leaf and painted with a great wave, a paper lantern written in the code hanging by him; and
across the floor his opponent waiting in his guard under a great round window onto the city, beside a stone lantern
that by night burns phosphor and pools its light on the tatami. An H2 sets the two of them before a byobu painted with
a great pine at the right, the kick at the guard, the stone lantern by them, risen as tall as the words leave room;
an H3 slides the shoji open on the garden at the right, where a pagoda rises nearly the strip's full height among
cherry blossom, under the moon and the code by night. The dojo's crest, a cherry blossom of gold leaf, stands beside
SECTION A-A and a strip's title, and petals lie fallen along the rules. A phone's H1 has the whole dojo across its
width under the words, and its H2 and H3 stand the clash before the pine and the pagoda in its window under the words
across the phone, whatever the words say. A footer stands on the dojo's floor, a dais of hinoki rising where its cells
leave it room, with the alcove after a title block's last cell, a hanging scroll brushed with 力 between two paper
lanterns that burn by night; the crest sits at the corner of the closing notes, the heart is vermilion lacquer and the
graphic scale a lacquered scabbard. Links are lacquered tablets hung from a straw rope; badges carry the rope along
their top over lacquered blocks; the elements are lacquered boxes, silk cords with paper lanterns, bamboo, a taiko's
rim, dyed textiles, name plates of hinoki, banners hung from the rope and the vermilion of a seal; and the games are
played on tatami and vermilion lacquer in a frame of black lacquer, the Hall's podium black lacquer hung with banners.
The design is drawn in the Matrix collection's hand (`collections.hand`): its words in the hand's inks, its paper
within the hand's grounds, every light on the hand's phosphor and its moon the hand's.
"""
from __future__ import annotations

from ...holidays.designs.badges import inside
from ...holidays.designs.materials import Podium, Stuff
from ...holidays.pixel import sphere
from ..hand import CollectionSet
from .. import rain
from . import art as A
from .palette import C, RAMP, TOKENS, X, step

GOLD, LACQUER, HINOKI, WASHI = RAMP["gold"], RAMP["lacquer"], RAMP["hinoki"], RAMP["washi"]


class Dojo(CollectionSet):
    key = "matrix-dojo"
    name = "Dojo"
    collection = "matrix"
    tagline = ("A dojo of shoji and tatami: lacquer and gold-leaf titles, drifting petals, a flying kick and lanterns "
               "burning by night.")
    about = (
        "A dojo built of shoji: honey paper behind a lattice of pale hinoki by day, and by night the same paper "
        "glowing deep indigo with the city's light behind it, the kumiko standing out against it in silhouette. Black "
        "lacquered beams frame every sheet with gold fittings at their joints, the edge of a tatami runs along the "
        "foot in black brocade worked in gold, and a shimenawa of twisted straw hangs along the top with its zigzags "
        "of white paper. Titles are black lacquer edged in gold leaf and brushed, the dry brush fraying at a stroke's "
        "end, and by night they are gold leaf catching the light, while cherry petals drift across the sky behind "
        "them. The H1 is the training program: a fighter in a dark gi at the top of a flying kick, his afterimages "
        "trailing behind him, over a byobu laid in gold leaf and painted with a great wave, a paper lantern written in "
        "the code hanging by him; and across the floor his opponent waiting in his guard under a great round window "
        "onto the city of code, beside a stone lantern that by night burns phosphor and pools its light on the "
        "tatami. A section's header sets the two of them before a byobu painted with a great pine, the kick at the "
        "guard; a strip's slides the shoji open on the garden, where a pagoda rises among cherry blossom under the "
        "moon. On a phone the whole dojo stands across the width under the words, and a section's and a strip's "
        "phones stand the clash and the pagoda there. Footers stand on the dojo's floor, a dais of hinoki rising "
        "where the cells leave room and the alcove after the last cell, a hanging scroll between two paper lanterns; "
        "links hang from a straw rope; badges carry the rope over lacquered blocks; and the elements are lacquered "
        "boxes, silk cords hung with paper lanterns, bamboo, a taiko's rim, dyed textiles, name plates of hinoki, "
        "banners on the rope and a vermilion seal. The games are played on tatami and vermilion lacquer in a frame of "
        "black lacquer, and the Hall of Fame's podium is black lacquer hung with banners.")
    tokens = frozenset(TOKENS)
    trophy_frame = (4, 4, 4, 5)     # the frame's posts, beam and tatami four deep, its gold fittings five square

    # ---- colour and paper
    def ink(self, night):
        """The words in the hand's two inks; the titles in black lacquer by day and gold leaf by night."""
        return dict(
            title=GOLD[4] if night else LACQUER[1], shadow=LACQUER[0] if night else HINOKI[4],
            body=self.hand.body[night], muted=self.hand.muted[night],
            rule=X["rule_night"] if night else X["rule_day"], accent=GOLD[4] if night else RAMP["red"][2],
            tag=GOLD[3] if night else LACQUER[2], tag_ink=LACQUER[0] if night else GOLD[5],
            fill=WASHI[3] if night else RAMP["paper"][6], dim=X["dim_night"] if night else X["dim_day"],
        )

    def paper(self, p, night, uid="p"):
        p.sheet = uid
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        return A.bg_at(p, night, y)

    def _finish(self, p, night):
        """The last pass, which a drawing made lighter keeps too: the file written as lightly as it can be, the same
        drawing unit for unit, the month's mark left as it is drawn (see `Pix.compact`)."""
        if not p.lite:
            self.finish(p, night)
        p.compact(keep=("mark",))

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The shoji alone: a dojo has no sky."""
        self.paper(p, night)

    def frame(self, p, night, webs=False):
        A.frame(p, night, header=webs)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """The shimenawa along the top, parting either side of the month's mark."""
        A.shimenawa(p, x0, x1, night, self.mark_box(p), self.marked, span=span, sag=min(sag, 3))

    def tag(self, p, x, y, w, h, night):
        """A block of black lacquer by day, of gold leaf by night, a note's number knocked out of it."""
        p.rect(x, y, w, h, GOLD[3] if night else LACQUER[2])
        p.hline(x, x + w, y, GOLD[5] if night else LACQUER[4])

    def title_text(self, p, x, y, s, night, scale):
        """Black lacquer edged in gold leaf by day, gold leaf by night (see `art.lacquer_title`). The drawing keeps
        each line, for the scan that passes down it in a moving header."""
        w = A.lacquer_title(p, x, y, s, scale, night)
        p.titles = getattr(p, "titles", []) + [(x, y, s, scale, w)]
        return w

    # ---- the headers' scenes
    def section_mark(self, p, x, y, night):
        """The dojo's crest beside SECTION A-A, a cherry blossom of gold leaf, from a row above the words to three
        under them: two clear of the title's foot above and of the tagline below."""
        A.crest(p, x + 4, y + 4, 4.2, night, disc=False)

    def strip_mark(self, p, x, y, night):
        """The dojo's crest beside a strip's title: the cherry blossom of gold on its disc of black lacquer, ringed in
        gold, its foot kept two rows clear of the tagline under the title."""
        A.crest(p, x + 9, y + 1, 6.5, night)

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        """None: a dojo has a ceiling, not a sky. Its night is the paper lit from behind (see `art.paper`)."""

    def rule_decor(self, p, x0, x1, y, seed, night):
        """Cherry petals fallen along a rule where no scene stands, now and then."""
        A.petals_on_rule(p, x0, x1, y, night, seed=seed + x0)

    def _drift(self, p, g, night, motion):
        """The petals drifting across the sky of a header, behind its title, ending two rows above the first word under
        it (see `art.petal_drift`)."""
        titles = getattr(p, "titles", ())
        under = max((y + 7 * scale for x, y, s, scale, w in titles), default=0)
        foot = min([b[1] for b in p.words if b[1] >= under] + [g - 4]) - 2
        A.petal_drift(p, night, motion, foot, self.mark_box(p))

    def scene(self, design, p, rule, night, motion):
        """On every header cherry petals drift across the sky behind the title, ending above the words under it, and
        in a moving header the beam passes down each line of the title on the hand's period. On H1 at the left the
        fighter's flying kick high over a byobu painted with a great wave, and at the right his opponent in his guard
        under a great round window onto the city, beside a stone lantern that pools its light on the tatami by night;
        on H2, at the right, the two meet: the fighter in the air at his opponent standing in his guard, before a byobu
        painted with a great pine, a paper lantern hanging over them; on H3, at the right, the shoji slid open on the
        garden, a pagoda rising nearly the strip's full height through it, a stone lantern beside it. Each piece is
        left out should a long title or a long line come near it."""
        titles = getattr(p, "titles", ())
        if motion:
            for n, (x, y, s, scale, w) in enumerate(titles):
                rain.scan(p, x, y, s, scale, w, n, self.hand.glint, C["white"])
        g = rule - 1
        self._drift(p, g, night, motion)
        if p.clear_of_words(4, g - 3, p.w - 4, g + 1):
            A.tatami(p, 4, p.w - 4, g, night)
            A.fallen(p, [(6, p.w - 6)], g, night)
        return {"H1": self._h1, "H2": self._h2, "H3": self._h3}[design](p, g, night, motion)

    def _h1(self, p, g, night, motion):
        spans = []
        if p.clear_of_words(4, 22, 56, g + 1):
            screen = A.byobu(p, 6, 24, g, night)
            spans.append((4, 56))
            if p.clear_of_words(4, 29, 56, 70):
                A.shadow(p, 32, g, 12)
                A.kicker(p, 14, 31, night, motion, light=night)
                if night:
                    A.glow_on(p, screen, 26, 46, 26, 22)
        if p.clear_of_words(360, 33, 411, 86):
            A.window(p, 386, 59, 24, night, motion)
        if p.clear_of_words(363, 4, 378, 37):
            A.chochin(p, 365, 15, night, motion)
        light = A.lantern(p, 394, g, night, motion) if p.clear_of_words(392, g - 32, 411, g + 1) else None
        if p.clear_of_words(362, g - 33, 389, g + 1):
            A.guard(p, 366, g, night, motion, light=light)
            spans.append((356, p.w - 4))
        return spans

    def _h2(self, p, g, night, motion):
        """The clash at the right of a section: the pine byobu from SCREEN_X, as tall as the rows the words leave it,
        the pine rising at its right and reaching out over the two fighters, the one in the air at the left and his
        opponent standing in the middle, and the stone lantern at the right."""
        x0 = next((x for x in range(SCREEN_X, SCREEN_X + 12) if p.clear_of_words(x - 3, 20, p.w - 4, g + 1)), None)
        if x0 is None:
            return []
        panels = 4
        pw = (p.w - 6 - x0) // panels + 1
        top = 24
        screen = A.screen(p, x0, top, g, night, panels, pw, "pine")
        A.shadow(p, x0 + 24, g, 12)
        A.kicker(p, x0 + 3, max(top + 6, g - 62), night, motion, light=night)
        light = A.lantern(p, p.w - 21, g, night, motion, phase=1)
        A.guard(p, x0 + 46, g, night, motion, light=light if night else None)
        if night:
            A.glow_on(p, screen, light[0], light[1], 40, 30)
        return [(x0 - 2, p.w - 4)]

    def _h3(self, p, g, night, motion):
        """The pagoda at the right of a strip, through the shoji slid open on the garden, rising the strip's full height
        from under the rope to the tatami, and the stone lantern beside it where the words leave it room."""
        x1 = p.w - 6
        x0 = next((x for x in range(PAGODA_X, PAGODA_X + 14) if p.clear_of_words(x - 3, 20, x1 + 2, g + 1)), None)
        if x0 is None:
            return []
        A.pagoda_window(p, x0, x1, 24, g, night, motion)
        spans = [(x0 - 2, p.w - 4)]
        lx = x0 - 13
        if p.clear_of_words(lx - 2, g - len(A.LANTERN) - 2, lx + 17, g + 1):
            A.lantern(p, lx, g, night, motion)
            spans.append((lx - 2, x0))
        return spans


    # ---- on a phone
    PHONE_SCENE = 58    # the rows a phone's H1 gives its dojo under its words and its notes
    # The rows a phone's H2 and H3 ask for under their words, whatever the words: room for the pine byobu with the two
    # fighters before it, and for the window onto the pagoda, kept clear of the words over them.
    UNDER = {"H2": 64, "H3": 62}
    HERO_LEAST = 44     # the fewest rows a phone's scene stands in

    def h1_narrow(self, h, night):
        """A phone's H1, its dojo given PHONE_SCENE rows under the words and the notes set under them, however many
        notes there are."""
        self.phone_scene_rows = self.PHONE_SCENE + 4 + 10 * len(self.said(h))
        try:
            return super().h1_narrow(h, night)
        finally:
            del self.phone_scene_rows

    @staticmethod
    def _room(p, x0, x1, g, most, least):
        """The rows free of words above the tatami at row g between x0 and x1, `most` at the most, keeping three
        rows of margin above and two beside; None when fewer than `least` are free."""
        for room in range(most, least - 1, -1):
            if p.clear_of_words(x0 - 2, g - room - 3, x1 + 2, g + 3):
                return room
        return None

    def scene_narrow(self, design, p, y, night):
        """A phone's H1 scene, the whole dojo across the phone under the words: the byobu of the great wave at the left,
        the fighter in the air off it in the middle of his flying kick, and at the right his opponent in his guard
        before the round window onto the city, the stone lantern beside him, on the tatami, built to the rows the words
        leave free; a phone's H2 and H3 stand their scenes under their words instead (see `scene_under`)."""
        if design != "H1":
            return
        g = y - 1
        room = self._room(p, 5, p.w - 5, g, self.PHONE_SCENE - 2, self.HERO_LEAST)
        if not room:
            return
        A.tatami(p, 4, p.w - 4, g, night)
        A.fallen(p, [(6, p.w - 6)], g, night, seed=4)
        top = g - room + 2
        A.byobu(p, 6, max(top, g - 50), g, night)
        A.shadow(p, 76, g, 12)
        A.kicker(p, 56, max(top + 4, g - 46), night, False, light=night)
        r = min(17, (room - 6) // 2)
        A.window(p, 146, g - 6 - r, r, night, False)
        light = A.lantern(p, p.w - 21, g, night, False)
        A.guard(p, 126, g, night, False, light=light if night else None)

    def phone_rows(self, design, title_w):
        """The rows a phone's H2 or H3 leaves under its words for its scene, whatever the words say (see
        `scene_under`)."""
        return self.UNDER[design]

    def scene_under(self, design, p, y0, y1, night):
        """A phone's scene under its words, across the phone, standing on the rule at y1 and built to the rows free
        over it: on H2 the pine byobu with the fighter in the air at his opponent before it and the stone lantern; on
        H3 the shoji slid open on the garden and the pagoda rising through it, the stone lantern beside it and the
        opponent standing in the dojo, looking out at it. By night the lanterns burn and light the tatami."""
        g = y1 - 1
        room = self._room(p, 5, p.w - 5, g, self.UNDER[design] - 2, self.HERO_LEAST)
        if not room:
            return
        A.tatami(p, 4, p.w - 4, g, night)
        top = g - room + 2
        if design == "H2":
            screen = A.screen(p, 6, top, g, night, 6, 29, "pine")
            A.shadow(p, 52, g, 12)
            A.kicker(p, 30, max(top + 6, g - 50), night, False, light=night)
            light = A.lantern(p, p.w - 22, g, night, False)
            A.guard(p, 92, g, night, False, light=light if night else None)
            if night:
                A.glow_on(p, screen, light[0], light[1], 46, 30)
        else:
            A.pagoda_window(p, 92, p.w - 6, top, g, night, False)
            A.lantern(p, 74, g, night, False)
            A.guard(p, 30, g, night, False)


    # ---- the footers and the links
    def footer_mark(self, p, x, y, night):
        """The dojo's crest at the corner of the closing notes, a cherry blossom of gold leaf."""
        A.crest(p, x + 6, y + 4, 3.6, night, disc=False)

    def _footed(self, p, night, last=False):
        """A footer once its cells are laid: the dojo's floor along its foot, a dais rising where the cells leave it
        room, and the alcove, a hanging scroll between two paper lanterns, where they leave the paper free (see
        `art.footing`): on a title block only after its `last` cell."""
        after = max((b[2] for b in p.words), default=0) + 4 if last else 0
        A.footing(p, night, after=after)
        return p

    def f1(self, ft, night):
        return self._footed(super().f1(ft, night), night, last=True)

    def f2(self, ft, night):
        return self._footed(super().f2(ft, night), night)

    def f1_narrow(self, ft, night):
        return self._footed(super().f1_narrow(ft, night), night, last=True)

    def f2_narrow(self, ft, night):
        return self._footed(super().f2_narrow(ft, night), night)

    def link_top(self, p, x0, x1, y, seed, night):
        """The button hung like a shrine's gate: a rope of twisted straw along its top, knotted at its ends."""
        A.rope(p, x0, x1, y - 2, night)

    def heart(self, p, x, y):
        A.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        """The graphic scale's bar as a lacquered scabbard: black lacquer and gold leaf by turns."""
        A.scabbard(p, x0, y0, w, h, period)

    def link_colours(self, night):
        """A face of black lacquer in a rim of gold leaf, gold letters, and the lacquer's deepest shade along the
        foot."""
        L, G = LACQUER, GOLD
        if night:
            return L[1], G[2], G[5], L[0]
        return L[2], G[3], G[5], L[0]

    def link_icon(self, index, night, ink):
        return A.ICONS[LINK_SPRITES[index % len(LINK_SPRITES)]], A.icon_pal(night, ink)

    # ---- the elements
    def card_bevel(self, night):
        return (WASHI[5], LACQUER[0]) if night else (C["white"], HINOKI[4])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A card as a lacquered box: a band of black lacquer down its icon cell's edge, capped with gold, and on its
        lid a gold fitting over each upper corner."""
        A.card_deco(p, x, y, w, h, night, lid)

    def wire_ink(self, night):
        return RAMP["red"][3] if night else RAMP["red"][2]

    def wire_lights(self, p, cells, night, seed):
        """The wire as a cord of vermilion silk, a paper lantern hung under it every so often, lit by night."""
        A.cord_lights(p, cells, night)

    def dashes(self, night):
        return [RAMP["red"][4 if night else 3], GOLD[4 if night else 3]]

    def ornament(self, kind, p, x, y, night):
        """A stone lantern in a free corner of the schematic, its fire box burning by night."""
        if kind == "schematic":
            if p is not None:
                A.lantern(p, x, y + len(A.LANTERN) - 1, night, False, glow=False)
            return (len(A.LANTERN[0]), len(A.LANTERN))
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as a cane of bamboo, a node every seven rows."""
        A.bamboo(p, bx, base - v, bw, v, night)

    def peak_mark(self, p, x, y, night):
        A.crest(p, x + 3, y + 4, 3.2, night, disc=False)

    def dial_ring(self, p, arc, night):
        """The rim of a taiko drum bent over the dial, vermilion studded with gold."""
        A.drum_rim(p, arc, night)

    def dial_tick(self, p, x, y, night):
        p.px(x, y, GOLD[5])
        p.px(x + 1, y + 1, GOLD[1])

    def dial_hub(self, p, cx, cy, night):
        """A boss of gold leaf with a vermilion centre."""
        sphere(p, cx + 0.5, cy - 0.5, 3.0, GOLD, lo=1, hi=6)
        p.px(cx, cy - 1, RAMP["red"][3])

    def material(self, i, xx, yy, y0, y1, lift, night):
        """The wrappers dyed in the old patterns by turns: waves of the sea, hemp leaf, a check, cherry blossom and
        the tortoise shell."""
        return A.dyed(i, xx, yy, y0, lift, night)

    def counter_cell(self, q, ox, oy, night):
        A.nafuda(q, ox, oy, night)

    def counter_ink(self, night, dim):
        """A numeral brushed in sumi on the name plate by day, in gold leaf on the darker plate by night; a leading
        nought brushed paler."""
        if night:
            return HINOKI[3] if dim else GOLD[5]
        return HINOKI[2] if dim else LACQUER[1]

    def timeline_line(self, p, x0, x1, y, night):
        """A rope of twisted straw the releases stand on, up to today."""
        if x1 - x0 >= 3:
            A.rope(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        """A nobori on its pole for a release, dyed by turns; a little torii for the repository's founding."""
        A.nobori(p, x, gy, kind, night, i)

    def today_mark(self, p, x, y, night):
        A.hinomaru(p, x, y, night)

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor as a crest: a disc dyed in their colour, ringed in gold, their initials on it in white; a
        bot's of granite with a cross."""
        A.mon(p, cx, cy, i, person, night, C["white"])

    def commit_bar(self, p, x, y, w, fill, night):
        """A contributor's share as a cord of vermilion silk wound on a lacquered rod."""
        p.box(x, y, w + 2, 4, LACQUER[1])
        p.hline(x + 1, x + 1 + w, y + 1, LACQUER[3])
        p.hline(x + 1, x + 1 + w, y + 2, LACQUER[2])
        R = RAMP["red"]
        for xx in range(x + 1, x + 1 + fill):
            p.px(xx, y + 1, R[5] if xx % 3 else R[4])
            p.px(xx, y + 2, R[3] if xx % 3 else R[2])

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """Vermilion round the seal's pressed centre, studded with gold at its rim."""
        A.seal(p, cx, cy, r0, r1, n, night)

    def seal_mark(self, p, x, y, night):
        A.crest(p, x + 3, y + 3, 3.2, night, disc=False)

    def placard_board(self, p, night):
        """The placard as the dojo's signboard of hinoki, in a frame of black lacquer with gold at its corners."""
        A.kanban(p, night)

    def placard_mark(self, p, x, y, night):
        A.crest(p, x + 6, y, 6.5, night)

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """The set's touch over a badge, kept inside its shape and off its letters: a rope of twisted straw along its
        top two rows, as a shimenawa is hung over a shrine's door, knotted at its ends; the badge's foot in the
        lacquer's shadow; and its two blocks lacquered, lit along their top and left and shaded along their foot and
        right, with a seam where the label's lacquer meets the value."""
        h = s["h"]
        ty = self._text_y(s)
        text_rows = range(ty - 1, ty + (7 if s["font"] == "57" else 5) + 1)
        k = -1 if night else 0
        S = RAMP["straw"]

        def ins(x, y):
            return 0 <= x < w and 0 <= y < h and inside(x, y, w, h, s["corner"])
        row = h - 2 if (h - 2) % 4 != 2 else h - 3
        first = next((x for x in range(w) if ins(x, row)), 0)
        edge = next((x for x in range(first + 1, w) if ins(x, row) and p.get(x, row) != p.get(first, row)), w)
        if edge == w and p.get(first, row) not in (self.badge_label()[0], self.badge_gold()[0]):
            edge = 0                                    # a value and no label: one block from end to end
        for y in range(h):
            ends = [x for x in range(w) if ins(x, y)]
            for x in ends:
                if y <= 1:
                    t = x % 3
                    tone = (5 if t == 0 else 4 if t == 1 else 2) if y == 0 else (3 if t == 0 else 2 if t == 1 else 1)
                    if x in (ends[0], ends[-1]):
                        tone = 1 - y
                    p.px(x, y, A.ramp_at(S, tone + k))
                    continue
                if y == h - 1:
                    p.px(x, y, LACQUER[1])
                    continue
                c = p.get(x, y)
                try:
                    if y == 2 and y not in text_rows:
                        p.px(x, y, step(c, 1))
                    elif y == h - 2:
                        p.px(x, y, step(c, -1))
                    elif not ins(x - 1, y) or x == edge:
                        p.px(x, y, step(c, 1))
                    elif not ins(x + 1, y) or x == edge - 1:
                        p.px(x, y, step(c, -1))
                except KeyError:
                    pass

    def badge_label(self):
        """A label of black lacquer lettered in gold leaf."""
        return LACQUER[2], GOLD[5]

    def badge_gold(self):
        """A live badge's label: gold leaf lettered in lacquer."""
        return GOLD[3], LACQUER[0]

    def badge_states(self):
        return {"green": (RAMP["moss"][2], C["white"]), "yellow": (GOLD[4], LACQUER[0]),
                "red": (RAMP["red"][2], C["white"]), "slate": (RAMP["stone"][2], C["white"])}

    def badge_swatches(self):
        """The colours a value may be dyed: vermilion, persimmon, gold, moss, indigo, wisteria, cherry, washi, black
        lacquer, granite and hinoki, so a written colour finds its nearest."""
        R = RAMP
        W, L0 = C["white"], LACQUER[0]
        return {"vermilion": (R["red"][3], W, None), "persimmon": (R["kaki"][4], L0, None),
                "gold": (GOLD[3], L0, None), "moss": (R["moss"][3], W, None), "indigo": (R["indigo"][3], W, None),
                "wisteria": (R["fuji"][3], W, None), "cherry": (R["sakura"][4], L0, None),
                "washi": (R["paper"][6], LACQUER[1], "washi"), "lacquer": (LACQUER[1], GOLD[5], None),
                "granite": (R["stone"][3], W, None), "hinoki": (R["hinoki"][1], W, None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        """Washi, its fibres showing here and there where the letters leave it."""
        if pattern == "washi" and y not in text_rows and (x * 5 + y * 11) % 17 == 0:
            return RAMP["paper"][4]
        return c

    def badge_outline(self, pattern):
        return HINOKI[3] if pattern == "washi" else None

    def badge_shine(self, c, y, h):
        """Lacquer's gloss: its top row a step lighter and its foot a step darker."""
        try:
            return step(c, 1) if y == 2 else step(c, -1) if y == h - 1 else c
        except KeyError:
            return c

    def plate_edge(self, block):
        return step(block, -1)

    def plate_colours(self, mode):
        """A plate is a panel of washi in a frame of black lacquer by day, the paper lit from behind by night, the
        value on vermilion lettered in gold; a live plate is gold leaf."""
        if mode == "day":
            return dict(paper=RAMP["paper"][5], dot=RAMP["paper"][4], frame=LACQUER[1], block=RAMP["red"][2],
                        ink=LACQUER[1], letters=GOLD[5])
        if mode == "night":
            return dict(paper=WASHI[1], dot=WASHI[2], frame=GOLD[3], block=RAMP["red"][2], ink=C["body_night"],
                        letters=GOLD[5])
        return dict(paper=GOLD[3], dot=GOLD[4], frame=LACQUER[0], edge=GOLD[1], ink=LACQUER[0])

    # ---- the games
    def game_squares(self, night):
        """A board of tatami and vermilion lacquer, each a tone down by night, as every board of the year is dimmer
        after dark."""
        return (Stuff(RAMP["tatami"], 5 if night else 6, "weave"), Stuff(RAMP["red"], 2 if night else 3, "satin"))

    def game_frame(self, night):
        """A frame of black lacquer over wood, its grain showing through."""
        return Stuff(LACQUER, 3), "wood"

    def game_podium(self, night):
        """A podium of black lacquer, hung with banners of vermilion and the board's colours."""
        return Podium(Stuff(LACQUER, 2, "satin"), "banners", Stuff(RAMP["red"], 3))


LINK_SPRITES = ("lantern", "torii", "blossom", "katana")
SCREEN_X = 312      # the furthest left an H2's pine byobu begins: three units clear of the furthest its words reach
PAGODA_X = 364      # and an H3's window onto the pagoda


SET = Dojo()
