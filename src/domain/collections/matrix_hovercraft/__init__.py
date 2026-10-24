# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Hovercraft set: the ship in the tunnels of the real, September's design in the Matrix collection, drawn in
the collection's hand.

Every sheet is the wall of a sewer tunnel in the real world, board-marked concrete, pale and rust-grey by day under
the ship's floodlights, its formwork joints and tie holes weeping rust, and by night the tunnel's black. Riveted
steel plate runs down its sides and along its foot, and across a header's top run the tunnel's pipes, a gunmetal
main and a rusted copper line under it, flanged and strapped, limescale grown down from them in straws and work
lamps hung under them in their cages, each pipe ending in a blind flange either side of the top centre when the
header carries the month's mark, and steam leaking from a joint at the left rolls along under them. Titles are
stencilled in military paint, the stencil's bridges cutting each letter from its stem, oversprayed at its edges and
worn through here and there; an H1's title is painted on a scuffed steel plate riveted to the wall, casting its
shadow on it, and by night two caged work lamps at its corners light it, and the paint, green; in a moving header
the beam passes down the letters on the hand's period. Across an H1's sky the ship's searchlight sweeps behind the
title, up toward the pipes and back toward the far wall, slowly, never as low as the words under the title, dust
glinting in it by night. Headers open on the tunnel. On an H1, at the left the ship, an armoured hovercraft,
battered and patched, hovering low over the channel of black water on pads that glow phosphor, their light
shimmering in the water and the water thrown up in spray under them, mist lying on it, the bridge's windows lit by
night and the searchlight high on its mast; at the right a machine coming out of a great drain in a brick headwall,
a carapace of iron plates and a face of a dozen red eyes, its tentacles spread wide across the wall, back into the
drain and down to the water, the red of its eyes on the brick and in the channel, while water drips from the
drain's lip. On an H2 the ship's main deck stands at the right, cut away along its near side and risen the full
height: the operator on his chair at a rack of old monitors running the code in phosphor, his headset on, and a
crew member lying back on the chair beside him with her eyes shut, jacked in, the cable rising from the back of her
head to a junction box on the deckhead, a lamp on the chair's arm blinking while she is under; by night the screens
light the operator's back and the work lamps pool on the deck. On an H3 a machine hangs from the pipes at the
right over the water, the strip's full height, three tentacles coiled round the copper line and the rest trailing
to the water, its red gaze swinging slowly over the channel. A phone's H1 holds the whole tunnel under its words,
the ship's searchlight held on the machine coming out of the drain, and its H2 and H3 stand the deck and the
hanging machine under theirs, whatever they say. The footers stand on the channel's black water, the ship in
little hovering after a title block's last cell with its searchlight on a drain where the machine's eyes burn, its
lights flickering by night, and a valve wheel marks the closing notes; a link button is a steel plate riveted along
its top; a badge carries the tunnel's pipe along its top; the elements are built of the ship's steel plate, its
cables, valves, gauges, readouts and dog tags; and the games stand on boards of deck plate and drab paint, their
winners on blocks of the ship's steel with shields along their rail.
"""
from __future__ import annotations

from ...holidays.designs import WIDE
from ...holidays.designs.badges import inside
from ...holidays.designs.materials import Podium, Stuff
from ..hand import CollectionSet
from .. import rain
from . import art as A
from . import parts as P
from .palette import C, RAMP, TOKENS, X, step

FLAME, STEEL, DRAB, PLATE, EYE = RAMP["flame"], RAMP["steel"], RAMP["drab"], RAMP["plate"], RAMP["eye"]
RUST, BRICK, WATER, IRON, CONCRETE = RAMP["rust"], RAMP["brick"], RAMP["water"], RAMP["iron"], RAMP["concrete"]


class Hovercraft(CollectionSet):
    key = "matrix-hovercraft"
    name = "Hovercraft"
    collection = "matrix"
    tagline = "The ship in the tunnels of the real, its searchlight sweeping the dark as the machines come."
    about = (
        "Every sheet is the wall of a sewer tunnel in the real world, board-marked concrete pale and rust-grey by day "
        "under the ship's floodlights and black by night, framed in riveted steel plate with the tunnel's pipes "
        "running across the top, limescale hanging from them and steam leaking from a joint. Titles are stencilled in "
        "military paint, the stencil's bridges cutting each letter, an H1's on a scuffed steel plate lit green by "
        "night by two work lamps, and behind it the beam of the ship's searchlight sweeps the tunnel's sky, dust "
        "glinting in it. Headers open on the tunnel: an armoured hovercraft, battered and patched, hovering low over "
        "the black water on pads that glow phosphor, and a machine coming out of a great drain in a brick headwall, a "
        "carapace of iron with a face of a dozen red eyes, its tentacles spread wide across the wall; the ship's main "
        "deck cut away, the operator at his monitors running the code and a crew member jacked in on her chair, the "
        "cable rising from her head; and a machine hanging from the pipes over the water, its red gaze swinging over "
        "it. The footers stand on the water with the ship in little after their last cell, links are riveted plates, "
        "badges carry the pipe, and the elements and the games are built of the ship's steel, cables, valves and "
        "gauges.")
    tokens = frozenset(TOKENS)

    # ---- colour and paper
    def ink(self, night):
        """The words in the hand's two inks; the titles in the stencil's paint, the rules in steel, and labels in rust
        by day and phosphor by night."""
        return dict(
            title=FLAME[3] if night else DRAB[1], shadow=C["plate_night"] if night else PLATE[3],
            body=self.hand.body[night], muted=self.hand.muted[night],
            rule=X["rule_night"] if night else X["rule_day"], accent=FLAME[4] if night else X["accent_day"],
            tag=FLAME[2] if night else STEEL[3], tag_ink=STEEL[0] if night else PLATE[6],
            fill=STEEL[1] if night else PLATE[5], dim=X["dim_night"] if night else X["dim_day"],
        )

    def paper(self, p, night, uid="p"):
        p.sheet = uid
        A.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        return A.bg_at(p, night, y)

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The concrete; and on a wide H1, whose layout keeps the title's box and the words under it clear (`avoid`),
        the steel plate riveted behind the title and the searchlight's beam sweeping the tunnel's sky behind it, from
        the lens of the ship hovering at the left and ending above the words (see `art.beam`)."""
        self.paper(p, night)
        if not (p.w == WIDE and len(avoid) > 1 and avoid[1][0] == 40):
            return
        (a0, a1), mark = avoid[:2], self.mark_box(p)
        words = a1[1] + 2                                     # the top of the words under the title
        tx, right, top, foot = a0[0] + 4, a0[2] - 6, a0[1] + 10, a0[3] - 4
        if foot - top >= 7 and right > tx:
            A.title_plate(p, (tx - 6, max(top - 4, mark[3] + 1), right + 6, min(foot + 2, words - 4)), night, motion)
        A.beam(p, A.ship_place(y1 + 1)[2], night, motion, mark, words - 2)

    def top_centre(self, p) -> tuple:
        """The columns of a header's top kept for the month's mark, its box and two units either side."""
        x0, _, x1, _ = self.mark_box(p)
        return x0, x1

    def frame(self, p, night, webs=False):
        """The riveted steel, and across a header's top the pipes, ending either side of the month's mark when the
        header carries it."""
        A.frame(p, night, header=webs, clear=self.top_centre(p) if (webs and self.marked) else None)

    def _finish(self, p, night):
        """The last pass, which a drawing made lighter keeps too: the kit's last light at full weight only (see
        `finish`), then the file written as lightly as it can be, the same drawing unit for unit, the month's mark
        left as it is drawn (see `Pix.compact`)."""
        if not p.lite:
            self.finish(p, night)
        p.compact(keep=("mark",))

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        """No stars: a tunnel has a vault, not a sky. In their place drops of water on the concrete catch what light
        there is, a third as many as the stars asked for, faintly (see `art.glints`)."""
        A.glints(p, x0, y0, x1, y1, max(3, n // 3), seed, twinkling, avoid)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        """Limescale grown down from the pipes in straws, a drop at each tip, and work lamps hung in their cages,
        burning by night, none in the columns kept for the month's mark when the header carries it, and no lamp over
        the title's plate (see `art.straws`)."""
        plate = getattr(p, "plate", None)
        A.straws(p, x0, x1, night, True, clear=self.top_centre(p) if self.marked else None,
                 keep=(plate,) if plate else ())

    def section_mark(self, p, x, y, night):
        """The machine's head in little after SECTION A-A, its red eyes to the left (see `art.sentinel_mark`)."""
        A.sentinel_mark(p, x, y - 1, night)

    def strip_mark(self, p, x, y, night):
        """The ship in little beside a strip's title, its pads glowing (see `art.ICONS`)."""
        p.sprite(x, y - 1, A.ICONS["ship"], A.icon_pal(night))

    def rule_decor(self, p, x0, x1, y, seed, night):
        """The tunnel's litter on the rule where no scene stands: a spanner, a coil of cable, a rusted nut and a
        puddle (see `art.debris`)."""
        A.debris(p, x0, x1, y, seed, night)

    def tag(self, p, x, y, w, h, night):
        """A block of steel by day, of phosphor by night, a note's number knocked out of it."""
        p.rect(x, y, w, h, FLAME[2] if night else STEEL[3])
        p.hline(x, x + w, y, FLAME[3] if night else STEEL[5])

    def title_text(self, p, x, y, s, night, scale):
        """Stencilled in military paint (see `art.stencil_title`). The drawing keeps each line, for its plate and for
        the beam that passes down it in a moving header."""
        w = A.stencil_title(p, x, y, s, night, scale)
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

    def scene(self, design, p, rule, night, motion):
        """On H1 the channel of water along the foot wherever the words leave it, mist on it, the ship hovering over
        it at the left with steam leaking from the pipes above, and the drain with its machine at the right; and in
        a moving header the beam passing down each line of the title on the hand's period."""
        titles = getattr(p, "titles", ())
        if motion:
            for n, (x, y, s, scale, w) in enumerate(titles):
                rain.scan(p, x, y, s, scale, w, n, self.hand.glint, C["white"])
        g = rule - 1
        spans = []
        if design != "H1":                    # the steam leaking from the main, rolling along under the pipes
            A.steam(p, 15, 9, night, motion, reach=min(170, self.mark_box(p)[0] - 6))
        if design == "H2":
            x0 = 306
            while x0 < 330 and not p.clear_of_words(x0 - 2, g - 50, 413, g + 2):
                x0 += 1
            if x0 < 330:
                spans.append(A.deck(p, x0, 410, g, night, motion, self._top(p, x0, 410, g, A.TOP + 2)))
            return spans
        if design == "H3":
            x0 = 346
            while x0 < 362 and not p.clear_of_words(x0 - 2, A.TOP, 413, g + 2):
                x0 += 1
            if x0 < 362:
                hx, hy = 362, A.TOP + 10
                glints = A.hanging(p, hx, hy, night, motion, 11, g - 6, (x0 - 1, hy, 411, g - 5))
                A.water(p, x0, 411, g, night, motion, glints)
                A.mist(p, [(x0 + 2, 410)], g, night, motion)
                A.drips(p, 352 if x0 < 350 else x0 + 3, A.TOP, g - 7, night, motion, phase=0.3, dur=3.3)
                spans.append((x0, 411))
            return spans
        if design != "H1":
            return spans
        top = A.TOP + 2
        glints, mists = [], []
        x0, y0, _ = A.ship_place(g)
        if p.clear_of_words(4, y0 - 24, 56, g + 2):
            ship = A.ship(p, x0, y0, night, motion)
            A.wash(p, ship["pads"], g, night, motion)
            glints += [(x, 11, FLAME[4] if night else FLAME[2]) for x in ship["pads"]]
            A.steam(p, 15, 9, night, motion, reach=min(110, (getattr(p, "plate", (120,))[0]) - 8))
            A.drips(p, 6, top - 2, g - 7, night, motion, phase=0.2, dur=3.1)
            mists.append((5, 56))
            spans.append((4, 58))
        if p.clear_of_words(356, g - 40, 411, g + 2):
            rtop = self._top(p, 358, 410, g, top)
            if rtop <= g - 46:
                wall_top = max(rtop + 2, top + 2)
                A.headwall(p, 366, 411, wall_top, g - 6, night)
                r = 14
                cx, cy = 392, wall_top + r + 2
                lip = A.outlet(p, cx, cy, r, night)
                hx, hy = 352, cy - 3
                plate = getattr(p, "plate", (0, 0, 0, 0))
                if p.clear_of_words(hx - 2, hy - 2, 396, hy + 24):
                    A.sentinel(p, hx, hy, night, motion, (cx, cy, r), g - 7, max(plate[2] + 6, 300))
                    if night:
                        glints.append((hx + 10, 10, EYE[3]))
                A.drips(p, cx + 7, lip + 1, g - 7, night, motion)
                A.drips(p, cx - 3, lip + 1, g - 7, night, motion, phase=0.45, dur=3.4)
                spans.append((356, 411))
            elif rtop <= g - 28:
                wall_top = rtop + 2
                A.headwall(p, 366, 411, wall_top, g - 6, night)
                r = min(9, (g - 6 - wall_top - 9) // 2)
                cx, cy = 390, wall_top + r + 5
                lip = A.outlet(p, cx, cy, r, night)
                A.lurker(p, (cx, cy, r), night, motion, g - 7)
                A.drips(p, cx + 5, lip + 1, g - 7, night, motion)
                spans.append((356, 411))
            mists.append((360, 410))
        x = 4
        while x < 411:
            if p.clear_of_words(x - 2, g - 9, x + 3, g + 1):
                x1 = x
                while x1 < 411 and p.clear_of_words(x1 - 2, g - 9, x1 + 3, g + 1):
                    x1 += 1
                A.water(p, x, x1, g, night, motion, [gl for gl in glints if x <= gl[0] < x1])
                x = x1
            x += 1
        A.mist(p, mists, g, night, motion)
        return spans

    # ---- a phone's scenes
    UNDER = {"H2": 64, "H3": 62}    # the rows a phone's H2 and H3 ask for under their words, whatever they say
    _notes = 0                      # the notes of the phone H1 being drawn

    @property
    def phone_scene_rows(self):
        """The rows a phone's H1 leaves under its words for the tunnel: PHONE_WORLD, and ten more for each note,
        which are set under the words before it."""
        return A.PHONE_WORLD + 4 + 10 * self._notes

    def h1_narrow(self, h, night):
        """A phone's H1, the rows for its tunnel counting its notes (see `phone_scene_rows`)."""
        self._notes = len(self.said(h))
        try:
            return super().h1_narrow(h, night)
        finally:
            self._notes = 0

    def phone_rows(self, design, title_w):
        """The rows a phone's H2 or H3 leaves under its words for its hero, whatever the words say: beside the words
        a hero has no room to stand at its height, so it always stands under them (see `scene_under`)."""
        return self.UNDER[design]

    def scene_narrow(self, design, p, y, night):
        """A phone's H1 scene, standing on the rule at `y` in the rows its words leave over it: the whole tunnel
        across the phone, the ship hovering over the water at the left with its searchlight held on the drain at the
        right, where the machine comes out (see `art.phone_world`). A phone's H2 and H3 stand their heroes under
        their words instead (see `scene_under`)."""
        if design != "H1":
            return
        g = y - 1
        top = self._top(p, 5, 175, g, g - A.PHONE_WORLD)
        if top <= g - 44:
            A.phone_world(p, g, night, top)

    def scene_under(self, design, p, y0, y1, night):
        """A phone's hero under its words, from its last words at row y0 to its rule at y1, across the phone: on H2
        the main deck cut away, the operator at his monitors and the crew member jacked in on her chair (see
        `deck.deck`); on H3 the machine hanging from a pipe over the water, its red gaze on it (see
        `art.phone_hunter`)."""
        g = y1 - 1
        top = max(y0 + 3, self._top(p, 6, 174, g, y0 + 3))
        if design == "H2":
            A.deck(p, 26, 154, g, night, False, top)
        else:
            A.phone_hunter(p, A.EDGE, 176, g, night, top)

    # ---- the footers and links
    def _footed(self, p, night, last=False):
        """A footer as the tunnel's: its channel of black water along its foot, under every cell where the words
        leave it room, and on a title block, after its `last` cell, the ship in little hovering over it with its
        searchlight on the drain where the machine's eyes burn (see `art.footing` and `art.emblem`)."""
        g = A.footing(p, night) - 1
        if last:
            after = max((b[2] for b in p.words), default=0) + 4
            A.emblem(p, after, p.w - A.EDGE, g, night)
        return p

    def f1(self, ft, night):
        return self._footed(super().f1(ft, night), night, last=True)

    def f2(self, ft, night):
        return self._footed(super().f2(ft, night), night)

    def f1_narrow(self, ft, night):
        return self._footed(super().f1_narrow(ft, night), night, last=True)

    def f2_narrow(self, ft, night):
        return self._footed(super().f2_narrow(ft, night), night)

    def footer_mark(self, p, x, y, night):
        """A valve wheel of rusted iron in the corner of the closing notes (see `art.valve_mark`)."""
        A.valve_mark(p, x + 2, y - 3, night)

    def link_top(self, p, x0, x1, y, seed, night):
        """The plate's rivets along its top edge, rust weeping from one or two (see `art.rivets`)."""
        A.rivets(p, x0, x1, y, seed, night)

    def heart(self, p, x, y):
        """A heart cut from steel plate and painted the machines' red (see `art.heart`)."""
        A.heart(p, x, y)

    def bar(self, p, x0, y0, w, h, period=5):
        """Riveted steel plates, pale and dark by turns (see `art.plate_bar`)."""
        A.plate_bar(p, x0, y0, w, h, period)

    def link_colours(self, night):
        """A steel plate riveted in gunmetal, stencilled in military paint by day and in phosphor by night."""
        if night:
            return C["plate_night"], STEEL[3], FLAME[3], STEEL[0]
        return PLATE[4], STEEL[1], DRAB[1], PLATE[2]

    def link_icon(self, index, night, ink):
        """A thing of the tunnel for each link, by turns: the ship, the machine, a valve wheel and a work lamp."""
        return A.ICONS[A.LINK_ICONS[index % len(A.LINK_ICONS)]], A.icon_pal(night, ink)

    # ---- the elements
    def card_bevel(self, night):
        return (STEEL[4], STEEL[0]) if night else (PLATE[6], PLATE[2])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        """A card as a steel plate: a rivet in each corner, a weld down its icon cell's edge and, on a card with a
        lid, a work lamp clamped to its top (see `parts.card`)."""
        P.card(p, x, y, w, h, night, lid)

    def wire_ink(self, night):
        return STEEL[4] if night else STEEL[0]

    def wire_lights(self, p, cells, night, seed):
        """The wire as the ship's black cable, tied every so often, a signal light on it by night (see
        `parts.cable_ties`)."""
        P.cable_ties(p, cells, night, seed)

    def dashes(self, night):
        return [FLAME[3], STEEL[3]] if night else [RUST[3], STEEL[2]]

    def ornament(self, kind, p, x, y, night):
        """The ship in little hovering over a puddle in a free corner of the schematic."""
        if kind == "schematic":
            if p is not None:
                P.ornament(p, x, y, night)
            return (33, 17)
        return (0, 0)

    def hist_bar(self, p, bx, base, bw, v, night):
        """A week's commits as a stack of steel plates (see `parts.plate_stack`)."""
        P.plate_stack(p, bx, base, bw, v, night)

    def peak_mark(self, p, x, y, night):
        P.warning_lamp(p, x, y + 1, night)

    def dial_ring(self, p, arc, night):
        """The dial as a pressure gauge's bezel, red over its last quarter (see `parts.gauge_ring`)."""
        P.gauge_ring(p, arc, night)

    def dial_tick(self, p, x, y, night):
        p.px(x, y, STEEL[0])
        p.px(x + 1, y + 1, PLATE[6] if not night else STEEL[4])

    def dial_hub(self, p, cx, cy, night):
        """A hex nut of steel (see `parts.nut_hub`)."""
        P.nut_hub(p, cx, cy, night)

    def material(self, i, xx, yy, y0, y1, lift, night):
        """Each file type wrapped in one of the ship's stuffs by turns (see `parts.stuff`)."""
        return P.stuff(i, xx, yy, y0, y1, lift, night)

    def counter_cell(self, q, ox, oy, night):
        """A readout's dark glass in its steel bezel (see `parts.readout`)."""
        P.readout(q, ox, oy, night)

    def counter_ink(self, night, dim):
        """A numeral glowing phosphor on the readout's glass; a leading nought dimmer."""
        return FLAME[2] if dim else FLAME[4]

    def timeline_line(self, p, x0, x1, y, night):
        """A pipe, flanged, the releases hanging from it (see `parts.pipe_line`)."""
        P.pipe_line(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        """A valve wheel, a smaller one, a bolt, a wheel in outline or a capped stub (see `parts.valve`)."""
        P.valve(p, x, gy, kind, night)

    def today_mark(self, p, x, y, night):
        P.lamp_mark(p, x, y, night)

    def avatar(self, p, cx, cy, i, person, night):
        """A contributor's dog tag with their initials stamped in it; a bot, one of the machines (see
        `parts.dog_tag`)."""
        P.dog_tag(p, cx, cy, i, person, night)

    def commit_bar(self, p, x, y, w, fill, night):
        P.gauge_bar(p, x, y, w, fill, night, self.wire_ink(night))

    def rosette(self, p, cx, cy, r0, r1, n, night):
        """A flange of steel bolted round the seal (see `parts.flange`)."""
        P.flange(p, cx, cy, r0, r1, n, night)

    def seal_mark(self, p, x, y, night):
        P.seal_ship(p, x, y, night)

    def placard_board(self, p, night):
        """A plate of the ship's steel riveted to the wall (see `parts.placard`)."""
        P.placard(p, night)

    def placard_mark(self, p, x, y, night):
        A.sentinel_mark(p, x, y, night)

    # ---- the badges
    def badge_label(self):
        """A label of gunmetal, lettered in pale steel."""
        return (STEEL[1], PLATE[5])

    def badge_gold(self):
        """A live label in rust, the tunnel's gold, lettered in gunmetal."""
        return (RUST[5], STEEL[0])

    def badge_states(self):
        return {"green": (DRAB[3], C["white"]), "yellow": (RUST[6], STEEL[0]), "red": (EYE[3], C["white"]),
                "slate": (STEEL[3], C["white"])}

    def badge_swatches(self):
        """The tunnel's colours: the machine's red, rust, brick, a pale rust, the stencil's drab, the water, the
        plate's blue-grey, the machine's iron, gunmetal, concrete and the plate's pale steel."""
        return {"eye": (EYE[3], C["white"], None), "rust": (RUST[3], C["white"], None),
                "brick": (BRICK[3], C["white"], None), "tan": (RUST[6], STEEL[0], None),
                "drab": (DRAB[3], C["white"], None), "water": (WATER[3], C["white"], None),
                "plate": (PLATE[1], C["white"], "rivets"), "iron": (IRON[4], C["white"], None),
                "gunmetal": (STEEL[1], PLATE[6], None), "concrete": (CONCRETE[4], STEEL[0], None),
                "pale": (PLATE[6], STEEL[0], None)}

    def plate_colours(self, mode):
        """A plate is the title's steel plate: pale steel studded with rivets by day, the plate in the dark by night,
        framed in gunmetal, its value painted in drab with pale letters, phosphor by night; a live plate is rust."""
        if mode == "day":
            return dict(paper=PLATE[4], dot=PLATE[2], frame=STEEL[2], block=DRAB[2], ink=STEEL[0], letters=PLATE[6])
        if mode == "night":
            return dict(paper=C["plate_night"], dot=STEEL[2], frame=STEEL[4], block=DRAB[2], ink=C["body_night"],
                        letters=FLAME[4])
        return dict(paper=RUST[5], dot=RUST[6], frame=STEEL[0], edge=RUST[3], ink=STEEL[0])

    def badge_top(self, p, w, s, seed, night):
        """The tunnel's pipe along a badge's top two rows, kept inside its shape and off its letters: gunmetal lit
        along its crown and in shade under it, a flange every sixteen units, rust weeping from one of them where no
        letter sits; and the label's block and the value's each a plate, lit along its left end and in shade along
        its right and its foot, a seam where they meet."""
        h = s["h"]
        ty = self._text_y(s)
        text_rows = range(ty - 1, ty + (7 if s["font"] == "57" else 5) + 1)
        k = -1 if night else 0

        def ins(x, y):
            return 0 <= x < w and 0 <= y < h and inside(x, y, w, h, s["corner"])
        # Where the label's block ends: the first change of colour along two rows under the letters at once (a
        # plate's dots change one row at a time, and its frame is the first pixel of a row alone).
        row = h - 2 if (h - 2) % 4 != 2 else h - 3
        first = next((x for x in range(w) if ins(x, row) and ins(x, row - 1)), 0)
        edge = next((x for x in range(first + 2, w) if ins(x, row) and p.get(x, row) != p.get(x - 1, row)
                     and p.get(x, row - 1) != p.get(x - 1, row - 1)), w)
        weep = 6 + seed % 9
        for y in range(h):
            for x in range(w):
                if not ins(x, y):
                    continue
                flange = (x - 5) % 16 in (0, 1)
                if y == 0:
                    p.px(x, y, STEEL[6 + k] if not flange else STEEL[5 + k])
                    continue
                if y == 1:
                    p.px(x, y, STEEL[3 + k] if not flange else STEEL[1])
                    continue
                c = p.get(x, y)
                try:
                    if y == 2 and y not in text_rows:
                        p.px(x, y, RUST[3] if x in (weep, weep + 16) else step(c, -1))
                    elif y == h - 1:
                        p.px(x, y, step(c, -1))
                    elif not ins(x - 1, y) or x == edge:
                        p.px(x, y, step(c, 1))
                    elif not ins(x + 1, y) or x == edge - 1:
                        p.px(x, y, step(c, -1))
                except KeyError:
                    pass

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        """A plate's rivets, in the rows its letters leave."""
        if pattern == "rivets" and y not in text_rows and x % 8 == 3:
            return PLATE[4]
        return c

    def badge_outline(self, pattern):
        """The plate's dark edge round it."""
        return STEEL[0] if pattern == "rivets" else None

    def badge_shine(self, c, y, h):
        """Plastic painted on steel: lit under the pipe, in shade along its foot."""
        try:
            return step(c, 1) if y == 2 else step(c, -1) if y == h - 1 else c
        except KeyError:
            return c

    def plate_edge(self, block):
        try:
            return step(block, -1)
        except KeyError:
            return block

    # ---- the games
    def game_squares(self, night):
        """A board of the ship's deck plates, pale steel brushed and riveted, and steel painted drab and flecked with
        rust, a tone down by night as every board of the year is."""
        return Stuff(PLATE, 4 if night else 5, "metal"), Stuff(DRAB, 2 if night else 3, "flecks", RUST[3])

    def game_frame(self, night):
        """A frame of the ship's gunmetal, riveted."""
        return Stuff(STEEL, 2), "iron"

    def game_podium(self, night):
        """A podium of the ship's steel, brushed and riveted, with shields of rusted iron along its rail as a
        fighting ship carries them."""
        return Podium(Stuff(STEEL, 3, "metal"), "shields", Stuff(RUST, 4))


SET = Hovercraft()
