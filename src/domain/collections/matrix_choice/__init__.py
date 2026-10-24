# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Choice set: the choice between two pills, February's design in the Matrix collection, drawn in the collection's
hand.

Every sheet is the damask wallpaper of an old hotel room on a stormy night, dusty rose by day and wine-black by
night, held in a frame of oxblood chesterfield leather close-studded with brass, and across a header's top a deep-
buttoned panel of tufted leather parts either side of the month's mark. Titles are glossy gel capsules of candy red,
each stroke streaked with light along its upper left over a darker underside; by night the streak is the green of
the room's one lamp, and in a moving header the terminal's beam passes down them on the hand's period. The H1 opens
on the room: at the left a red leather wingback chair under a cracked mirror whose glass the code falls through by
night, and a round table beside it with a glass of water and a banker's lamp burning green; at the right a tall window
streaming with rain between curtains of green velvet, a grey storm outside by day and by night the city's green-lit
towers under lightning, each stroke lighting the whole room above the words for its instant, and before it a little
table with an open box and the two pills, one red and one blue; and on the floor under the words a suitcase and a wet
umbrella dripping in its stand. An H2 stands the fireside at the right: a fireplace of carved mahogany, cold by day
and by night burning green with its candles lit on the mantel, a tall pier mirror over it showing the window and the
storm across the room, a club chair either side facing the other across the hearth and between them a low table with
the glass of water and the two pills, the lightning lighting the room by night. An H3 stands the cheval glass rising
the strip's full height at the right, the red chair facing it and caught in its foot, its face going to liquid in
rings where a hand touched it. SECTION A-A carries the two pills; a strip's title round dark glasses with the pills
caught in their lenses; and the Persian runner lies along the floor where no scene stands. A phone's H1 holds the
whole room under its words, its H2 the fireside and its H3 the cheval glass, under theirs whatever they say. The
footer stands on a mahogany skirting, rising where its cells leave it room, with the open box of pills on it after a
title block's last cell and the banker's lamp beside it, and the lamp again in the corner of its notes, lit by night;
link buttons are oxblood leather nailed in brass along their tops, each with its own thing of the room; the elements
are built of leather and brass nails, the title's red gel, mahogany, velvet tassels hung from a brass curtain rod
and the room's people in round dark glasses; badges carry a band of nailed leather; and the games are played on
boards of the box's satin and the chesterfield's leather in a mahogany frame, their winners standing on a podium of
the leather tied with a satin ribbon.
"""
from __future__ import annotations

import math

from ...holidays.designs.badges import inside
from ...holidays.designs.materials import Podium, Stuff
from ...holidays.pixel import Pix
from ..hand import CollectionSet
from .. import rain
from . import art as A
from .palette import C, RAMP, TOKENS, X, step

OX, BRASS, CANDY, WINE, ROSE = RAMP["oxblood"], RAMP["brass"], RAMP["candy"], RAMP["wine"], RAMP["rose"]
SATIN, VELVET, STORM, GLASS, BLUE = RAMP["satin"], RAMP["velvet"], RAMP["storm"], RAMP["glass"], RAMP["blue"]
NIGHT, WOOD, FLAME = RAMP["night"], RAMP["mahogany"], RAMP["flame"]


class Choice(CollectionSet):
    key = "matrix-choice"
    name = "Choice"
    collection = "matrix"
    tagline = "The choice between two pills: red gel titles, oxblood leather and brass, a storm at the window."
    about = (
        "Every sheet is the damask wallpaper of an old hotel room on a stormy night, dusty rose by day and wine-black "
        "by night, framed in oxblood chesterfield leather close-studded with brass, a deep-buttoned panel of tufted "
        "leather across the top. Titles are glossy gel capsules of candy red, a streak of light along each stroke over "
        "a darker underside, the streak turning the green of the room's one lamp by night. The headers open on the "
        "room: a red leather wingback chair under a cracked mirror that shows the code falling through it by night, a "
        "round table beside it with a glass of water and a banker's lamp burning green, and across the room a tall "
        "window streaming with rain between curtains of green velvet, the city's towers outside under lightning that "
        "lights the whole room for its instant, and before it a little stand with an open box and the two pills, one "
        "red and one blue; a section's header stands the fireside, a club chair either side of a fire burning green "
        "by night under a pier mirror, and a strip's the cheval glass rising its full height, going to liquid where a "
        "hand touched it. The two pills sit beside SECTION A-A, round dark glasses beside a strip's title, and a "
        "Persian runner lies along the floor. On a phone the whole room stands under the words, and a section's and a "
        "strip's heroes under theirs. The footer stands on a mahogany skirting with the box of pills and the lamp on "
        "it; links are leather nailed in brass; the elements are leather, brass, red gel, mahogany and velvet tassels; "
        "badges wear a band of nailed leather; and the games are played on satin and leather, their winners standing "
        "on leather tied with a satin ribbon.")
    tokens = frozenset(TOKENS)

    # ---- colour and paper
    def ink(self, night):
        """The words in the hand's two inks; the labels in the oxblood of the leather by day and the brass of its
        nails by night; a title set in plain letters in the candy gel's deepest red by day and its glow by night."""
        return dict(
            title=CANDY[5] if night else CANDY[1], shadow=X["shade"],
            body=self.hand.body[night], muted=self.hand.muted[night],
            rule=X["rule_night"] if night else X["rule_day"], accent=BRASS[5] if night else OX[1],
            tag=OX[3] if not night else OX[2], tag_ink=BRASS[6],
            fill=WINE[3] if night else ROSE[6], dim=X["dim_night"] if night else X["dim_day"],
        )

    def paper(self, p, night, uid="p"):
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        return A.bg_at(p, night, y)

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The wallpaper alone: the room has no sky but the one through its window. The drawing keeps the boxes the
        words take, `avoid`, for the lightning's flash, which lights the room only where there is a window for it to
        come in by (see `scene`)."""
        self.paper(p, night)
        p.avoid = list(avoid)

    def frame(self, p, night, webs=False):
        """The chesterfield's padded roll down the sides and along the foot; on a sheet with no tufted panel across
        its top, along its top as well."""
        A.frame(p, night)
        if not webs:
            k = -1 if night else 0
            for i, c in enumerate((OX[0], OX[5 + k], OX[3 + k], OX[1])):
                p.shapes["base"].append(f'<rect y="{i}" width="{p.w}" height="1" fill="{c}"/>')

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """The deep-buttoned panel of tufted leather across a header's top, parting either side of the month's mark
        when the header carries it (see `art.band`)."""
        box = self.mark_box(p)
        A.band(p, night, gap=(box[0], box[2]) if self.marked else None)

    def tag(self, p, x, y, w, h, night):
        """A block of oxblood leather, a note's number in brass on it, a nail at its corner."""
        p.rect(x, y, w, h, OX[3] if not night else OX[2])
        p.hline(x, x + w, y, OX[5] if not night else OX[4])
        p.hline(x, x + w, y + h - 1, OX[1])

    def title_text(self, p, x, y, s, night, scale):
        """Glossy gel capsules of candy red (see `art.capsule_title`). The drawing keeps each line, for the beam that
        passes down it in a moving header."""
        w = A.capsule_title(p, x, y, s, night, scale)
        p.titles = getattr(p, "titles", []) + [(x, y, s, scale, w)]
        return w

    # ---- the headers' scenes
    def scene(self, design, p, rule, night, motion):
        """On H1 the room: the wingback chair, the mirror, the table and its lamp at the left, and the window in the
        storm with the two pills before it at the right, each where the words leave it room, and by night in a moving
        header the lightning lighting the room above the words for its instant (see `art.room_flash`); and in a moving
        header the beam passing down each line of the title on the hand's period."""
        if motion:
            for n, (x, y, s, scale, w) in enumerate(getattr(p, "titles", ())):
                rain.scan(p, x, y, s, scale, w, n, self.hand.glint, C["white"])
        g = rule - 1
        spans = []
        if design == "H1":
            # The left of the room where the words leave its furniture room, its mirror where they leave that too;
            # the window at the right, drawn in to whatever room the words leave it, if that is enough.
            mirrored = p.clear_of_words(4, A.BAND + 1, 41, g - 40)
            if p.clear_of_words(4, g - 42, 61, g + 2):
                spans.append(A.room(p, 6, g, night, motion, mirrored=mirrored))
            elif p.clear_of_words(4, g - 42, 55, g + 2):
                spans.append(A.room(p, 6, g, night, motion, mirrored=mirrored, compact=True))
            for x0 in range(356, 363):
                if p.clear_of_words(x0 - 2, A.BAND + 1, 411, g + 2):
                    spans.append(A.storm_window(p, x0, 410, g, night, motion))
                    # By night the lightning lights the whole room for its instant, the wallpaper above the words,
                    # brightest round the window it comes in by.
                    avoid = getattr(p, "avoid", ())
                    if night and motion and len(avoid) > 1:
                        A.room_flash(p, (A.EDGE, A.BAND, p.w - A.EDGE, avoid[1][1] - 2), (x0, A.BAND + 6, 410, g - 14),
                                     holes=[self.mark_box(p)])
                    break
            # On the floor under the words, where they leave it room: a suitcase at the left, and an umbrella
            # dripping in its stand by the window.
            if spans and p.clear_of_words(58, g - 16, 82, g + 2):
                A.suitcase(p, 62, g, night)
                spans.append((60, 80))
            if len(spans) > 1 and p.clear_of_words(336, g - 19, 356, g + 2):
                A.umbrella(p, 343, g, night, motion)
                spans.append((338, 354))
            return spans
        x1 = p.w - A.EDGE - 1
        if design == "H2":
            # The fireside at the right, its pier mirror as high as the room goes.
            x0 = next((x for x in range(306, 346) if p.clear_of_words(x - 2, A.BAND + 1, p.w - 2, g + 3)), None)
            room = self._room(p, x0, x1, g, g - A.BAND - 2, 44) if x0 is not None else None
            if room:
                spans.append(A.fireside(p, x0, x1, g, night, motion, room))
        else:
            # The corner with the cheval glass at the right, rising the strip's whole height, the chair facing it.
            x0 = next((x for x in range(352, 386) if p.clear_of_words(x - 2, A.BAND + 1, p.w - 2, g + 3)), None)
            room = self._room(p, x0, x1, g, g - A.BAND - 2, 40) if x0 is not None else None
            if room:
                spans.append(A.mirror_corner(p, x0, x1, g, night, motion, room))
        avoid = getattr(p, "avoid", ())
        if spans and night and motion and len(avoid) > 1:
            # By night the storm's lightning lights the whole room above the words for its instant, though no
            # window shows here.
            A.room_flash(p, (A.EDGE, A.BAND, p.w - A.EDGE, avoid[1][1] - 2), (x0, A.BAND + 6, x1, g - 14),
                         holes=[self.mark_box(p)])
        return spans

    # ---- the headers on a phone
    PHONE_SCENE = 56    # the rows a phone's H1 keeps under its words for the whole room
    UNDER = {"H2": 70, "H3": 60}    # the rows a phone's H2 and H3 keep under theirs for the fireside and the glass

    @staticmethod
    def _room(p, x0, x1, g, most, least):
        """The rows free of words over the floor at row g between x0 and x1, `most` at the most, keeping three rows
        of margin above and two beside; None when fewer than `least` are free."""
        for room in range(most, least - 1, -1):
            if p.clear_of_words(x0 - 2, g - room - 3, x1 + 2, g + 3):
                return room
        return None

    def h1_narrow(self, h, night):
        """A phone's H1, its room given PHONE_SCENE rows under the words and the notes set under them, however many
        notes there are."""
        self.phone_scene_rows = self.PHONE_SCENE + 4 + 10 * len(self.said(h))
        try:
            return super().h1_narrow(h, night)
        finally:
            del self.phone_scene_rows

    def scene_narrow(self, design, p, y, night):
        """A phone's H1 scene: the whole room across the phone under the words (`art.phone_room`), built to the rows
        they leave free over the rule at `y`. A phone's H2 and H3 stand their heroes under their words instead (see
        `scene_under`)."""
        if design == "H1":
            room = self._room(p, 5, p.w - 5, y - 1, self.PHONE_SCENE - 2, 48)
            if room:
                A.phone_room(p, A.EDGE + 1, p.w - A.EDGE - 1, y - 1, night, room)
                p.grounded = True

    def phone_rows(self, design, title_w):
        """The rows a phone's H2 or H3 leaves under its words for its hero, whatever the words say (see
        `scene_under`)."""
        return self.UNDER[design]

    def scene_under(self, design, p, y0, y1, night):
        """A phone's hero under its words, across the phone, standing on the rule at y1 and built to the rows free
        over it: on H2 the fireside with the lamp at the left and the suitcase and the umbrella at the right
        (`art.phone_fireside`); on H3 the cheval glass with the chair facing it and the lamp beside it
        (`art.phone_mirror`)."""
        g = y1 - 1
        room = self._room(p, 5, p.w - 5, g, self.UNDER[design] - 4, 44)
        if not room:
            return
        if design == "H2":
            A.phone_fireside(p, A.EDGE + 1, p.w - A.EDGE - 1, g, night, room)
        else:
            A.phone_mirror(p, A.EDGE + 1, p.w - A.EDGE - 1, g, night, room)
        p.grounded = True

    def section_mark(self, p, x, y, night):
        """The two pills after SECTION A-A, the red and the blue, centred on its letters as near as the title over
        them leaves two units clear (see `art.pills_mark`)."""
        w, h = A.PILLS_W, A.PILLS_H
        for y0 in range(y, y + 10 - h):
            if p.clear_of_words(x - 2, y0 - 2, x + w + 2, y0 + h + 2):
                A.pills_mark(p, x, y0, night)
                return

    def strip_mark(self, p, x, y, night):
        """Round dark glasses beside a strip's title, the red pill caught in one lens and the blue in the other,
        raised so that they stay two rows clear of the tagline under the title, and never in the month's mark (see
        `art.spectacles`)."""
        w, h = A.SPECS_W, A.SPECS_H
        mx0, my0, mx1, my1 = self.mark_box(p)
        foot = max((b[3] for b in p.words), default=y + 12) - 1    # the tagline's box begins two rows under the title's
        for y0 in range(min(y - 4, foot - h + 1), y - 12, -1):
            if (p.clear_of_words(x - 2, y0 - 2, x + w + 2, y0 + h + 2)
                    and not (x < mx1 and mx0 < x + w and y0 < my1 and my0 < y0 + h)):
                A.spectacles(p, x, y0, night)
                return

    def rule_decor(self, p, x0, x1, y, seed, night):
        """The Persian runner laid along the floor where no scene stands (see `art.runner`); none under a phone's
        scene, which stands across the whole floor, nor on a drawing made lighter to fit its budget."""
        if not getattr(p, "grounded", False) and not p.lite:
            A.runner(p, x0, x1, y, night)

    def _finish(self, p, night):
        """The last pass, which a drawing made lighter keeps too: the file written as lightly as it can be, the same
        drawing unit for unit (see `Pix.compact`)."""
        if not p.lite:
            self.finish(p, night)
        p.compact(keep=("mark",))

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        """A banker's lamp in the corner of the closing notes, its green glass lit by night (see `art.lamp_mark`)."""
        A.lamp_mark(p, x + 1, y - 1, night)

    def _footed(self, p, night, last=False):
        """A footer once its cells are laid: the mahogany skirting along its foot, rising where the cells leave it
        room, and the open box with the two pills standing on it where they leave the wall free (see
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

    def heart(self, p, x, y):
        A.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        """A bar of the chesterfield's oxblood leather and brass by turns, `period` pixels a block, lit along its top
        and shaded along its foot."""
        for yy in range(y0, y0 + h):
            f = (yy - y0) / max(1, h - 1)
            band = 0 if f < 0.2 else (1 if f < 0.7 else 2)
            for xx in range(x0, x0 + w):
                brass = ((xx - x0) // period) % 2 == 0
                p.px(xx, yy, (BRASS[5], BRASS[4], BRASS[2])[band] if brass else (OX[4], OX[3], OX[1])[band])

    def link_colours(self, night):
        """A button of oxblood leather with its letters in pale satin and a dark edge; by night the leather darker,
        edged in brass, the letters in brass."""
        if night:
            return OX[1], BRASS[2], BRASS[5], OX[0]
        return OX[3], OX[0], SATIN[6], OX[2]

    def link_icon(self, index, night, ink):
        return A.ICONS[A.LINK_ICONS[index % len(A.LINK_ICONS)]], A.icon_pal(night, ink)

    def link_top(self, p, x0, x1, y, seed, night):
        """The button's leather rolled over at its top edge and close-nailed in brass along it, lit along the top and
        down the left, shaded down the right."""
        fill, edge, _, shade = self.link_colours(night)
        p.hline(1, p.w - 1, y + 1, OX[5] if not night else OX[3])
        p.vline(1, y + 1, y + 9, OX[5] if not night else OX[3])
        p.vline(p.w - 2, y + 2, y + 9, shade)
        for xx in range(x0 + 2, x1 - 2, 5):
            A.nail(p, xx, y + 2, night)

    # ---- the elements
    def card_bevel(self, night):
        return (WINE[5], WINE[0]) if night else (SATIN[6], ROSE[2])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A card as a panel of oxblood leather: a roll of it down its icon cell's edge held by two brass nails, a
        nail in each corner, and by night the icon's cell lit green, as the lamp lights what stands near it."""
        k = -1 if night else 0
        ink = self.ink(night)
        if night:
            for yy in range(y + 2, y + h - 2):
                for xx in range(x + 2, x + 10):
                    if p.get(xx, yy) == ink["fill"]:
                        p.px(xx, yy, FLAME[0])
        for yy in range(y + 1, y + h - 1):
            p.px(x + 10, yy, OX[5 + k])
            p.px(x + 11, yy, OX[3 + k])
            p.px(x + 12, yy, OX[1])
        A.nail(p, x + 10, y + 3, night)
        A.nail(p, x + 10, y + h - 5, night)
        for (nx, ny) in ((x + 1, y + 1), (x + w - 3, y + 1), (x + 1, y + h - 3), (x + w - 3, y + h - 3)):
            A.nail(p, nx, ny, night)

    def wire_ink(self, night):
        return BRASS[2] if night else BRASS[3]

    def wire_lights(self, p, cells, night, seed):
        """The wire as a curtain's brass cord, a velvet tassel hanging from it here and there where it runs level."""
        for i, (x, y, d) in enumerate(cells[4:-6]):
            if d == "h" and (i + seed) % 17 == 0 and all(p.get(x + dx, y + dy) is None for dx in (-1, 0, 1)
                                                         for dy in range(1, 7)):
                A.tassel(p, x, y + 1, night)

    def dashes(self, night):
        return [BRASS[4] if night else OX[3], WINE[5] if night else ROSE[2]]

    def ornament(self, kind, p, x, y, night):
        """The open box with the two pills in a free corner of the schematic."""
        if kind == "schematic":
            if p is not None:
                A.pill_box(p, x, y + 12, night, False)
            return (22, 15)
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as a stick of the title's candy-red gel."""
        A.gel_bar(p, bx, base, bw, v, night)

    def peak_mark(self, p, x, y, night):
        A.pill_drop(p, x, y - 1, night)

    def dial_ring(self, p, arc, night):
        """A gauge's ring of polished brass."""
        A.brass_ring(p, arc, 2.0, night)

    def dial_tick(self, p, x, y, night):
        A.nail(p, x - 1, y - 1, night)

    def dial_hub(self, p, cx, cy, night):
        A.boss(p, cx, cy, night)

    def material(self, i, xx, yy, y0, y1, lift, night):
        """The room's materials by turns: the chesterfield's leather deep-buttoned, the nails' brass, the mahogany in
        its grain, and the curtains' velvet in its folds."""
        k = -1 if night else 0
        kind = i % 4
        if kind == 0:
            c = OX[1] if (xx % 6 == 3 and (yy - y0) % 4 == 1) or (xx % 6 == 0 and (yy - y0) % 4 == 3) else OX[3 + k]
        elif kind == 1:
            c = BRASS[5 + k] if (xx + yy) % 5 == 0 else BRASS[4 + k]
        elif kind == 2:
            c = WOOD[4 + k] if (xx * 3 + (yy - y0) // 2) % 7 == 0 else WOOD[3 + k]
        else:
            c = VELVET[4 + k] if xx % 4 < 2 else VELVET[3 + k]
        return step(c, lift)

    def counter_cell(self, q, ox, oy, night):
        """A dark mahogany cell, 11 by 15, in a brass rim lit along its top."""
        q.rect(ox, oy, 11, 15, WOOD[1])
        q.hline(ox, ox + 11, oy, BRASS[4] if not night else BRASS[3])
        q.box(ox - 1, oy - 1, 13, 17, BRASS[1] if not night else BRASS[0])

    def counter_ink(self, night, dim):
        """A counter's digit in brass, a duller brass for a leading nought: an ink no other words take, so the digits
        are set over their cells."""
        return BRASS[3] if dim else BRASS[5]

    def timeline_line(self, p, x0, x1, y, night):
        """A brass curtain rod the releases hang from, up to today."""
        A.curtain_rod(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        """A tassel hung from the rod for a release, a longer one for a big release, a brass nail for a patch, an empty
        ring for one still to come, and for the repository's creation a red tassel."""
        if kind == "big":
            A.tassel(p, x, gy + 1, night, big=True)
        elif kind == "major":
            A.tassel(p, x, gy + 1, night)
        elif kind == "minor":
            A.nail(p, x - 1, gy + 2, night)
        elif kind == "made":
            A.tassel(p, x, gy + 1, night, ramp=CANDY)
        else:
            k = -1 if night else 0
            p.px(x - 1, gy + 1, BRASS[3 + k])
            p.px(x + 1, gy + 1, BRASS[2 + k])
            p.px(x, gy + 2, BRASS[2 + k])

    def today_mark(self, p, x, y, night):
        """A small banker's lamp over the rod's end at today, lit by night."""
        A.lamp_small(p, x - 3, y - 7, night)

    def avatar(self, p, cx, cy, i, person, night):
        A.face(p, cx, cy, i, person, night)

    def commit_bar(self, p, x, y, w, fill, night):
        A.gel_fill(p, x, y, w, fill, night)

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """A roll of oxblood leather round the seal, from r0 to r1, close-nailed in brass."""
        rad = (r0 + r1) / 2 - 0.5
        ring = [(cx + rad * math.cos(math.radians(a)), cy + rad * math.sin(math.radians(a))) for a in range(0, 361, 4)]
        pins = [(cx + rad * math.cos(math.radians(a)), cy + rad * math.sin(math.radians(a))) for a in range(0, 360, 30)]
        A.leather_ring(p, ring, (r1 - r0) / 2 - 0.3, night, nails=pins)

    def seal_mark(self, p, x, y, night):
        A.pill_drop(p, x + 1, y, night)

    def placard_board(self, p, night):
        """A panel of the room's wall: the damask, the chesterfield's roll round it and its tufted panel along the
        top."""
        self.paper(p, night, uid="pl")
        self.frame(p, night)
        A.band(p, night)

    def placard_mark(self, p, x, y, night):
        A.lamp_mark(p, x - 2, y - 5, night)

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """The set's touch on a badge, kept inside its shape: a band of the chesterfield's leather along its top two
        rows close-nailed in brass, and under it each block as the badge laid it, read off its middle row, bevelled:
        lit along its top where no letter sits, shaded along its foot and its far end."""
        h = s["h"]
        k = -1 if night else 0
        mid = h // 2
        row = [p.get(x, mid) for x in range(w)]
        first = next((x for x in range(w) if row[x]), 0)
        left = next((x for x in range(first, w) if row[x] != row[first]), w)
        tmp = Pix(w, h)
        tmp.hline(0, w, 0, OX[5 + k])
        tmp.hline(0, w, 1, OX[2 + k])
        x = 1 + seed % 4
        while x + 1 < w:
            tmp.px(x, 0, BRASS[6 + k])
            tmp.px(x + 1, 0, BRASS[4 + k])
            tmp.px(x, 1, BRASS[3 + k])
            tmp.px(x + 1, 1, BRASS[1])
            x += 5
        ty = self._text_y(s)
        for (a, b) in ((first, left), (left, w)):
            if b <= a:
                continue
            c = row[a]
            try:
                lit, dark = step(c, 1), step(c, -1)
            except KeyError:
                lit = dark = None
            for xx in range(a, b):
                if lit and ty > 2 and p.get(xx, 2) == c:
                    tmp.px(xx, 2, lit)
                if dark and p.get(xx, h - 1) == c:
                    tmp.px(xx, h - 1, dark)
            if dark:
                for yy in range(2, h - 1):
                    if p.get(b - 1, yy) == c:
                        tmp.px(b - 1, yy, dark)
        for (x, y), c in tmp.layers["base"].items():
            if inside(x, y, w, h, s["corner"]):
                p.px(x, y, c)

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

    def badge_label(self):
        return (OX[2], SATIN[6])

    def badge_gold(self):
        return (BRASS[4], WINE[0])

    def badge_states(self):
        return {"green": (VELVET[4], C["white"]), "yellow": (BRASS[5], WINE[0]), "red": (CANDY[2], C["white"]),
                "slate": (STORM[2], C["white"])}

    def badge_swatches(self):
        return {"red pill": (CANDY[2], C["white"], None), "coral": (OX[6], WINE[0], None),
                "rose": (ROSE[3], WINE[0], None), "brass": (BRASS[4], WINE[0], None),
                "velvet": (VELVET[4], C["white"], None), "glass": (GLASS[2], C["white"], None),
                "blue pill": (BLUE[3], C["white"], None), "night": (NIGHT[4], SATIN[6], None),
                "storm": (STORM[4], WINE[0], None), "mahogany": (WOOD[4], C["white"], None),
                "satin": (SATIN[5], WINE[0], "outline"), "wine": (WINE[6], C["white"], None),
                "oxblood": (OX[3], SATIN[6], "studs")}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        if pattern == "studs" and (x * 7 + y * 13) % 29 == 0 and y not in text_rows:
            return BRASS[4]
        return c

    def badge_outline(self, pattern):
        return SATIN[2] if pattern == "outline" else None

    def plate_colours(self, mode):
        """A plate's colours: the wallpaper's rose by day, its dots a tone deeper, framed in oxblood, the value on a
        block of leather; by night the wine-black paper framed in brass with the value on brass; live, the label on
        brass."""
        if mode == "day":
            return dict(paper=C["paper"], dot=ROSE[4], frame=OX[3], block=OX[2], ink=C["ink"], letters=SATIN[6])
        if mode == "night":
            return dict(paper=C["paper_n"], dot=WINE[4], frame=BRASS[3], block=BRASS[4], ink=C["body_night"],
                        letters=WINE[0])
        return dict(paper=BRASS[4], dot=BRASS[4], frame=WINE[1], edge=BRASS[2], ink=WINE[0])

    # ---- the games
    def game_squares(self, night):
        """A board of the box's satin lining and the chesterfield's oxblood leather, its stitching drawn in, the satin a
        tone down by night, as every board of the year is dimmer after dark."""
        return Stuff(RAMP["satin"], 4 if night else 5, "satin"), Stuff(RAMP["oxblood"], 3, "stitch")

    def game_frame(self, night):
        """A frame of carved mahogany."""
        return Stuff(RAMP["mahogany"], 3), "wood"

    def game_podium(self, night):
        """A podium of the chesterfield's leather, its stitching drawn in, tied with a ribbon of the box's satin, as a
        present is."""
        return Podium(Stuff(RAMP["oxblood"], 3, "stitch"), "ribbon", Stuff(RAMP["satin"], 5, "satin"))


SET = Choice()
