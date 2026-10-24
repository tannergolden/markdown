# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Rooftop set: the jump across the summer skyline, June's design in the Matrix collection, drawn in the
collection's hand.

Every sheet is the sky over the city in summer, pale blue by day and by night the city's deep blue with the code's
glyphs showing through it for stars. A riveted steel column stands down each side, a girder truss runs along the top,
stopping either side of the month's mark, and the foot is a parapet's concrete coping. Titles are towers of blue
mirror glass, a tower to a letter, ruled in floors and bays with the sky running down their faces, and by night dark
glass lit pane by pane in phosphor; in a moving header the terminal's beam passes down them on the hand's period. An
H1 is the jump, under the sky's own: clouds drifting across it by day, and by night searchlights sweeping it from the
roofs, their beams crossing behind the title, the hand's moon over the city. At the left the near tower rises nearly
the sheet's height, its fire escape down its face, its water tower on its stilts on the roof, pigeons on its parapet
by day, and a man in a long dark coat in the air off its edge, his coat flaring; at the right the far tower, lower,
with its bulkhead and its searchlight, and a helicopter hovering over its roof, its rotor turning and by night its
spotlight thrown down onto the roof; and far below between them the city in two rows of towers, hazy by day and lit
window by window by night. An H2 is the fight on a roof at the right, risen full height: a tower of blue glass rising
behind the parapet with its aviation light on its mast, the city's far towers across the back, an agent aiming from
the left and the man in the long coat bending back from the bullets, which creep through the air in bullet time,
rippling it, while clouds drift by day and a searchlight sweeps the night from the tower's crown. An H3 stands the
great water tower on its building's roof at the right, rising the strip's full height, a pigeon on it by day and a
searchlight's lamp burning on the parapet by night. A pigeon perches beside SECTION A-A, a small water tower stands
beside a strip's title, and the rules are riveted. A phone's H1 has the whole jump across its width under the words,
and its H2 and H3 stand the fight on the roof and the water tower under the words across the phone, whatever the words
say. A footer stands on the parapet, brick under a concrete coping, rising where its cells leave it room, with a small
water tower and a searchlight's lamp after a title block's last cell, the lamp burning by night; a pigeon perches at
the corner of the closing notes, the heart is painted red on the brick and the graphic scale is a steel beam in hazard
stripes. Links are panes of blue glass hung from a riveted steel beam; badges carry the beam along their top; the
elements are panels of glass in steel, steel cables hung with aviation lights, towers of glass, a riveted steel dial,
split-flap counters, signs hung from a girder and a ring of brass; and the games are played on concrete and blue glass
in a riveted steel frame, the Hall's podium the water tower's cedar staves. The design is drawn in the Matrix
collection's hand (`collections.hand`): its words in the hand's inks, its sky within the hand's grounds, every light
on the hand's phosphor and its moon the hand's.
"""
from __future__ import annotations

from ...holidays.designs.badges import inside
from ...holidays.designs.materials import Podium, Stuff
from ...holidays.pixel import sphere
from ..hand import CollectionSet
from .. import rain
from . import art as A
from .palette import C, RAMP, TOKENS, X, step

GLASS, STEEL, DUSK, FLAME = RAMP["glass"], RAMP["steel"], RAMP["dusk"], RAMP["flame"]


class Rooftop(CollectionSet):
    key = "matrix-rooftop"
    name = "Rooftop"
    collection = "matrix"
    tagline = ("Rooftops over the summer skyline: towers of mirror glass, a long coat in the air, bullet time and "
               "searchlights by night.")
    about = (
        "The sky over the city in summer: pale blue by day, and by night the city's deep blue with the code's glyphs "
        "showing through it for stars. Riveted steel columns stand down the sides, a girder truss runs along the top "
        "and the foot is a parapet's concrete coping. Titles are towers of blue mirror glass, a tower to a letter, "
        "ruled in floors and bays with the sky running down their faces, and by night the glass goes dark and is lit "
        "pane by pane in phosphor. The H1 is the jump, under clouds drifting across the sky by day and searchlights "
        "sweeping it by night, their beams crossing behind the title: a tall tower with its water tower on its stilts "
        "and pigeons on its parapet, a man in a long dark coat in the air off its roof with his coat flaring behind "
        "him, and across the gap the far tower with its bulkhead and a helicopter hovering over it, its rotor turning "
        "and its spotlight on the roof, the city far below between them under the moon. A section's header is the "
        "fight on a roof before a tower of blue glass: an agent aiming, the bullets rippling the air in bullet time "
        "and the man in the long coat bending back from them; a strip's is the great water tower on its building's "
        "roof. On a phone the whole jump stands across the width under the words, and a section's and a strip's "
        "phones stand the fight and the water tower there. Footers stand on the parapet, rising where the cells leave "
        "room, with a small water tower and its lamp after the last cell; links hang from a riveted steel beam; "
        "badges carry the beam along their top; and the elements are panels of glass in steel, cables hung with "
        "aviation lights, towers of glass, a riveted dial, split-flap counters, signs hung from a girder and a ring of "
        "brass. The games are played on concrete and blue glass in a riveted steel frame, and the Hall of Fame's "
        "podium is the water tower's cedar staves.")
    tokens = frozenset(TOKENS)

    # ---- colour and paper
    def ink(self, night):
        """The words in the hand's two inks; the titles in the towers' glass."""
        return dict(
            title=GLASS[5] if night else GLASS[2], shadow=GLASS[0] if night else GLASS[4],
            body=self.hand.body[night], muted=self.hand.muted[night],
            rule=X["rule_night"] if night else X["rule_day"], accent=GLASS[5] if night else GLASS[2],
            tag=GLASS[5] if night else GLASS[2], tag_ink=GLASS[0] if night else GLASS[6],
            fill=DUSK[3] if night else RAMP["cloud"][5], dim=X["dim_night"] if night else X["dim_day"],
        )

    def paper(self, p, night, uid="p"):
        p.sheet = uid
        A.sky(p, night)

    def bg_at(self, p, night, y):
        return A.bg_at(p, night, y)

    def _finish(self, p, night):
        """The last pass, which a drawing made lighter keeps too: the file written as lightly as it can be, the same
        drawing unit for unit, the month's mark left as it is drawn (see `Pix.compact`)."""
        if not p.lite:
            self.finish(p, night)
        p.compact(keep=("mark",))

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The sky, and by night the code's glyphs showing through it for stars, kept off the words and the month's
        mark."""
        self.paper(p, night)
        if night:
            rain.stars(p, 6, 12, p.w - 6, int(y1 * 0.75), p.w // 8, FLAME, seed=seed, twinkling=motion,
                       avoid=(*avoid, self.mark_box(p)))

    def frame(self, p, night, webs=False):
        A.frame(p, night, header=webs)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """The girder truss along the top, stopping either side of the month's mark."""
        A.truss(p, x0, x1, night, self.mark_box(p), self.marked)

    def tag(self, p, x, y, w, h, night):
        """A block of blue glass, a note's number knocked out of it."""
        p.rect(x, y, w, h, GLASS[5] if night else GLASS[2])
        p.hline(x, x + w, y, GLASS[6] if night else GLASS[4])

    def title_text(self, p, x, y, s, night, scale):
        """Towers of blue mirror glass (see `art.glass_title`). The drawing keeps each line, for the scan that passes
        down it in a moving header."""
        w = A.glass_title(p, x, y, s, scale, night)
        p.titles = getattr(p, "titles", []) + [(x, y, s, scale, w)]
        return w

    # ---- the headers' scenes
    def scene(self, design, p, rule, night, motion):
        """On H1 the sky's own across the whole sheet, behind the title and ending above the tagline: searchlights
        sweeping by night and clouds drifting by day; the near tower at the left with its water tower and the leap off
        its roof, the far tower at the right with the helicopter hovering over its roof, and the city far below
        between them. On H2 the fight on the roof at the right, before a tower of glass risen full height (see
        `_h2`); on H3 the water tower on its building at the right, rising the strip's full height (see `_h3`). In a
        moving header the beam passes down each line of the title on the hand's period. Each piece is left out should
        a long title or a long line come near it."""
        titles = getattr(p, "titles", ())
        if motion:
            for n, (x, y, s, scale, w) in enumerate(titles):
                rain.scan(p, x, y, s, scale, w, n, self.hand.glint, C["white"])
        g = rule - 1
        spans = []
        under = max((y + 7 * scale for x, y, s, scale, w in titles), default=0)
        foot = min([b[1] for b in p.words if b[1] >= under] + [g - 4]) - 2
        if design != "H1":
            return {"H2": self._h2, "H3": self._h3}[design](p, g, foot, night, motion)
        near, far = g - NEAR, g - FAR
        if night:
            A.beams(p, foot, self.mark_box(p), (((LAMPS[0] + 1, near - 8), 44, 86, 36.0),
                                                 ((LAMPS[1] + 1, far - 8), -46, -88, 44.0)), motion)
            if p.clear_of_words(306, 6, 330, 25):
                A.moon(p, 318, 15, 4.5, glow=1.6)
        else:
            A.cloud_drift(p, foot, self.mark_box(p), motion)
        A.far_city(p, 40, 361, g, night, motion)
        left = self._near(p, near, g, night, motion)
        if left:
            spans.append(left)
        right = self._far(p, far, g, night, motion)
        if right:
            spans.append(right)
        return spans

    def _near(self, p, roof, g, night, motion):
        """The left of an H1: the near tower rising nearly the sheet's height, its fire escape down its face, its water
        tower on its roof and its searchlight, pigeons on its parapet by day, and the man in the long coat leaping off
        it, as far out over the gap as the words leave him room. Returns the span it covers."""
        if not p.clear_of_words(2, roof - 40, 47, g + 1):
            return None
        A.facade(p, 4, 45, roof + 3, g, night, seed=3, lit=0.45)
        A.fire_escape(p, 28, 43, roof + 3, g, night)
        A.parapet(p, 4, 45, roof, night)
        A.water_tower(p, 5, roof + 1, night)
        A.lamp(p, LAMPS[0], roof - 7, night)
        if not night:
            A.pigeons(p, [(30, roof - 1), (35, roof - 1)], None, motion)
        top = roof - 34
        x = next((x for x in range(46, 19, -1) if p.clear_of_words(x - 2, top - 3, x + len(A.LEAP[0]) + 2,
                                                                  top + len(A.LEAP) + 2)), None)
        if x is not None:
            A.leaper(p, x, top, night, motion)
        return (4, 47)

    def _far(self, p, roof, g, night, motion):
        """The right of an H1: the far tower, lower, its bulkhead and its plant and its searchlight on its roof, and
        the helicopter hovering over it, by night its spotlight thrown down onto the roof. Returns the span it
        covers."""
        x0 = next((x for x in (362, 365, 368) if p.clear_of_words(x - 3, roof - 2, 411, g + 1)), None)
        if x0 is None:
            return None
        A.facade(p, x0, 410, roof + 3, g, night, seed=6, lit=0.5)
        A.parapet(p, x0, 410, roof, night)
        A.vents(p, x0 + 3, roof, night)
        A.bulkhead(p, x0 + 18, x0 + 36, roof - 11, roof, night)
        A.lamp(p, LAMPS[1], roof - 7, night)
        if p.clear_of_words(362, 11, 413, 34):
            A.helicopter(p, 363, 14, night, motion, aim=roof - 1)
        return (359, 411)

    def _h2(self, p, g, foot, night, motion):
        """The fight at the right of a section, from H2_X or as near it as the words allow, risen full height: the
        tower of blue glass behind the parapet, the city's far towers across the back, the agent aiming from the left
        and the man in the long coat bending back from the bullets at the right; clouds drifting across the sky by day
        and by night a searchlight sweeping it from the tower's crown."""
        x0 = next((x for x in range(H2_X, H2_X + 12) if p.clear_of_words(x - 3, 20, p.w - 4, g + 1)), None)
        if x0 is None:
            return []
        if night:
            A.beams(p, foot, self.mark_box(p), (((p.w - 19, 30), -24, -68, 40.0),), motion)
        else:
            A.cloud_drift(p, foot, self.mark_box(p), motion)
        A.bullet_time(p, x0, p.w - 6, 22, g, night, motion)
        return [(x0 - 2, p.w - 4)]

    def _h3(self, p, g, foot, night, motion):
        """The water tower at the right of a strip, on its building's roof, rising the strip's full height from the
        rule to under the truss; clouds drifting across the sky by day."""
        x0 = next((x for x in range(H3_X, H3_X + 12) if p.clear_of_words(x - 3, 20, p.w - 4, g + 1)), None)
        if x0 is None:
            return []
        if not night:
            A.cloud_drift(p, foot, self.mark_box(p), motion)
        A.roof_tower(p, x0, p.w - 6, 22, g, night, motion)
        return [(x0 - 2, p.w - 4)]

    def section_mark(self, p, x, y, night):
        """A pigeon perched beside SECTION A-A, from a row above the words to three under them."""
        A.pigeons(p, [(x + 1, y + 6)], None, False)

    def strip_mark(self, p, x, y, night):
        """A small water tower on its stilts beside a strip's title, its feet two rows clear of the tagline."""
        A.water_tower(p, x + 3, y + 7, night, legs=4, w=11, tank=5)

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        """The code's glyphs showing through the night for stars; faint ones a dim blue, the city's haze lit."""
        rain.stars(p, x0, y0, x1, y1, n, FLAME, seed=seed, twinkling=twinkling, faint=faint, avoid=avoid,
                   dim=DUSK[5] if faint else None)

    def rule_decor(self, p, x0, x1, y, seed, night):
        """The rule riveted every so often, a steel rivet's head lit along its top."""
        A.rivets(p, x0, x1, y, night, seed)

    # ---- on a phone
    PHONE_SCENE = 58    # the rows a phone's H1 gives its rooftops under its words and its notes
    # The rows a phone's H2 and H3 ask for under their words, whatever the words: room for the fight on the roof with
    # its tower of glass rising behind it, and for the water tower on its building.
    UNDER = {"H2": 64, "H3": 62}
    HERO_LEAST = 44     # the fewest rows a phone's scene stands in

    def h1_narrow(self, h, night):
        """A phone's H1, its rooftops given PHONE_SCENE rows under the words and the notes set under them, however
        many notes there are."""
        self.phone_scene_rows = self.PHONE_SCENE + 4 + 10 * len(self.said(h))
        try:
            return super().h1_narrow(h, night)
        finally:
            del self.phone_scene_rows

    @staticmethod
    def _room(p, x0, x1, g, most, least):
        """The rows free of words above the rule at row g between x0 and x1, `most` at the most, keeping three rows of
        margin above and two beside; None when fewer than `least` are free."""
        for room in range(most, least - 1, -1):
            if p.clear_of_words(x0 - 2, g - room - 3, x1 + 2, g + 3):
                return room
        return None

    def scene_narrow(self, design, p, y, night):
        """A phone's H1 scene, the jump across the phone under the words: the near tower at the left with its water
        tower, the man in the long coat in the air off its roof, the far tower at the right with its bulkhead and its
        searchlight, and the city far below between them, built to the rows the words leave free; a phone's H2 and H3
        stand their scenes under their words instead (see `scene_under`)."""
        if design != "H1":
            return
        g = y - 1
        room = self._room(p, 5, p.w - 5, g, self.PHONE_SCENE - 2, self.HERO_LEAST)
        if not room:
            return
        A.phone_jump(p, g, room, night)

    def phone_rows(self, design, title_w):
        """The rows a phone's H2 or H3 leaves under its words for its scene, whatever the words say (see
        `scene_under`)."""
        return self.UNDER[design]

    def scene_under(self, design, p, y0, y1, night):
        """A phone's scene under its words, across the phone, standing on the rule at y1 and built to the rows free
        over it: on H2 the fight on the roof, the tower of glass rising behind it; on H3 the water tower on its
        building at the right and the city across the left."""
        g = y1 - 1
        room = self._room(p, 5, p.w - 5, g, self.UNDER[design] - 2, self.HERO_LEAST)
        if not room:
            return
        top = g - room + 2
        if design == "H2":
            A.bullet_time(p, 6, p.w - 6, top, g, night, False)
        else:
            A.far_city(p, 6, 98, g, night, False, seed=21)
            A.roof_tower(p, 98, p.w - 6, top, g, night, False)

    # ---- the footers and the links
    def footer_mark(self, p, x, y, night):
        """A pigeon perched at the corner of the closing notes."""
        A.pigeons(p, [(x + 2, y + 6)], None, False)

    def _footed(self, p, night, last=False):
        """A footer once its cells are laid: the parapet along its foot, brick under a coping of concrete, rising where
        the cells leave it room, and a small water tower on its stilts with a searchlight's lamp beside it where they
        leave the sky free (see `art.footing`): on a title block only after its `last` cell."""
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
        """The button hung from a steel beam riveted along its top."""
        A.beam_top(p, x0, x1, y - 2, night)
    def heart(self, p, x, y):
        A.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        """The graphic scale's bar as a steel beam painted in hazard stripes."""
        A.hazard(p, x0, y0, w, h, period)

    def link_colours(self, night):
        """A face of blue glass in a steel frame, the glass's palest tone for its letters, and its deepest along the
        foot."""
        G, S = GLASS, STEEL
        if night:
            return G[1], S[3], G[6], G[0]
        return G[2], S[1], G[6], G[0]

    def link_icon(self, index, night, ink):
        return A.ICONS[LINK_SPRITES[index % len(LINK_SPRITES)]], A.icon_pal(night, ink)

    # ---- the elements
    def card_bevel(self, night):
        return (DUSK[5], RAMP["coat"][0]) if night else (C["white"], STEEL[4])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A card as a panel of glass in a steel frame: a steel beam riveted down its icon cell's edge, and on its lid
        a steel bracket over each upper corner."""
        A.card_deco(p, x, y, w, h, night, lid)

    def wire_ink(self, night):
        return STEEL[4] if night else STEEL[3]

    def wire_lights(self, p, cells, night, seed):
        """The wire as a steel cable, an aviation light hung on it every so often, burning phosphor by night."""
        A.cable_lights(p, cells, night)

    def dashes(self, night):
        return [RAMP["taxi"][4], RAMP["coat"][1]]

    def ornament(self, kind, p, x, y, night):
        """A water tower on its stilts in a free corner of the schematic."""
        if kind == "schematic":
            if p is not None:
                A.water_tower(p, x, y + 32, night, legs=6)
            return (24, 33)
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as a tower of blue glass, ruled in floors."""
        A.tower_bar(p, bx, base - v, bw, v, night)

    def peak_mark(self, p, x, y, night):
        A.mast(p, x, y + 1, night)

    def dial_ring(self, p, arc, night):
        """A ring of steel bent over the dial, riveted."""
        A.steel_rim(p, arc, night)

    def dial_tick(self, p, x, y, night):
        p.px(x, y, RAMP["taxi"][4])
        p.px(x + 1, y + 1, RAMP["coat"][1])

    def dial_hub(self, p, cx, cy, night):
        """A hub of steel under a cap of a cab's yellow."""
        sphere(p, cx + 0.5, cy - 0.5, 3.0, STEEL, lo=1, hi=6)
        p.px(cx, cy - 1, RAMP["taxi"][4])

    def material(self, i, xx, yy, y0, y1, lift, night):
        """The wrappers in the roof's own stuffs by turns: brick, blue glass, hazard stripes, concrete and a steel
        deck plate."""
        return A.wrapper(i, xx, yy, y0, lift, night)

    def counter_cell(self, q, ox, oy, night):
        A.flip_cell(q, ox, oy, night)

    def counter_ink(self, night, dim):
        """A numeral on a split-flap board's flap, white; a leading nought in steel."""
        return STEEL[4] if dim else C["white"]

    def timeline_line(self, p, x0, x1, y, night):
        """A steel girder the releases hang from, up to today, riveted along its web."""
        if x1 - x0 >= 3:
            A.girder(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        """A sign hung from the girder for a release, painted by turns; a work light for a patch; the cornerstone for
        the repository's founding."""
        A.sign(p, x, gy, kind, night, i)

    def today_mark(self, p, x, y, night):
        A.searchlight(p, x, y, night)

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor as a pane of glass in a steel frame, painted in their colour, their initials on it; a bot an
        agent in dark glasses."""
        A.pane(p, cx, cy, i, person, night)

    def commit_bar(self, p, x, y, w, fill, night):
        """A contributor's share as a steel beam painted in hazard stripes."""
        p.box(x, y, w + 2, 4, STEEL[2])
        p.hline(x + 1, x + 1 + w, y + 1, STEEL[1])
        p.hline(x + 1, x + 1 + w, y + 2, STEEL[1])
        if fill:
            A.hazard(p, x + 1, y + 1, fill, 2, period=2)

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """A ring of brass round the seal's pressed centre, riveted at its rim."""
        A.brass(p, cx, cy, r0, r1, n, night)

    def seal_mark(self, p, x, y, night):
        A.pigeons(p, [(x, y + 4)], None, False)

    def placard_board(self, p, night):
        """The placard as a billboard on a roof, framed in steel and riveted."""
        A.billboard(p, night)

    def placard_mark(self, p, x, y, night):
        A.water_tower(p, x + 1, y + 9, night, legs=4, w=11, tank=5)

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """The set's touch over a badge, kept inside its shape and off its letters: a steel beam along its top two
        rows, its flange lit and a rivet's head every eight columns along its web; the badge's foot in the beam's
        shadow; and its two blocks bevelled, lit along their top and left and shaded along their foot and right, with
        a seam where the label meets the value."""
        h = s["h"]
        ty = self._text_y(s)
        text_rows = range(ty - 1, ty + (7 if s["font"] == "57" else 5) + 1)
        k = -1 if night else 0
        S = STEEL

        def ins(x, y):
            return 0 <= x < w and 0 <= y < h and inside(x, y, w, h, s["corner"])
        row = h - 2 if (h - 2) % 4 != 2 else h - 3
        first = next((x for x in range(w) if ins(x, row)), 0)
        edge = next((x for x in range(first + 1, w) if ins(x, row) and p.get(x, row) != p.get(first, row)), w)
        if edge == w and p.get(first, row) not in (self.badge_label()[0], self.badge_gold()[0]):
            edge = 0                                    # a value and no label: one block from end to end
        for y in range(h):
            for x in range(w):
                if not ins(x, y):
                    continue
                if y <= 1:
                    rivet = (x in (1, w - 2) or x % 8 == 4) and ins(x, 0) and ins(x, 1)
                    tone = (6 if rivet else 5) if y == 0 else (1 if rivet else 3)
                    p.px(x, y, A.ramp_at(S, tone + k))
                    continue
                if y == h - 1:
                    p.px(x, y, RAMP["coat"][1])
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

    def badge_label(self):
        """A label of the long coat's black leather lettered in the glass's pale blue."""
        return RAMP["coat"][2], GLASS[6]

    def badge_gold(self):
        """A live badge's label: a cab's yellow lettered in black."""
        return RAMP["taxi"][4], RAMP["coat"][0]

    def badge_states(self):
        return {"green": (RAMP["go"][2], C["white"]), "yellow": (RAMP["taxi"][4], RAMP["coat"][0]),
                "red": (RAMP["brick"][2], C["white"]), "slate": (STEEL[3], C["white"])}

    def badge_swatches(self):
        """The paints a value may wear: brick, rust, a cab's yellow, a street sign's green, blue glass, an awning's
        plum, concrete, the coat's black, steel, cedar and the summer sky, so a written colour finds its nearest."""
        R = RAMP
        W, K = C["white"], R["coat"][0]
        return {"brick": (R["brick"][3], W, None), "rust": (R["rust"][2], W, None), "taxi": (R["taxi"][4], K, None),
                "go": (R["go"][3], W, None), "glass": (GLASS[3], W, "panes"), "plum": (R["plum"][3], W, None),
                "concrete": (R["concrete"][5], R["coat"][1], None), "coat": (R["coat"][1], R["cloud"][5], None),
                "steel": (STEEL[3], W, None), "cedar": (R["cedar"][2], W, None),
                "sky": (R["cloud"][4], R["coat"][1], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        """Blue glass in its mullions, kept out of the letters' rows."""
        if pattern == "panes" and y not in text_rows and x % 4 == 0:
            return GLASS[2]
        return c

    def badge_outline(self, pattern):
        return STEEL[2] if pattern == "panes" else None

    def badge_shine(self, c, y, h):
        """Glass's gleam: its top row a step lighter and its foot a step darker."""
        try:
            return step(c, 1) if y == 2 else step(c, -1) if y == h - 1 else c
        except KeyError:
            return c

    def plate_edge(self, block):
        return step(block, -1)

    def plate_colours(self, mode):
        """A plate is a riveted steel plate by day and the same steel under the dusk by night, the value on a
        street sign's green lettered in white; a live plate is a cab's yellow."""
        if mode == "day":
            return dict(paper=STEEL[5], dot=STEEL[6], frame=STEEL[1], block=RAMP["go"][2], ink=RAMP["coat"][0],
                        letters=C["white"])
        if mode == "night":
            return dict(paper=DUSK[2], dot=DUSK[3], frame=STEEL[3], block=RAMP["go"][2], ink=C["body_night"],
                        letters=C["white"])
        return dict(paper=RAMP["taxi"][4], dot=RAMP["taxi"][5], frame=RAMP["coat"][0], edge=RAMP["taxi"][2],
                    ink=RAMP["coat"][0])

    # ---- the games
    def game_squares(self, night):
        """A board of the roof's concrete and the towers' blue glass in its mullions, each a tone down by night, as
        every board of the year is dimmer after dark."""
        return (Stuff(RAMP["concrete"], 4 if night else 5, "stone"),
                Stuff(GLASS, 2 if night else 3, "glass", fleck=STEEL[1]))

    def game_frame(self, night):
        """A frame of steel, riveted."""
        return Stuff(STEEL, 3), "iron"

    def game_podium(self, night):
        """A podium of the water tower's cedar staves, plain."""
        return Podium(Stuff(RAMP["cedar"], 3, "wood"))


LINK_SPRITES = ("tower", "heli", "skyline", "shades")
H2_X = 306          # the furthest left an H2's fight begins: three units clear of the furthest its words reach
H3_X = 352          # and an H3's water tower
NEAR, FAR = 50, 44      # how high each roof stands over the floor of the sheet: the near one and the far one
LAMPS = (38, 403)       # the column each roof's searchlight stands at


SET = Rooftop()
