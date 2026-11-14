# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""brain, a pixel theme: a living brain kept in a glass jar in a laboratory, wired to the machines it works with,
`theme: brain`.

A page in it is drawn in this set every day of the year (see `pixelthemes`), twice: in GitHub's light mode the lab
is lit and busy, and in its dark mode the lights are out and the brain lights the room.

The brain floats in a jar of aqua fluid held between caps of riveted brass by a strut at each side, a pressure gauge
on its domed cap and two pipes rising from it to the ceiling, on a console of petrol enamel, wires coming down to the
electrodes on its crown and bubbles rising past it. It works: sparks run along its folds and its synapses fire in
waves from the front of the head to the back. It feels: the screen on its console shows its face, focused, happy,
in love, struck by an idea, and cool in shades, and the light it throws on the wall takes each mood's colour; when
the idea strikes every fold lights at once and lightning runs down its wires. The H1 is the lab at work, the
mainframe it works with at the left, its tape reels turning, its terminal writing and its printout folding to the
floor, a heavy cable across to the jar; the H2 is the jar drawn as large as the words leave it room, a Tesla coil
beside it throwing lightning at it; the H3 the jar small, an oscilloscope on the wall beside it sweeping the brain's
waves across its screen. Every header stands on the lab's chequered floor, cables lying along it with signals
running down them.

