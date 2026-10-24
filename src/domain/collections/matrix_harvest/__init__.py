# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Harvest set: the fields where the machines grow us, October's design in the Matrix collection, drawn in the
collection's hand, for Halloween.

Every sheet is the sky over the fields: ashen lavender by day, streaked with a high overcast in its own tones, and
by night the black-purple of the storm. Ribbed black conduit runs round its edges, clamped in dark metal at the
corners, and across a header's top the cables hang in swags from clamp to clamp, parting either side of the top
centre when the header carries the month's mark. Across a header's sky, behind the title, the storm drifts: heavy
clouds in rows, lit along their upper edges, dark underneath by day and lit green from below by night by the glow of
the fields, and lightning crawling through them, forked, striking twice on its loop, a bolt of it striking down among
the far towers of an H1, the clouds lit round it and by night the whole sky flashing faintly as it strikes. Titles
are glass tubes of phosphor fluid: a little empty glass at the top of every tube and the fluid's surface a bright line
under it, the fluid bright under the surface and denser at its foot, pale glass walls catching the light at the left
and in shade at the right, each letter outlined dark, a dark metal cap on every stroke's end, bubbles rising through
them; by night they glow, and in a moving header the beam passes down them on the hand's period. The H1 opens on the
fields: at the left a tower of glass pods round its segmented spine, each pod glowing green with a sleeper curled in
its fluid, cables running up from the tower into the dark, and beyond it the next towers fading into the haze; at the
right the harvester, a spidery machine of knuckled arms and a cluster of red eyes, three of them blinking, clinging
to a tower and drawing a pod out of its slot, or the tower alone, risen higher, where a long title leaves the
harvester no room; and along the foot, wherever the words leave room, the towers of the fields stand in rows to the
horizon under the glow of their pods. An H2 stands the awakening at the right, risen the full height of its sky: a
pod drawn from the tower standing open on its pedestal, glowing, its rim collared in metal, a sleeper risen out of
its fluid to the waist, gasping, the cables from his skull and his back running into the tower, and over him the
doctor let down from the dark on its cable, its red eyes on him and its claws reaching for the jack in his neck; an
H3 the pod tree rising the strip's full height, a trunk of ribbed conduit whose cables arch out like a willow's
boughs, hung with glowing pods like fruit at harvest, the more the taller the strip. SECTION A-A carries a pod lying
on its side, a strip's title a pod standing, and the rule where no scene stands short lengths of cable, clamped, a
pulse of phosphor in each. A phone's H1 holds the whole of the fields under its words, the tower, the harvester at
its work and the fields to the horizon; its H2 the awakening and its H3 the pod tree, its boughs arching across the
phone, under theirs whatever they say. The footer stands on the trench's cables, a pulse of phosphor running in them,
a second course of conduit laid on them where its cells leave it room, with a pod plugged into its socket after a
title block's last cell, burning by night, and the machines' red eyes watching from the corner of its notes; BUILT
WITH carries a heart of glass full of the fluid, and the scale's bar is a tube of it banded in metal. Link buttons are
plates of dark metal under ribbed conduit, each with its own sprite of the fields; the elements are built of pods'
control panels, cables carrying the code, tubes of the fluid, conduit and the machines' red eyes; badges carry a band
of ribbed conduit; and the games are played on boards of the pods' glass and the towers' riveted metal in a frame of
the conduit's rubber, their winners standing on a podium of the towers' dark metal, cobwebbed in its corners.
"""
from __future__ import annotations

from ...holidays.designs import WIDE
from ...holidays.designs.materials import Podium, Stuff
from ..hand import CollectionSet
from .. import rain
from . import art as A
from .palette import C, RAMP, TOKENS, X, step

FLAME, METAL, ASH, STORM, GLASS = RAMP["flame"], RAMP["metal"], RAMP["ash"], RAMP["storm"], RAMP["glass"]
COPPER = RAMP["copper"]


class Harvest(CollectionSet):
    key = "matrix-harvest"
    name = "Harvest"
    collection = "matrix"
    # How deep the conduit reaches into a trophy file, in units: its top, its sides, its foot, and the clamps at its
    # corners.
    trophy_frame = (4, 4, 4, 6)
    tagline = "The fields where the machines grow us: towers of glowing pods under a Halloween storm."
    about = (
        "Every sheet is the sky over the fields where the machines grow us, ashen lavender by day and by night a "
        "black-purple storm, framed in ribbed black conduit with cables hung in swags across the top, storm clouds "
        "drifting across it and green lightning crawling through them. Titles are glass tubes of glowing phosphor "
        "fluid, capped in dark metal, bubbles rising through them. The headers open on the fields: a tower of glass "
        "pods glowing green, each holding a sleeper curled in its fluid, cables running up into the dark and the next "
        "towers fading into the haze beyond it; and the harvester, a spidery machine of knuckled arms and red eyes, "
        "clinging to a tower and plucking a pod from it, while the towers of the fields stand in rows to the horizon "
        "along the foot. A section's header stands the awakening, a sleeper risen gasping out of an open pod as the "
        "doctor is let down from the dark to pull his jacks, and a strip's the pod tree, its cables arching out like a "
        "willow's boughs hung with glowing pods. A pod lies beside SECTION A-A and stands beside a strip's title, and "
        "lengths of cable lie along the rule. On a phone the whole of the fields stands under the words, and a "
        "section's and a strip's heroes under theirs. The footer stands on the trench's cables with a pod in its "
        "socket, glowing by night; links are metal plates under ribbed conduit; the elements are control panels, "
        "cables carrying the code, tubes of the fluid and the machines' red eyes; badges wear a band of conduit; and "
        "the games are played on glass and riveted metal, their winners standing on a podium of dark metal, cobwebbed "
        "in its corners.")
    tokens = frozenset(TOKENS)

    # ---- colour and paper
    def ink(self, night):
        """The words in the hand's two inks; words in the title's ink in the tubes' phosphor, its darkest tone by day,
        the rules in the storm's violet, and labels in deep violet by day and phosphor by night."""
        return dict(
            title=FLAME[3] if night else FLAME[0], shadow=STORM[0] if night else ASH[3],
            body=self.hand.body[night], muted=self.hand.muted[night],
            rule=X["rule_night"] if night else X["rule_day"], accent=FLAME[4] if night else X["accent_day"],
            tag=FLAME[2] if night else METAL[3], tag_ink=STORM[0] if night else ASH[6],
            fill=STORM[3] if night else ASH[6], dim=X["dim_night"] if night else X["dim_day"],
        )

    def paper(self, p, night, uid="p"):
        p.sheet = uid
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        return A.bg_at(p, night, y)

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The sky; and on a wide header, whose layout keeps the title's box and the words under it clear (`avoid`),
        the storm across its top, behind the title, its clouds drifting and lightning crawling through them, ending
        above the words (see `art.storm`): on an H1 a bolt strikes down among the far towers."""
        self.paper(p, night)
        if not (p.w == WIDE and len(avoid) > 1):
            return
        (a0, a1), mark = avoid[:2], self.mark_box(p)
        title = (a0[0] + 2, a0[1] + 9, a0[2] - 2, a0[3] - 1)
        h1 = a1[0] == 40
        if a1[1] - 1 - A.TOP < 24:
            return
        A.storm(p, night, motion, (A.EDGE, A.TOP, p.w - A.EDGE, a1[1] - 1), title, mark,
                strike=a1[1] - A.TOP - 14 if h1 else 0)

    def top_centre(self, p) -> tuple:
        """The columns of a header's top kept for the month's mark, its box and two units either side."""
        x0, _, x1, _ = self.mark_box(p)
        return x0, x1

    def frame(self, p, night, webs=False):
        A.frame(p, night, header=webs)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """The cables hung in swags across a header's top, parting for the month's mark when the header carries it
        (see `art.swags`)."""
        A.swags(p, A.EDGE + 2, p.w - A.EDGE - 3, night, clear=self.top_centre(p) if self.marked else None)

    def tag(self, p, x, y, w, h, night):
        """A block of dark metal by day, of phosphor by night, a note's number knocked out of it."""
        p.rect(x, y, w, h, FLAME[2] if night else METAL[3])
        p.hline(x, x + w, y, FLAME[3] if night else METAL[5])

    def title_text(self, p, x, y, s, night, scale):
        """Glass tubes of phosphor fluid (see `art.tube_title`). The drawing keeps each line, for the beam that
        passes down it in a moving header."""
        w = A.tube_title(p, x, y, s, night, scale, getattr(p, "moving", True))
        p.titles = getattr(p, "titles", []) + [(x, y, s, scale, w)]
        return w

    # ---- the headers' scenes
    @staticmethod
    def _reach(p, x0, y0, y1, limit):
        """How far right from x0 a band from row y0 to y1 runs clear of words, two units kept; at most `limit`."""
        x = x0
        while x < limit and p.clear_of_words(x - 2, y0 - 2, x + 3, y1 + 3):
            x += 1
        return x

    @staticmethod
    def _top(p, x0, x1, g, most):
        """The highest row from which the columns x0 to x1 stand clear of words down to the ground at row g, two
        units kept; no higher than `most`."""
        y = most
        while y < g and not p.clear_of_words(x0 - 2, y - 2, x1 + 2, g + 2):
            y += 1
        return y

    def _fields(self, p, g, night, run=24):
        """The fields to the horizon along the foot, wherever the words leave them room along `run` columns or more,
        the glow of their pods along the horizon over them."""
        x0 = 4
        while x0 < 411:
            if p.clear_of_words(x0 - 2, g - 9, x0 + 3, g + 1):
                x1 = x0
                while x1 < 411 and p.clear_of_words(x1 - 2, g - 9, x1 + 3, g + 1):
                    x1 += 1
                if x1 - x0 >= run:
                    A.fields(p, x0, x1, g, night, uid=f"fld{x0}")
                    A.horizon(p, x0, x1, g - 7, g - 1, night)
                x0 = x1
            x0 += 1

    def scene(self, design, p, rule, night, motion):
        """On H1 the near tower of pods at the left with the far towers beyond it, the harvester plucking a pod from a
        tower at the right (or where a long title leaves it no room, the tower alone, risen as high as the words let
        it), and the fields along the foot wherever the words leave room, the glow of their pods along the horizon; on
        H2 the awakening at the right, risen the full height of its sky (see `art.awakening`), and on H3 the pod tree
        at the right, rising the strip's full height (see `art.pod_tree`), each with the fields along the foot
        wherever the words leave them room; and in a moving header the beam passing down each line of the title on
        the hand's period."""
        titles = getattr(p, "titles", ())
        if motion:
            for n, (x, y, s, scale, w) in enumerate(titles):
                rain.scan(p, x, y, s, scale, w, n, self.hand.glint, C["white"])
        g = rule - 1
        spans = []
        if design == "H2":
            x0 = next((x for x in range(300, 346) if p.clear_of_words(x - 2, A.TOP, 412, g + 2)), None)
            if x0 is not None:
                self._fields(p, g, night)
                spans.append(A.awakening(p, x0, p.w - A.EDGE - 1, g, night, motion))
            return spans
        if design == "H3":
            x0 = next((x for x in range(340, 362) if p.clear_of_words(x - 2, A.TOP, 412, g + 2)), None)
            if x0 is not None:
                self._fields(p, g, night)
                spans.append(A.pod_tree(p, x0, p.w - A.EDGE - 1, g, night, motion, A.TOP + 2))
            return spans
        if design != "H1":
            return spans
        top = A.TOP + 2
        hy = g - 7
        whole = p.clear_of_words(2, hy - 2, 413, g + 2)       # the glow along the horizon, as high as the words let it
        while whole and hy > g - 17 and p.clear_of_words(2, hy - 3, 413, g + 2):
            hy -= 1
        if whole:
            A.horizon(p, 4, 411, hy, g - 1, night)
        x0 = 4
        while x0 < 411:
            if p.clear_of_words(x0 - 2, g - 9, x0 + 3, g + 1):
                x1 = x0
                while x1 < 411 and p.clear_of_words(x1 - 2, g - 9, x1 + 3, g + 1):
                    x1 += 1
                A.fields(p, x0, x1, g, night, uid=f"fld{x0}")
                if not whole:
                    A.horizon(p, x0, x1, g - 7, g - 1, night)
                x0 = x1
            x0 += 1
        if p.clear_of_words(4, g - 40, 58, g + 2):
            ktop = self._top(p, 6, 54, g, top)
            levels = max(2, min(4, (g - ktop - 6) // 17))
            ttop = g - 17 * levels - 4
            A.crown_cables(p, 30, ttop, night, 6, 54)
            A.tower(p, 30, ttop, g, night, motion, levels)
            reach = self._reach(p, 58, top, 56, 122)
            if reach >= 90:
                A.far_towers(p, 60, reach - 2, top + 1, min(56, g - 2), night)
            spans.append((4, 58))
        if p.clear_of_words(356, g - 40, 411, g + 2):
            # The harvester where the words leave it room at the top; where they leave none (a long title), the tower
            # alone, risen as high as they let its own column rise, its cables running on up into the dark.
            hx = 296
            while hx < 330 and not p.clear_of_words(hx - 2, top, 392, 57):
                hx += 1
            plucking = hx < 330
            rtop = self._top(p, 358 if plucking else 388, 410, g, top)
            levels = max(2, min(4, (g - rtop - 6) // 17))
            rt = g - 17 * levels - 4
            step = (g - rt - 17) // max(1, levels - 1)
            A.tower(p, 405, rt, g, night, motion, levels, skip={(1, 0)} if plucking else (), sides=(0,))
            if plucking or rt - top >= 12:
                A.crown_cables(p, 405, rt, night, 380, 409)
            if plucking:
                A.harvester(p, hx + 6, top + 4, night, motion, (405, rt, g), (390, rt + 2 + step), floor=55)
            spans.append((356, 411))
        return spans

    def _finish(self, p, night):
        """The last pass, which a drawing made lighter keeps too: the file written as lightly as it can be, the same
        drawing unit for unit (see `Pix.compact`), the month's mark left as the hand draws it."""
        if not p.lite:
            self.finish(p, night)
        p.compact(keep=("mark",))

    def section_mark(self, p, x, y, night):
        """A pod lying on its side after SECTION A-A, glowing, a row under the title."""
        A.mini_pod(p, x, y + 1, night)

    def strip_mark(self, p, x, y, night):
        """A pod standing beside a strip's title, level with its tubes."""
        A.mini_pod(p, x, y - 4, night, upright=True)

    @staticmethod
    def _room(p, x0, x1, g, most, least):
        """The rows free of words over the ground at row g between x0 and x1, `most` at the most, keeping three rows
        of margin above and two beside; None when fewer than `least` are free."""
        for room in range(most, least - 1, -1):
            if p.clear_of_words(x0 - 2, g - room - 3, x1 + 2, g + 3):
                return room
        return None

    # ---- the phones
    def h1_narrow(self, h, night):
        """A phone's H1, the fields given `art.PHONE_SCENE` rows under the words, the notes set under the words however
        many there are."""
        self.phone_scene_rows = A.PHONE_SCENE + 4 + 10 * len(self.said(h))
        try:
            return super().h1_narrow(h, night)
        finally:
            del self.phone_scene_rows

    def scene_narrow(self, design, p, y, night):
        """A phone's H1 scene, built to the rows its words leave free over it: the fields across the phone under the
        words, a tower of pods and the harvester at its work (`art.phone_fields`). A phone's H2 and H3 stand their
        heroes under their words instead (see `scene_under`)."""
        if design == "H1":
            g = y - 1
            room = self._room(p, 5, p.w - 5, g, A.PHONE_SCENE - 2, A.PHONE_LEAST)
            if room:
                A.phone_fields(p, g, night, room)

    def phone_rows(self, design, title_w):
        """The rows a phone's H2 or H3 leaves under its words for its hero, whatever the words say: the awakening and
        the pod tree (see `scene_under`)."""
        return A.UNDER[design]

    def scene_under(self, design, p, y0, y1, night):
        """A phone's hero under its words, across the phone, standing on the rule at y1 and built to the rows free
        over it: on H2 the awakening (`art.phone_awakening`), on H3 the pod tree (`art.phone_tree`)."""
        g = y1 - 1
        room = self._room(p, 5, p.w - 5, g, A.UNDER[design] - 3, 44)
        if room:
            (A.phone_awakening if design == "H2" else A.phone_tree)(p, g, night, room)

    def rule_decor(self, p, x0, x1, y, seed, night):
        """Short lengths of cable laid along a rule where no scene stands on it, clamped in dark metal, a pulse of
        phosphor in each, kept two rows clear of every word."""
        A.rule_cable(p, x0, x1, y, seed, night)

    # ---- the footers and links
    def footer_mark(self, p, x, y, night):
        """The machines watching from the corner of the closing notes: a disc of dark metal and its red eyes."""
        A.sentinel_eye(p, x + 4, y - 3, night)

    def _footed(self, p, night, last=False):
        """A footer once its cells are laid: the trench's cables along its foot, a second course of conduit laid on
        them where the cells leave it room, and a pod plugged into its socket where they leave it free (see
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
        """A pod's glass in the shape of a heart, full of glowing fluid."""
        A.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        """A tube of the pods' fluid banded in dark metal."""
        A.tube_bar(p, x0, y0, w, h, period)

    def link_colours(self, night):
        """A plate of dark metal, its letters lit in phosphor; by night its rim lit green by the fields."""
        if night:
            return METAL[2], FLAME[1], FLAME[4], METAL[0]
        return METAL[3], METAL[0], FLAME[4], METAL[1]

    def link_top(self, p, x0, x1, y, seed, night):
        """The button finished as a plate on the conduit: a run of ribbed conduit along its top edge, clamped at either
        end, and its face lit along its top and down its left and shaded down its right."""
        fill, edge, _, shade = self.link_colours(night)
        A.conduit_top(p, x0, x1, y, night)
        lit = METAL[5] if not night else METAL[4]
        p.hline(1, p.w - 1, y + 1, lit)
        p.vline(1, y + 1, y + 9, lit)
        p.vline(p.w - 2, y + 2, y + 9, shade)

    def link_icon(self, index, night, ink):
        """A pod with its sleeper, the harvester's red eyes, a cable's plug and a bolt of lightning, by turns."""
        names = ("pod", "eyes", "plug", "bolt")
        return A.ICONS[names[index % len(names)]], A.icon_pal(night, ink)

    # ---- the elements
    def card_bevel(self, night):
        return (STORM[5], STORM[1]) if night else (C["white"], ASH[4])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A card as a pod's control panel: ribbed conduit down its icon cell's edge, rivets, a lamp of phosphor, and
        a cable plugged into its lid."""
        A.panel_node(p, x, y, w, h, night, seed, lid)

    def wire_ink(self, night):
        return RAMP["conduit"][5] if night else RAMP["conduit"][3]

    def wire_lights(self, p, cells, night, seed):
        """The wire as a cable carrying the code, pulses of phosphor along it and clamps where it turns."""
        A.data_cable(p, cells, night, seed)

    def dashes(self, night):
        return [FLAME[3], METAL[5]] if night else [FLAME[1], METAL[3]]

    def ornament(self, kind, p, x, y, night):
        """A pod with its sleeper, standing in a free corner of the schematic."""
        if kind == "schematic":
            if p is not None:
                A.pod(p, x, y, night, look=1)
            return (12, 17)
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as a glass tube of the pods' fluid, filled as high as the week ran."""
        A.fluid_tube(p, bx, base, bw, v, night)

    def peak_mark(self, p, x, y, night):
        A.bolt(p, x, y - 1, night)

    def dial_ring(self, p, arc, night):
        """A bend of ribbed conduit over the dial."""
        A.conduit_ring(p, arc, night)

    def dial_tick(self, p, x, y, night):
        p.px(x, y, METAL[6] if not night else METAL[5])
        p.px(x + 1, y + 1, METAL[0])

    def dial_hub(self, p, cx, cy, night):
        """The machine's red eye, watching the days go by."""
        A.eye_hub(p, cx, cy, night)

    def material(self, i, xx, yy, y0, y1, lift, night):
        """The fields' stuffs by turns: the phosphor fluid, ribbed conduit, riveted metal, copper coil and glass."""
        return A.machine_wrapper(i, xx, yy, y0, y1, lift, night)

    def counter_cell(self, q, ox, oy, night):
        A.screen_cell(q, ox, oy, night)

    def counter_ink(self, night, dim):
        """A numeral lit in phosphor on its screen; a leading nought dimly lit, a tone brighter on the day's glass than
        on the night's metal so it shows as faintly on either: inks the drawing's other words never take, since a
        drawing sets all the letters of one ink together where that ink is first used."""
        if dim:
            return FLAME[1] if night else FLAME[2]
        return FLAME[5]

    def timeline_line(self, p, x0, x1, y, night):
        """The time line as a heavy cable carrying the code, up to today."""
        if x1 - x0 >= 2:
            A.cable_line(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        """A pod on the cable for a release, a stub of a tower for a big one, a bead of phosphor for a patch, an empty
        pod for one still to come, and the foot of the first tower for the repository's beginning."""
        A.release_pod(p, x, gy, kind, night, i)

    def today_mark(self, p, x, y, night):
        """A bolt of the storm's lightning striking today's end of the cable."""
        A.bolt(p, x - 2, y - 8, night)

    def avatar(self, p, cx, cy, i, person, night):
        A.pod_avatar(p, cx, cy, i, person, night)

    def commit_bar(self, p, x, y, w, fill, night):
        """A contributor's share as a tube filling with the fluid as far as their commits go."""
        A.filled_share(p, x, y, w, fill, night)

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """A ring of ribbed conduit round the seal, clamped in dark metal."""
        A.cable_wreath(p, cx, cy, r0, r1, n, night)

    def seal_mark(self, p, x, y, night):
        A.mini_pod(p, x + 1, y + 1, night)

    def placard_board(self, p, night):
        A.metal_board(p, night)

    def placard_mark(self, p, x, y, night):
        A.sentinel_eye(p, x + 3, y - 4, night)

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        """A run of ribbed conduit along a badge's top two rows, kept inside its shape, a pulse of phosphor in it now
        and then, the letters under it; and under it each block lit along its top and shaded along its foot."""
        from ...holidays.designs.badges import inside
        K = RAMP["conduit"]
        h = s["h"]
        ty = self._text_y(s)
        text_rows = range(ty - 1, ty + (7 if s["font"] == "57" else 5) + 1)
        for y in range(h):
            for x in range(w):
                if not inside(x, y, w, h, s["corner"]):
                    continue
                if y <= 1:
                    rib = (x + seed) % 3 == 0
                    pulse = (x + seed) % 13 == 6
                    if y == 0:
                        p.px(x, y, FLAME[4] if pulse else K[3] if rib else K[5])
                    else:
                        p.px(x, y, FLAME[2] if pulse else K[1] if rib else K[2])
                    continue
                c = p.get(x, y)
                try:
                    if y == 2 and y not in text_rows:
                        p.px(x, y, step(c, 1))
                    elif y == h - 1:
                        p.px(x, y, step(c, -1))
                except KeyError:
                    pass

    def badge_label(self):
        """A label of the machines' darkest metal, its letters pale glass."""
        return (METAL[1], GLASS[6])

    def badge_gold(self):
        """A live badge's label in the pods' pale glass."""
        return (GLASS[5], METAL[0])

    def badge_states(self):
        return {"green": (FLAME[1], C["white"]), "yellow": (COPPER[6], METAL[0]), "red": (RAMP["eye"][3], C["white"]),
                "slate": (METAL[5], C["white"])}

    def badge_swatches(self):
        """The fields' colours a written colour finds its nearest among: the phosphor, the pods' glass, the
        machine's red eyes and their glow, the cables' copper bare and bright, the ashen sky, the storm's violet,
        the conduit's black, the towers' metal and the moon."""
        E = RAMP["eye"]
        return {"phosphor": (FLAME[2], METAL[0], None), "glass": (GLASS[2], C["white"], "bubbles"),
                "eye": (E[3], C["white"], None), "ember": (E[5], METAL[0], None),
                "copper": (COPPER[4], C["white"], None), "amber": (COPPER[6], METAL[0], None),
                "ash": (ASH[3], METAL[0], None), "storm": (STORM[5], C["white"], None),
                "conduit": (RAMP["conduit"][2], GLASS[6], "ribs"), "metal": (METAL[4], C["white"], None),
                "moon": (RAMP["moon"][3], METAL[0], "rim")}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        """The glass with a bubble rising in it now and then, and the conduit ribbed, both off the letters' rows."""
        if y in text_rows:
            return c
        if pattern == "bubbles" and (x * 7 + y * 5) % 19 == 0:
            return GLASS[4]
        if pattern == "ribs" and x % 3 == 0:
            return RAMP["conduit"][3]
        return c

    def badge_outline(self, pattern):
        """The moon's pale face has a rim of dark metal."""
        return METAL[4] if pattern == "rim" else None

    def badge_shine(self, c, y, h):
        try:
            return step(c, 1) if y == 2 else step(c, -1) if y == h - 1 else c
        except KeyError:
            return c

    def plate_colours(self, mode):
        """A plate is a panel of the towers' dark metal, riveted in rows, the value lit in phosphor; by night its
        rim glows; a live plate is the pods' pale glass."""
        if mode == "day":
            return dict(paper=METAL[2], dot=METAL[4], frame=RAMP["conduit"][0], block=FLAME[2], ink=GLASS[6],
                        letters=METAL[0])
        if mode == "night":
            return dict(paper=METAL[1], dot=METAL[3], frame=FLAME[1], block=FLAME[3], ink=C["body_night"],
                        letters=METAL[0])
        return dict(paper=GLASS[5], dot=GLASS[4], frame=METAL[0], edge=GLASS[3], ink=METAL[0])

    def plate_edge(self, block):
        return step(block, -1)

    # ---- the games
    def game_squares(self, night):
        """A board of the pods' glass in its leads and the towers' dark metal, riveted, each a tone down by night."""
        return (Stuff(GLASS, 4 if night else 5, "glass", fleck=METAL[2]), Stuff(METAL, 5 if night else 6, "metal"))

    def game_frame(self, night):
        """A frame of the black conduit's rubber, riveted."""
        return Stuff(RAMP["conduit"], 4), "iron"

    def game_podium(self, night):
        """A podium of the towers' dark metal, cobwebbed in its corners, as is fitting for Halloween."""
        return Podium(Stuff(METAL, 4, "metal"), "cobwebs", Stuff(GLASS, 5))


SET = Harvest()
