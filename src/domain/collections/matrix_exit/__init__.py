# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Exit set: a ringing phone on a wet city street, March's design in the Matrix collection, drawn in the
collection's hand.

Every sheet is a city street's wall in the March rain, overcast grey-blue concrete by day and navy-black and wet by
night, held in the riveted iron of the elevated railway, a lattice girder of the El across a header's top parting
either side of the month's mark and a granite kerb along the foot. Titles are neon signs on a dark board, the glass
tubes pale and unlit by day and by night burning the hand's phosphor, haloed on the board and blooming round it, one
letter guttering; in a moving header the terminal's beam passes down them on the hand's period, and the rain slants
across the whole sky behind them. The H1 opens on the street: at the left a phone booth of steel and glass under a
bishop's-crook streetlamp, its payphone ringing and its handset swinging off the hook, a pillar of the El braced to the
girder with a poster of a white rabbit on it, a traffic signal hung from the girder, and a figure in a long dark coat
striding to the booth; at the right a brick tenement with its fire escape, its windows lit green by night, someone
watching from one, and a vertical neon sign, HOTEL, glowing on the brick; under the words a manhole breathing steam
and a hydrant, and along the foot the wet street holding every light in shimmering streaks. An H2 stands the booth
close up and answered, someone in a long coat inside with the handset to an ear, under the streetlamp, an Agent
striding toward it and a pillar of the El rising from the girder beside it; an H3 the hotel's corner rising the
strip's full height, its sign, its fire escape and its doorway. SECTION A-A carries an EXIT sign, green enamel by day
and lit by night; a strip's title the payphone ringing; and the rule where no scene stands is an iron strap, riveted,
puddles of the rain on it ringing with drops. A phone's H1 holds the whole street under its words, its H2 the booth
answered and its H3 the hotel, under theirs whatever they say. The footer stands on the El's girder, deepening where
its cells leave it room, with the booth on it after a title block's last cell and a streetlamp's lantern in the corner
of its notes, both lit by night; link buttons are riveted plates of iron, each with its own thing of the street; the
elements are built of neon tubes, the El's iron and rivets, lanterns hung from the girder and the street's people in
dark glasses; badges carry a band of riveted iron; and the games are played on boards of concrete and iron in an iron
frame, their moves lettered in the tubes without the board, and their winners stand on a podium of the tenement's
brick hung with bunting.
"""
from __future__ import annotations

import math

from ...holidays.designs.badges import inside
from ...holidays.designs.materials import Podium, Stuff
from ...holidays.pixel import Pix
from ..hand import CollectionSet
from .. import rain as code
from . import art as A
from .palette import C, RAMP, TOKENS, X, step

IRON, FLAME, WALL, STREET = RAMP["iron"], RAMP["flame"], RAMP["wall"], RAMP["street"]
BOARD, BRICK, RUST, STEEL = RAMP["board"], RAMP["brick"], RAMP["rust"], RAMP["steel"]
GLASS, MORTAR, TUBE, HAIR = RAMP["glass"], RAMP["mortar"], RAMP["tube"], RAMP["hair"]
GRANITE, ENAMEL = RAMP["granite"], RAMP["enamel"]


class Exit(CollectionSet):
    key = "matrix-exit"
    name = "Exit"
    collection = "matrix"
    tagline = "A ringing phone on a wet city street: neon titles, the El's iron and the rain, green by night."
    about = (
        "Every sheet is a city street's wall in the March rain, overcast grey-blue concrete by day and navy-black and "
        "wet by night, held in the riveted iron of the elevated railway, a lattice girder of the El across the top and "
        "a granite kerb along the foot, the rain slanting across the whole sky. Titles are neon signs on a dark board, "
        "their glass tubes pale and unlit by day and burning green by night, blooming round the sign, one letter "
        "guttering. The headers open on the street: a phone booth of steel and glass under a bishop's-crook "
        "streetlamp, its payphone ringing and its handset swinging off the hook, a pillar of the El braced to the "
        "girder, a traffic signal showing green and a figure in a long dark coat striding to the booth through the "
        "rain, and a brick tenement with its fire escape, its windows lit green by night and a vertical neon sign, "
        "HOTEL, glowing on the brick; a section's header stands the booth answered close up, an Agent striding toward "
        "it, and a strip's the hotel's corner rising its full height. An EXIT sign hangs beside SECTION A-A, a "
        "payphone rings beside a strip's title, and puddles on the rule ring with the rain. On a phone the whole "
        "street stands under the words, and a section's and a strip's heroes under theirs. Along the foot the wet "
        "street holds every light in shimmering streaks. The footer stands on the El's girder with the booth on it, "
        "lit by night; links are riveted iron plates; the elements are neon tubes, rivets and lanterns hung from the "
        "girder; badges wear a band of riveted iron; and the games are played on concrete and iron, their winners "
        "standing on the tenement's brick hung with bunting.")
    tokens = frozenset(TOKENS)

    # ---- colour and paper
    def ink(self, night):
        """The words in the hand's two inks; the labels in the El's iron by day and the neon's green by night; a title
        set in plain letters in the sign's board black by day and its neon by night."""
        return dict(
            title=FLAME[5] if night else BOARD[1], shadow=X["shade"],
            body=self.hand.body[night], muted=self.hand.muted[night],
            rule=X["rule_night"] if night else X["rule_day"], accent=FLAME[4] if night else IRON[2],
            tag=IRON[3] if not night else IRON[2], tag_ink=FLAME[5] if night else WALL[6],
            fill=STREET[4] if night else WALL[6], dim=X["dim_night"] if night else X["dim_day"],
        )

    def paper(self, p, night, uid="p"):
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        return A.bg_at(p, night, y)

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The street wall, the city's overcast hiding every star; and across the sky above the words the rain
        falling, behind the title, and by night the neon's bloom round it, both ending above the text the layout
        sets under the title (its second box in `avoid`) and keeping out of the month's mark (see `art.sky_rain`
        and `art.neon_bloom`)."""
        self.paper(p, night)
        if len(avoid) > 1:
            bottom, holes = avoid[1][1], [self.mark_box(p)]
            A.sky_rain(p, (A.EDGE, A.GIRDER, p.w - A.EDGE, bottom), night, holes)
            if night:
                A.neon_bloom(p, avoid[0], (A.EDGE, 0, p.w - A.EDGE, bottom), holes)

    def frame(self, p, night, webs=False):
        """The El's iron columns down the sides and the kerb along the foot; on a sheet with no girder across its top,
        a beam of riveted iron along its top as well."""
        A.frame(p, night)
        if not webs:
            k = -1 if night else 0
            for i, c in enumerate((IRON[0], IRON[5 + k], IRON[3 + k], IRON[1])):
                p.shapes["base"].append(f'<rect y="{i}" width="{p.w}" height="1" fill="{c}"/>')

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """The El's lattice girder across a header's top, parting either side of the month's mark when the header
        carries it (see `art.girder`)."""
        box = self.mark_box(p)
        A.girder(p, night, gap=(box[0], box[2]) if self.marked else None)

    def tag(self, p, x, y, w, h, night):
        """A plate of the El's iron, a note's number on it, riveted at its corners."""
        p.rect(x, y, w, h, IRON[3] if not night else IRON[2])
        p.hline(x, x + w, y, IRON[5] if not night else IRON[4])
        p.hline(x, x + w, y + h - 1, IRON[1])

    def title_text(self, p, x, y, s, night, scale):
        """A neon sign on a dark board (see `art.neon_title`). The drawing keeps each line, for the beam that passes
        down it in a moving header."""
        w = A.neon_title(p, x, y, s, night, scale)
        p.titles = getattr(p, "titles", []) + [(x, y, s, scale, w)]
        return w

    def section_mark(self, p, x, y, night):
        """An EXIT sign after SECTION A-A, centred on its letters as near as the title's board over them leaves two
        units clear, and set smaller where it leaves less, its foot always two rows clear of the words the layout
        sets under SECTION A-A, from row y + 11 (see `art.exit_sign`)."""
        w = len(A.EXIT_SIGN[0])
        for art, small in ((A.EXIT_SIGN, False), (A.EXIT_SMALL, True)):
            h = len(art)
            for y0 in range(y - 1, y + 10 - h):
                if p.clear_of_words(x - 2, y0 - 2, x + w + 2, y0 + h + 2):
                    A.exit_sign(p, x, y0, night, small)
                    return

    def strip_mark(self, p, x, y, night):
        """The payphone ringing beside a strip's title, raised so that its foot stays two rows clear of the tagline
        the layout sets under the title, and never in the month's mark (see `art.payphone`)."""
        w, h = len(A.PAYPHONE[0]), len(A.PAYPHONE)
        mx0, my0, mx1, my1 = self.mark_box(p)
        foot = max((b[3] for b in p.words), default=y + 12) - 3    # the tagline's box begins under the board's
        for y0 in range(min(y - 11, foot - h + 1), y - 17, -1):
            if (p.clear_of_words(x - 2, y0 - 2, x + w + 2, y0 + h + 2)
                    and not (x < mx1 and mx0 < x + w and y0 < my1 and my0 < y0 + h)):
                A.payphone(p, x, y0, night)
                return

    def rule_decor(self, p, x0, x1, y, seed, night):
        """The rule where no scene stands is an iron strap, riveted, with a puddle of the rain on it here and there
        and a drop splashing in it (see `art.rule_bits`); none under a phone's scene, which stands across the whole
        rule."""
        if not getattr(p, "grounded", False):
            A.rule_bits(p, x0, x1, y, seed, night)

    # ---- the headers' scenes
    def scene(self, design, p, rule, night, motion):
        """On H1 the street in the rain: the booth, the streetlamp and the striding figure at the left and the
        tenement with its fire escape and its sign at the right, each where the words leave it room, and the rain
        falling across both sides; and in a moving header the beam passing down each line of the title on the hand's
        period."""
        if motion:
            for n, (x, y, s, scale, w) in enumerate(getattr(p, "titles", ())):
                code.scan(p, x, y, s, scale, w, n, self.hand.glint, C["white"])
        g = rule - 1
        spans, boxes, cone, keep, lights = [], [], None, [], []
        if design == "H1":
            top = A.GIRDER + 1
            # The wet street in front of the kerb as deep as the words above it leave room for; none under notes
            # set low over the rule, when everything stands on the rule itself.
            depth = next((d for d in A.STREET_ROWS if p.clear_of_words(4, g - d - 2, p.w - 4, g + 2)), 0)
            gs = g - depth
            wet = depth > 0
            if wet:
                A.street(p, A.EDGE, p.w - A.EDGE, gs, g, night)
            if p.clear_of_words(4, top, 40, g + 2):
                walker = p.clear_of_words(40, gs - 28, 60, g + 2)
                posted = p.clear_of_words(34, top, 53, gs + 1)
                reach = next((r for r in (16, 13, 10) if p.clear_of_words(48, top, 52 + r, top + r + 2)), 0)
                span, cone, glass, (lx, bx, px) = A.corner(p, 6, gs, night, motion, walker=walker, posted=posted,
                                                           braces=(reach, reach) if posted else (0, 0))
                if posted and p.clear_of_words(82, top, 96, top + 26):
                    A.signal(p, 88, top - 1, night, motion)
                    lights.append((88, 1, FLAME[5], FLAME[3]) if night else (88, 1, FLAME[4], FLAME[2]))
                spans.append(span)
                keep.append(glass)
                if night:
                    lights += [(lx, 2, FLAME[5], FLAME[3]), (bx, 4, FLAME[4], FLAME[2])]
                else:
                    lights.append((bx, 4, WALL[6], WALL[5]))
                    if px:
                        lights.append((px, 4, IRON[2], IRON[3]))
            for x0 in range(356, 370):
                if p.clear_of_words(x0 - 2, top, 411, g + 2):
                    span, sx = A.tenement(p, x0, 410, gs, night, motion)
                    spans.append(span)
                    lights.append((sx, 2, FLAME[5], FLAME[3]) if night else (sx, 2, BOARD[3], WALL[1]))
                    break
            # On the street under the words, where they leave it room: a manhole breathing steam, and a hydrant at
            # the kerb by the tenement; and by night the title's neon lying in the wet between them as a sheen.
            if spans and p.clear_of_words(60, gs - 11, 84, g + 2):
                A.steam(p, 72, gs, night, motion)
            if len(spans) > 1 and p.clear_of_words(338, gs - 10, 356, g + 2):
                A.hydrant(p, 344, gs, night)
                spans.append((341, 352))
                lights.append((347, 2, None, BRICK[1]) if night else (347, 2, BRICK[4], BRICK[3]))
            if wet:
                pools = [(x, hw + 8, FLAME[3]) for x, hw, bright, _ in lights[:2]] if night and cone else []
                if night:
                    # The neon lies in the wet as one long soft sheen under the sign, not a streak a letter: from
                    # the kerb it is too far up the wall to break into its letters.
                    for tx, ty, ts, tscale, tw in getattr(p, "titles", ())[:1]:
                        pools.append((tx + tw // 2, tw // 2 + 6, FLAME[2]))
                A.reflections(p, lights, A.EDGE, p.w - A.EDGE, gs, g, pools)
                A.ripples(p, A.EDGE, p.w - A.EDGE, gs, g, motion, night)
            xl = next((x for x in range(62, 20, -1) if p.clear_of_words(4, top, x + 2, g + 1)), None)
            xr = next((x for x in range(354, 400) if p.clear_of_words(x - 2, top, 411, g + 1)), None)
            if xl:
                boxes.append((A.EDGE, top, xl, g + 1))
            if xr:
                boxes.append((xr, top, p.w - A.EDGE, g + 1))
            if boxes:
                A.rain(p, boxes, night, lit=cone, keep=keep)
        elif design == "H2":
            # The booth answered, close up at the right of the words, as tall as the sheet between the girder and
            # the rule, drawn in to the columns the words leave it.
            x0 = next((x for x in range(296, 366) if p.clear_of_words(x - 2, A.GIRDER, p.w - 2, g + 3)), None)
            if x0 is not None and g - A.GIRDER - 1 >= 56:
                spans.append(A.callbox(p, x0, p.w - A.EDGE - 1, g, night, motion, room=g - A.GIRDER - 1))
        else:
            # The hotel's corner rising the strip's full height at its right, its sign hung off the corner.
            x0 = next((x for x in range(338, 368) if p.clear_of_words(x - 2, A.GIRDER, p.w - 2, g + 3)), None)
            if x0 is not None and g - A.GIRDER - 1 >= 48:
                spans.append(A.hotel(p, x0, p.w - A.EDGE - 1, g, night, motion, room=g - A.GIRDER - 1))
        return spans

    # ---- the phones
    PHONE_SCENE = 56     # the rows a phone's H1 gives its street under its words and its notes
    # The rows a phone's H2 and H3 ask for under their words, whatever the words: room for the booth close up with
    # the lamp over it, and for the hotel's corner with its sign at its full height.
    UNDER = {"H2": 64, "H3": 60}

    @staticmethod
    def _room(p, x0, x1, g, most, least):
        """The rows free of words over the kerb at row g between x0 and x1, `most` at the most, keeping three rows of
        margin above and two beside; None when fewer than `least` are free."""
        for room in range(most, least - 1, -1):
            if p.clear_of_words(x0 - 2, g - room - 3, x1 + 2, g + 3):
                return room
        return None

    def h1_narrow(self, h, night):
        """A phone's H1, its street given PHONE_SCENE rows under the words and the notes set under them, however many
        notes there are."""
        self.phone_scene_rows = self.PHONE_SCENE + 4 + 10 * len(self.said(h))
        try:
            return super().h1_narrow(h, night)
        finally:
            del self.phone_scene_rows

    def scene_narrow(self, design, p, y, night):
        """A phone's H1 scene: the whole street across the phone under the words (`art.phone_street`), built to the
        rows they leave free over the rule at `y`. A phone's H2 and H3 stand their heroes under their words instead
        (see `scene_under`)."""
        if design == "H1":
            room = self._room(p, 5, p.w - 5, y - 1, self.PHONE_SCENE - 2, 44)
            if room:
                A.phone_street(p, y - 1, night, room)
                p.grounded = True

    def phone_rows(self, design, title_w):
        """The rows a phone's H2 or H3 leaves under its words for its hero, whatever the words say (see
        `scene_under`)."""
        return self.UNDER[design]

    def scene_under(self, design, p, y0, y1, night):
        """A phone's hero under its words, across the phone, standing on the rule at y1 and built to the rows free
        over it: on H2 the booth answered under the streetlamp with the Agent striding to it and a pillar of the El
        (`art.callbox`); on H3 the hotel's corner with its sign, its windows, its fire escape and its doorway
        (`art.hotel`)."""
        g = y1 - 1
        room = self._room(p, 5, p.w - 5, g, self.UNDER[design] - 4, 40)
        if not room:
            return
        if design == "H2":
            A.callbox(p, A.EDGE + 1, p.w - A.EDGE - 1, g, night, False, room, top=g - room + 1)
        else:
            A.hotel(p, A.EDGE + 1, p.w - A.EDGE - 1, g, night, False, room)
        p.grounded = True

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        """A streetlamp's lantern on its bracket in the corner of the closing notes, lit by night."""
        A.lamp_mark(p, x + 2, y - 2, night)

    def _footed(self, p, night, last=False):
        """A footer once its cells are laid: the El's girder along its foot, deepening where the cells leave it room,
        and the phone booth standing on it where they leave the wall free (see `art.footing`): on a title block only
        after its `last` cell, the way back up."""
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
        """A bar of the El's painted iron and the kerb's granite by turns, `period` pixels a block, lit along its top
        and shaded along its foot."""
        for yy in range(y0, y0 + h):
            f = (yy - y0) / max(1, h - 1)
            band = 0 if f < 0.2 else (1 if f < 0.7 else 2)
            for xx in range(x0, x0 + w):
                iron = ((xx - x0) // period) % 2 == 0
                p.px(xx, yy, (IRON[5], IRON[4], IRON[2])[band] if iron else (GRANITE[6], GRANITE[5], GRANITE[3])[band])

    def link_colours(self, night):
        """A plate of the El's painted iron, its letters pale, with a dark edge; by night a neon sign's dark board,
        edged in steel, its letters burning the hand's phosphor."""
        if night:
            return BOARD[2], STEEL[2], FLAME[5], BOARD[0]
        return IRON[4], IRON[0], TUBE[6], IRON[2]

    def link_icon(self, index, night, ink):
        return A.ICONS[A.LINK_ICONS[index % len(A.LINK_ICONS)]], A.icon_pal(night, ink)

    def link_top(self, p, x0, x1, y, seed, night):
        """The plate's rivets along its top edge and its bevel, lit along the top and down the left, shaded down the
        right; by night the board's rim catches the neon along its top."""
        fill, edge, _, shade = self.link_colours(night)
        lit = STEEL[4] if night else IRON[6]
        p.hline(1, p.w - 1, y + 1, lit)
        p.vline(1, y + 1, y + 9, lit)
        p.vline(p.w - 2, y + 2, y + 9, shade)
        for xx in range(x0 + 2, x1 - 2, 9):
            A.rivet(p, xx, y + 2, night) if not night else p.px(xx, y + 2, FLAME[3])

    # ---- the elements
    def card_bevel(self, night):
        return (STEEL[3], BOARD[0]) if night else (STEEL[6], IRON[2])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A card as a plate of the El's painted iron: a strap of iron down its icon cell's edge held by two rivets,
        a rivet in each corner, and by night the icon's cell lit like a window, the hand's phosphor."""
        k = -1 if night else 0
        ink = self.ink(night)
        if night:
            for yy in range(y + 2, y + h - 2):
                for xx in range(x + 2, x + 10):
                    if p.get(xx, yy) == ink["fill"]:
                        p.px(xx, yy, FLAME[0])
        for yy in range(y + 1, y + h - 1):
            p.px(x + 10, yy, IRON[5 + k])
            p.px(x + 11, yy, IRON[3 + k])
            p.px(x + 12, yy, IRON[1])
        A.rivet(p, x + 10, y + 3, night)
        A.rivet(p, x + 10, y + h - 5, night)
        for (rx, ry) in ((x + 1, y + 1), (x + w - 3, y + 1), (x + 1, y + h - 3), (x + w - 3, y + h - 3)):
            A.rivet(p, rx, ry, night)

    def wire_ink(self, night):
        return STEEL[3] if night else IRON[3]

    def wire_lights(self, p, cells, night, seed):
        """The wire as a cable strung along the El, raindrops hanging from it here and there where it runs level,
        catching the street's light, and by night the hand's phosphor."""
        drop = FLAME[4] if night else GLASS[6]
        for i, (x, y, d) in enumerate(cells[4:-6]):
            if d == "h" and (i + seed) % 11 == 0 and p.get(x, y + 1) is None and p.get(x, y + 2) is None:
                p.px(x, y + 1, drop)
                p.px(x, y + 2, (FLAME[2] if night else GLASS[4]))

    def dashes(self, night):
        return [FLAME[4] if night else IRON[4], STREET[5] if night else WALL[2]]

    def ornament(self, kind, p, x, y, night):
        """The phone booth and its streetlamp in a free corner of the schematic."""
        if kind == "schematic":
            if p is not None:
                A.booth_mark(p, x + 9, y, night)
                A.lamp_mark(p, x, y + 2, night)
            return (24, 24)
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as a neon tube stood up on its board."""
        A.neon_bar(p, bx, base, bw, v, night)

    def peak_mark(self, p, x, y, night):
        A.signal_mark(p, x, y - 4, night)

    def dial_ring(self, p, arc, night):
        """A gauge's ring of the El's painted iron."""
        A.iron_ring(p, arc, 2.0, night)

    def dial_tick(self, p, x, y, night):
        A.rivet(p, x - 1, y - 1, night)

    def dial_hub(self, p, cx, cy, night):
        A.bolt(p, cx, cy, night)

    def material(self, i, xx, yy, y0, y1, lift, night):
        """The street's materials by turns: brick in its courses, the El's iron set with rivets, wet concrete streaked
        by the rain, and the booth's steel."""
        k = -1 if night else 0
        kind = i % 4
        if kind == 0:
            c = MORTAR[3 + k] if (yy - y0) % 3 == 2 or (xx + 4 * (((yy - y0) // 3) % 2)) % 8 == 0 else BRICK[4 + k]
        elif kind == 1:
            c = IRON[6 + k] if (xx % 5 == 1 and yy % 4 == 1) else IRON[4 + k]
        elif kind == 2:
            c = WALL[3 + k] if (xx * 7) % 11 == 0 else WALL[4 + k]
        else:
            c = STEEL[5 + k] if yy % 2 else STEEL[4 + k]
        return step(c, lift)

    def counter_cell(self, q, ox, oy, night):
        """A neon sign's dark board, 11 by 15, in a rim of steel lit along its top, held by four rivets."""
        q.rect(ox, oy, 11, 15, BOARD[2])
        q.hline(ox, ox + 11, oy, STEEL[4] if not night else STEEL[2])
        q.box(ox - 1, oy - 1, 13, 17, IRON[1] if not night else IRON[0])

    def counter_ink(self, night, dim):
        """A counter's digit bent of neon: pale glass by day and the hand's phosphor by night, a dimmer tube for a
        leading nought. Each is an ink no other words take, so the digits are set over their boards."""
        if night:
            return FLAME[3] if dim else FLAME[6]
        return TUBE[2] if dim else TUBE[6]

    def timeline_line(self, p, x0, x1, y, night):
        """The El's girder the releases hang from, up to today."""
        A.girder_line(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        """A lantern hung from the girder for a release, a bigger one for a big release, a rivet for a patch, an
        unlit frame for one still to come, and for the repository's creation the phone booth's little sign."""
        if kind == "big":
            A.lantern(p, x, gy + 1, night, big=True)
        elif kind == "major":
            A.lantern(p, x, gy + 1, night)
        elif kind == "minor":
            A.rivet(p, x - 1, gy + 2, night)
        elif kind == "made":
            A.signal_mark(p, x - 2, gy + 3, night)
        else:
            A.lantern(p, x, gy + 1, night, lit=False)

    def today_mark(self, p, x, y, night):
        """A small traffic signal over the girder's end at today, its green lamp lit."""
        A.signal_small(p, x - 2, y - 7, night)

    def avatar(self, p, cx, cy, i, person, night):
        A.face(p, cx, cy, i, person, night)

    def commit_bar(self, p, x, y, w, fill, night):
        A.neon_fill(p, x, y, w, fill, night)

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """A ring of the El's painted iron round the seal, from r0 to r1, set with rivets."""
        rad = (r0 + r1) / 2 - 0.5
        ring = [(cx + rad * math.cos(math.radians(a)), cy + rad * math.sin(math.radians(a))) for a in range(0, 361, 4)]
        pins = [(cx + rad * math.cos(math.radians(a)), cy + rad * math.sin(math.radians(a))) for a in range(0, 360, 30)]
        A.iron_ring(p, ring, (r1 - r0) / 2 - 0.3, night, rivets=pins)

    def seal_mark(self, p, x, y, night):
        A.sprite(p, x, y, A.ICONS["handset"][1:4], A.icon_pal(night))

    def placard_board(self, p, night):
        """A sign on the street wall: the concrete, the El's iron round it and its girder along the top."""
        self.paper(p, night, uid="pl")
        self.frame(p, night)
        A.girder(p, night)

    def placard_mark(self, p, x, y, night):
        A.lamp_mark(p, x - 2, y - 6, night)

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """The set's touch on a badge, kept inside its shape: a band of the El's riveted iron along its top two rows,
        and under it each block as the badge laid it, read off its middle row, bevelled: lit along its top where no
        letter sits, shaded along its foot and its far end."""
        h = s["h"]
        k = -1 if night else 0
        mid = h // 2
        row = [p.get(x, mid) for x in range(w)]
        first = next((x for x in range(w) if row[x]), 0)
        left = next((x for x in range(first, w) if row[x] != row[first]), w)
        tmp = Pix(w, h)
        tmp.hline(0, w, 0, IRON[5 + k])
        tmp.hline(0, w, 1, IRON[2 + k])
        x = 1 + seed % 4
        while x + 1 < w:
            tmp.px(x, 0, IRON[6 + k])
            tmp.px(x, 1, IRON[0])
            x += 6
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
        return (IRON[3], TUBE[6])

    def badge_gold(self):
        return (RUST[5], BOARD[0])

    def badge_states(self):
        return {"green": (ENAMEL[3], C["white"]), "yellow": (RUST[6], BOARD[0]), "red": (BRICK[3], C["white"]),
                "slate": (STEEL[3], C["white"])}

    def badge_swatches(self):
        return {"brick": (BRICK[3], C["white"], None), "hydrant": (BRICK[4], C["white"], None),
                "rust": (RUST[5], BOARD[0], None), "amber": (RUST[6], BOARD[0], None),
                "enamel": (ENAMEL[3], C["white"], None), "iron": (IRON[3], TUBE[6], "rivets"),
                "glass": (GLASS[3], C["white"], None), "wall": (WALL[3], BOARD[0], None),
                "street": (STREET[6], C["white"], None), "mortar": (MORTAR[2], C["white"], None),
                "board": (BOARD[2], TUBE[6], None), "tube": (TUBE[5], BOARD[0], "outline"),
                "coat": (HAIR[6], C["white"], None)}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        if pattern == "rivets" and (x * 7 + y * 13) % 29 == 0 and y not in text_rows:
            return IRON[6]
        return c

    def badge_outline(self, pattern):
        return STEEL[3] if pattern == "outline" else None

    def plate_colours(self, mode):
        """A plate's colours: the street wall's concrete by day, its dots a tone lighter, framed in the El's iron, the
        value on a block of it; by night the wet navy wall framed in steel with the value on rust; live, the label on
        rust."""
        if mode == "day":
            return dict(paper=C["paper"], dot=WALL[4], frame=IRON[3], block=IRON[3], ink=C["ink"], letters=TUBE[6])
        if mode == "night":
            return dict(paper=C["paper_n"], dot=STREET[5], frame=STEEL[4], block=RUST[5], ink=C["body_night"],
                        letters=BOARD[0])
        return dict(paper=RUST[5], dot=RUST[5], frame=BOARD[1], edge=RUST[3], ink=BOARD[0])

    # ---- the games
    def game_title(self, p, x, y, s, night, scale):
        """A move, and the Hall's totals, without the board a title hangs on, a move being one of the sheet's words:
        by night bent in the sign's glass tubes alone, burning the hand's phosphor and glowing on the wall; by day in
        the board's black, the pale glass of an unlit tube catching the light along each letter's upper edge."""
        if night:
            return A.neon_title(p, x, y, s, night, scale, board=False)
        n = len(p.words)
        p.text(x - 1, y - 1, s, TUBE[6], "57", scale)
        del p.words[n:]          # the glass's light on the letters, not a word of its own
        return p.text(x, y, s, BOARD[1], "57", scale)

    def game_squares(self, night):
        """A board of the El's riveted iron on the street wall's concrete, the concrete a tone down by night, as every
        board of the year is dimmer after dark."""
        return Stuff(RAMP["wall"], 4 if night else 5, "stone"), Stuff(RAMP["iron"], 4, "metal")

    def game_frame(self, night):
        """A frame of the El's iron, riveted."""
        return Stuff(RAMP["iron"], 2), "iron"

    def game_podium(self, night):
        """A podium of the tenement's brick in its courses, hung with bunting in the board's colours."""
        return Podium(Stuff(RAMP["brick"], 3, "tile"), "bunting")


SET = Exit()