By day the wall is sage tiles, the lamps' light falling down it and the machines' shadows cast on it, the frame
steel riveted in brass, the titles the brain's crimson in enamel that a glint crosses. By night the lamps are out but
for a flicker, the jar glows, the rivets glow, lightning lights the coil, and the titles burn amber like the figures
in a nixie tube. A placard is a riveted plate; a badge takes the nearest of the lab's colours; the games' boards are
the lab's floor by day and the jar's glass by night, and the Hall's podium is a row of the machines' cabinets.
"""
from __future__ import annotations

from ...holidays.designs import WIDE, Holiday
from ...holidays.designs.badges import inside
from ...holidays.designs.materials import Podium, Stuff
from . import scenes as SC
from . import sheet as S
from . import trim as T
from .palette import C, RAMP, TOKENS, X, step

FLUID, ENAMEL, BRASS, STEEL, NIXIE, ARC, TISSUE, SAGE, ROOM = (RAMP["fluid"], RAMP["enamel"], RAMP["brass"],
                                                              RAMP["steel"], RAMP["nixie"], RAMP["arc"],
                                                              RAMP["tissue"], RAMP["sage"], RAMP["room"])


class Brain(Holiday):
    """brain: the set a page in the pixel theme is drawn in, every day it is not a holiday's or its birthday."""
    key = "brain"
    name = "brain"
    tokens = frozenset(TOKENS)

    # ---- colour and paper
    def ink(self, night):
        return dict(
            title=X["title_night"] if night else X["title_day"],
            shadow=NIXIE[0] if night else TISSUE[1],
            body=C["ink_n"] if night else C["ink"], muted=X["muted_night"] if night else X["muted_day"],
            rule=X["rule_night"] if night else X["rule_day"], accent=X["accent_night"] if night else X["accent_day"],
            tag=NIXIE[4] if night else BRASS[4], tag_ink=X["tag_ink_night"] if night else X["tag_ink_day"],
            fill=C["fill_n"] if night else C["fill"], dim=X["dim_night"] if night else X["dim_day"],
        )

    def paper(self, p, night, uid="p"):
        S.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        return S.bg_at(p, night, y)

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        S.motes(p, x0, y0, x1, y1, n, getattr(p, "night", True), seed=seed, twinkling=twinkling, faint=faint,
                avoid=avoid)

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """The lab's wall: by day dust turning in the lamps' light, by night a spark or two off the coils."""
        self.paper(p, night)
        S.motes(p, 6, 14, p.w - 6, int(y1 * 0.85), p.w // (40 if p.lite else 20), night, seed=seed, twinkling=motion,
                avoid=avoid)

    def frame(self, p, night, webs=False):
        S.frame(p, night, header=webs)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        S.festoon(p, x0 + 12, x1 - 12, y, night, seed=seed, sag=sag, span=span)

    def tag(self, p, x, y, w, h, night):
        """By day a plate of brass, by night a block of nixie amber: lit along its top, shaded at its foot."""
        base = NIXIE[4] if night else BRASS[4]
        p.rect(x, y, w, h, base)
        p.hline(x, x + w, y, step(base, 1))
        p.hline(x, x + w, y + h - 1, step(base, -1))

    def title_text(self, p, x, y, s, night, scale):
        return S.title(p, x, y, s, night, scale, motion=p.w == WIDE)

    def section_mark(self, p, x, y, night):
        S.section_mark(p, x, y, night)

    def strip_mark(self, p, x, y, night):
        S.strip_mark(p, x, y, night)

    # ---- the headers' scenes
    phone_scene_rows = SC.PHONE_ROWS["H1"]

    def scene(self, design, p, rule, night, motion):
        return {"H1": SC.h1, "H2": SC.h2, "H3": SC.h3}[design](p, rule, night, motion)

    def scene_narrow(self, design, p, y, night):
        """A phone's H1 stands on its rule; its H2 and H3 carry their scenes under their words (`scene_under`), and
        nothing beside them."""
        if design == "H1":
            SC.h1_phone(p, y, night)

    def phone_rows(self, design, title_w):
        return SC.PHONE_ROWS[design]

    def scene_under(self, design, p, y0, y1, night):
        SC.under(design, p, y0, y1, night)

    def rule_decor(self, p, x0, x1, y, seed, night):
        S.cables(p, x0, x1, y, night, seed=seed)

    def finish(self, p, night):
        """The last pass: the drawing written as lightly as it can be, its tall flat bands, the jar's glass and its
        fluid and the machines' enamel, as rectangles."""
        p.compact()

    # ---- the footers and links
    def heart(self, p, x, y):
        """A heart, 7 by 6: of the brain's crimson by day, of nixie amber by night."""
        R = NIXIE if getattr(p, "night", False) else TISSUE
        art = [".64.43.", "6544432", "5443321", ".33321.", "..321..", "...1..."]
        p.sprite(x, y, art, {str(i): R[i] for i in range(7)})

    def bar(self, p, x0, y0, w, h, period=5):
        """The scale's bar as a gauge tube: the jar's fluid and steel by turns, lit along its top."""
        for yy in range(y0, y0 + h):
            f = (yy - y0) / max(1, h - 1)
            band = 0 if f < 0.2 else (1 if f < 0.7 else 2)
            for xx in range(x0, x0 + w):
                fluid = ((xx - x0) // period) % 2 == 0
                p.px(xx, yy, (FLUID[5], FLUID[4], FLUID[2])[band] if fluid else (STEEL[5], STEEL[3], STEEL[1])[band])

    def link_colours(self, night):
        if night:
            return C["fill_n"], NIXIE[3], C["ink_n"], ROOM[1]
        return C["fill"], ENAMEL[3], C["ink"], X["dim_day"]

    def link_top(self, p, x0, x1, y, seed, night):
        S.link_top(p, x0, x1, y, seed, night)

    def link_icon(self, index, night, ink):
        """The brain, a flask, a bolt and a gear by turns."""
        return S.icon(index, night)

    # ---- the elements
    def card_bevel(self, night):
        return (STEEL[3], ROOM[0]) if night else (C["white"], X["dim_day"])

    def node_deco(self, p, night, x, y, w, h, seed, lid):
        T.node_deco(p, night, x, y, w, h, seed, lid)

    def wire_ink(self, night):
        return T.wire_ink(night)

    def wire_lights(self, p, cells, night, seed):
        T.wire_lights(p, cells, night, seed)

    def dashes(self, night):
        return T.dashes(night)

    def ornament(self, kind, p, x, y, night):
        return T.ornament(kind, p, x, y, night)

    def hist_bar(self, p, bx, base, bw, v, night):
        T.hist_bar(p, bx, base, bw, v, night)

    def peak_mark(self, p, x, y, night):
        T.peak_mark(p, x, y, night)

    def dial_ring(self, p, arc, night):
        T.dial_ring(p, arc, night)

    def dial_tick(self, p, x, y, night):
        T.dial_tick(p, x, y, night)

    def dial_hub(self, p, cx, cy, night):
        T.dial_hub(p, cx, cy, night)

    def material(self, i, xx, yy, y0, y1, lift, night):
        return T.material(i, xx, yy, y0, y1, lift, night)

    def counter_cell(self, q, ox, oy, night):
        T.counter_cell(q, ox, oy, night)

    def counter_ink(self, night, dim):
        return T.counter_ink(night, dim)

    def timeline_line(self, p, x0, x1, y, night):
        T.timeline_line(p, x0, x1, y, night)

    def release(self, p, x, gy, kind, night, i=0):
        T.release(p, x, gy, kind, night, i)

    def today_mark(self, p, x, y, night):
        T.today_mark(p, x, y, night)

    def avatar(self, p, cx, cy, i, person, night):
        T.avatar(p, cx, cy, i, person, night)

    def commit_bar(self, p, x, y, w, fill, night):
        T.commit_bar(p, x, y, w, fill, night)

    def rosette(self, p, cx, cy, r0, r1, n, night):
        T.rosette(p, cx, cy, r0, r1, n, night)

    def seal_mark(self, p, x, y, night):
        T.seal_mark(p, x, y, night)

    def placard_board(self, p, night):
        T.placard_board(p, night)

    def placard_mark(self, p, x, y, night):
        T.placard_mark(p, x, y, night)

    def footer_mark(self, p, x, y, night):
        """In the corner of a title block's notes: a flask."""
        S.section_mark(p, x, y, night)

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        T.badge_top(p, w, s, seed, night, inside)

    def badge_label(self):
        return (ENAMEL[2], C["white"])

    def badge_gold(self):
        return (BRASS[4], X["tag_ink_day"])

    def badge_states(self):
        return {"green": (FLUID[2], C["white"]), "yellow": (BRASS[4], X["tag_ink_day"]),
                "red": (TISSUE[2], C["white"]), "slate": (STEEL[3], C["white"])}

    def badge_swatches(self):
        """The lab's colours, so a written colour keeps its family: the brain's tissue and blush, the jar's fluid
        and aqua, enamel and its blue, brass and gold, nixie amber and orange, steel and chrome, lightning's violet
        and lilac, the tiles' sage and cream, and the dark of the room with its sparks."""
        return {"tissue": (TISSUE[2], C["white"], None), "blush": (TISSUE[5], X["tag_ink_day"], None),
                "fluid": (FLUID[2], C["white"], None), "aqua": (FLUID[5], X["tag_ink_day"], None),
                "enamel": (ENAMEL[2], C["white"], None), "blue": (ENAMEL[4], C["white"], None),
                "brass": (BRASS[3], X["tag_ink_day"], None), "gold": (BRASS[4], X["tag_ink_day"], None),
                "nixie": (NIXIE[2], C["white"], None), "amber": (NIXIE[4], X["tag_ink_day"], None),
                "steel": (STEEL[3], C["white"], None), "chrome": (STEEL[5], X["tag_ink_day"], None),
                "arc": (ARC[3], C["white"], None), "lilac": (ARC[5], X["tag_ink_day"], None),
                "sage": (SAGE[2], X["tag_ink_day"], None), "cream": (SAGE[6], C["ink"], "outline"),
                "room": (ROOM[3], C["ink_n"], "sparks")}

    def badge_pattern(self, pattern, x, y, c, s, text_rows):
        """Sparks in the dark of the room, kept off the letters' rows."""
        if y in text_rows:
            return c
        if pattern == "sparks" and (x * 7 + y * 13) % 19 == 0:
            return (ARC[5], NIXIE[4], FLUID[5])[(x + y) % 3]
        return c

    def badge_outline(self, pattern):
        return SAGE[3] if pattern == "outline" else None

    def badge_shine(self, c, y, h):
        return step(c, 1) if y == 2 else step(c, -1) if y == h - 1 else c

    def plate_edge(self, block):
        return step(block, -1)

    def plate_colours(self, mode):
        if mode == "day":
            return dict(paper=S.DAY_SKY[2], dot=X["dim_day"], frame=ENAMEL[3], block=BRASS[4], ink=C["ink"],
                        letters=X["tag_ink_day"])
        if mode == "night":
            return dict(paper=S.NIGHT_SKY[1], dot=X["dim_night"], frame=FLUID[3], block=NIXIE[4], ink=C["ink_n"],
                        letters=X["tag_ink_night"])
        return dict(paper=BRASS[4], dot=BRASS[3], frame=X["tag_ink_day"], edge=BRASS[3], ink=X["tag_ink_day"])

    # ---- the games
    def game_squares(self, night):
        """By day a board of the lab's own floor, sage tiles and plates of petrol enamel riveted at their corners;
        by night one of the jar's glass, glowing, leaded in steel, and of dark enamel plates."""
        if night:
            return Stuff(FLUID, 3, "glass", STEEL[1]), Stuff(ENAMEL, 2, "metal")
        return Stuff(SAGE, 5, "tile"), Stuff(ENAMEL, 3, "metal")

    def game_frame(self, night):
        """A frame of steel riveted, as the sheet's own frames are."""
        return (Stuff(STEEL, 2), "iron") if night else (Stuff(STEEL, 3), "iron")

    def game_podium(self, night):
        """The machines' petrol enamel, riveted, gauges along its top: of brass by day, glowing amber by night."""
        if night:
            return Podium(Stuff(ENAMEL, 2, "metal"), "shields", Stuff(NIXIE, 4))
        return Podium(Stuff(ENAMEL, 4, "metal"), "shields", Stuff(BRASS, 4))


SET = Brain()
