# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Heaven & Hell, a pixel theme: angels by day and demons by night, `theme: heaven-and-hell`.

A page in it is drawn in this set every day of the year (see `pixelthemes`), twice: in GitHub's light mode the
page is heaven, and in its dark mode the same page is hell, drawn to the same plan so that each thing of heaven has
its fallen twin standing where it stood.

By day the sky is a deep azure warming to gold over the clouds, heaven's light falling through it in shafts, in a
gilt frame strung with pearls under a festoon of pearls hung with gold stars, and the titles are gold leaf that a
glint crosses. Every header stands on a sea of cloud: heaped into cumulus wherever a figure stands, and lying low,
a deck of cloud seen far off, under the words. The H1 is heaven's gate, the pearly gates open on their cloud at the
left and the archangel on guard at the right; the H2 the archangel keeping vigil before the glory of heaven; the H3
a herald in flight whose trumpet throws a fan of light across the sky.

By night the sky is black smoke reddening to a crimson horizon, embers rising through it, in a frame of iron
studded red-hot under a chain hung with caged flames, and the titles are hellfire that flames lick. Every header
stands on a river of lava, fire licking up off it, black rock backlit by the fires heaped where heaven's cumulus
stood. The gates of hell stand where heaven's stood, the demon where the angel stood, before a wall of fire on the
H2, and on the H3 the herald of hell blows a jet of fire from a ram's horn.
"""
from __future__ import annotations

from ...holidays.designs import WIDE, Holiday
from ...holidays.designs.badges import inside
from ...holidays.designs.materials import Podium, Stuff
from ...holidays.pixel import Pix
from . import scenes as SC
from . import sheet as S
from . import trim as T
from .palette import C, RAMP, TOKENS, X, step

GOLD, PEARL, LAVA, FIRE, IRON = RAMP["gold"], RAMP["pearl"], RAMP["lava"], RAMP["fire"], RAMP["iron"]


class HeavenAndHell(Holiday):
    """Heaven & Hell: the set a page in the pixel theme is drawn in, every day it is not a holiday's or its
    birthday."""
    key = "heaven-and-hell"
    name = "Heaven & Hell"
    tokens = frozenset(TOKENS)

    # ---- colour and paper
    def ink(self, night):
        return dict(
            title=X["title_night"] if night else X["title_day"],
            shadow=LAVA[0] if night else GOLD[1],
            body=C["ink_n"] if night else C["ink"], muted=X["muted_night"] if night else X["muted_day"],
            rule=X["rule_night"] if night else X["rule_day"], accent=X["accent_night"] if night else X["accent_day"],
            tag=LAVA[4] if night else GOLD[4], tag_ink=X["tag_ink_night"] if night else X["tag_ink_day"],
            fill=C["fill_n"] if night else C["fill"], dim=X["dim_night"] if night else X["dim_day"],
        )

    def paper(self, p, night, uid="p"):
        S.paper(p, night, uid=uid)

    def bg_at(self, p, night, y):
        return S.bg_at(p, night, y)

    def stars(self, p, x0, y0, x1, y1, n, seed=3, twinkling=True, faint=False, avoid=()):
        S.embers(p, x0, y0, x1, y1, n, seed=seed, twinkling=twinkling, faint=faint, avoid=avoid)

    def sky(self, p, night, y1, seed=1, motion=True, avoid=()):
        """Heaven's sky and its shafts of light by day, with a few points of light; by night hell's, the fires'
        red thrown up it and embers drifting through it."""
        self.paper(p, night)
        if night:
            S.heat(p, int(y1 * 0.45), y1 + 1)
            self.stars(p, 6, 14, p.w - 6, y1, n=p.w // (20 if p.lite else 10), seed=seed, twinkling=motion,
                       avoid=avoid)
        else:
            if not p.lite:
                S.rays(p, seed=seed)
            S.glints(p, 8, 14, p.w - 8, int(y1 * 0.8), n=p.w // (60 if p.lite else 30), seed=seed,
                     twinkling=motion, avoid=avoid)

    def frame(self, p, night, webs=False):
        S.frame(p, night, header=webs)

    def garland(self, p, x0, x1, y, night, seed=0, sag=4, span=38, spacing=10):
        S.festoon(p, x0 + 12, x1 - 12, y, night, seed=seed, sag=sag, span=span)

    def tag(self, p, x, y, w, h, night):
        """By day a block of gold leaf, by night a block of glowing lava: lit along its top, shaded at its foot."""
        R = LAVA if night else GOLD
        base = R[4]
        p.rect(x, y, w, h, base)
        p.hline(x, x + w, y, step(base, 1))
        p.hline(x, x + w, y + h - 1, step(base, -1))

    def title_text(self, p, x, y, s, night, scale):
        return S.title(p, x, y, s, night, scale, motion=p.w == WIDE)

    # ---- the headers' scenes
    phone_scene_rows = SC.PHONE_ROWS["H1"]

    def scene(self, design, p, rule, night, motion):
        return {"H1": SC.h1, "H2": SC.h2, "H3": SC.h3}[design](p, rule, night, motion)

    def scene_narrow(self, design, p, y, night):
        if design == "H1":
            SC.h1_phone(p, y, night)
        else:
            SC.narrow(design, p, y, night)

    def phone_rows(self, design, title_w):
        return SC.PHONE_ROWS[design]

    def scene_under(self, design, p, y0, y1, night):
        SC.under(design, p, y0, y1, night)

    def rule_decor(self, p, x0, x1, y, seed, night):
        if night:
            S.crust(p, x0, x1, y, seed=seed)
        else:
            S.wisps(p, x0, x1, y, seed=seed)

    # ---- the footers and links
    def heart(self, p, x, y):
        """A heart, 7 by 6: by day a ruby heart lit on its upper lobe, by night a heart of fire."""
        R = RAMP["rose"] if not getattr(p, "night", False) else RAMP["lava"]
        art = [".64.43.", "6544432", "5443321", ".33321.", "..321..", "...1..."]
        p.sprite(x, y, art, {str(i): R[i] for i in range(7)})

    def bar(self, p, x0, y0, w, h, period=5):
        """The scale's bar in heaven's gold and hell's fire by turns, lit along its top."""
        for yy in range(y0, y0 + h):
            f = (yy - y0) / max(1, h - 1)
            band = 0 if f < 0.2 else (1 if f < 0.7 else 2)
            for xx in range(x0, x0 + w):
                gold = ((xx - x0) // period) % 2 == 0
                p.px(xx, yy, (GOLD[5], GOLD[4], GOLD[2])[band] if gold else (LAVA[5], LAVA[3], LAVA[1])[band])

    def link_colours(self, night):
        if night:
            return C["fill_n"], LAVA[2], C["ink_n"], IRON[1]
        return C["fill"], GOLD[2], C["ink"], X["dim_day"]

    def link_icon(self, index, night, ink):
        return [".......", "...#...", "..###..", ".#####.", "..###..", "...#...", "......."], {"#": ink}

    # ---- the elements
    def card_bevel(self, night):
        return (LAVA[1], RAMP["basalt"][0]) if night else (C["white"], X["dim_day"])

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

    def placard_mark(self, p, x, y, night):
        T.placard_mark(p, x, y, night)

    def footer_mark(self, p, x, y, night):
        """In the corner of a title block's notes: a feather drifting by day, a skull by night."""
        T.placard_mark(p, x, y - 1, night)

    # ---- the badges
    def badge_top(self, p, w, s, seed, night):
        T.badge_top(p, w, s, seed, night, inside)

    def badge_label(self):
        return (RAMP["azure"][1], C["white"])

    def badge_gold(self):
        return (GOLD[3], X["tag_ink_day"])

    def badge_states(self):
        return {"green": (RAMP["laurel"][2], C["white"]), "yellow": (GOLD[4], X["tag_ink_day"]),
                "red": (LAVA[2], C["white"]), "slate": (IRON[3], C["white"])}

    def badge_swatches(self):
        return {"gold": (GOLD[4], X["tag_ink_day"], None), "pearl": (PEARL[5], C["ink"], None),
                "fire": (LAVA[3], C["white"], None), "iron": (IRON[2], C["white"], None)}

    def plate_colours(self, mode):
        if mode == "day":
            return dict(paper=S.DAY_SKY[2], dot=X["dim_day"], frame=GOLD[2], block=GOLD[4], ink=C["ink"],
                        letters=X["tag_ink_day"])
        if mode == "night":
            return dict(paper=S.NIGHT_SKY[1], dot=X["dim_night"], frame=LAVA[3], block=LAVA[4], ink=C["ink_n"],
                        letters=X["tag_ink_night"])
        return dict(paper=GOLD[4], dot=GOLD[3], frame=X["tag_ink_day"], edge=GOLD[3], ink=X["tag_ink_day"])

    # ---- the games
    def game_squares(self, night):
        """By day a board of white marble veined in pearl and of beaten gold, heaven's two stuffs; by night one of
        bone and of black rock reddened by the fires."""
        if night:
            return Stuff(RAMP["bone"], 3, "stone"), Stuff(RAMP["scorch"], 4, "slate")
        return Stuff(PEARL, 5, "veins"), Stuff(GOLD, 3, "metal")

    def game_frame(self, night):
        """A gilt frame by day; by night one of iron, as the sheet's own frames are."""
        return (Stuff(IRON, 3), "iron") if night else (Stuff(GOLD, 4), "gilt")

    def game_podium(self, night):
        """By day a podium of white marble hung with a victor's laurel; by night one of black rock, crenellated,
        the fallen's fortress."""
        if night:
            return Podium(Stuff(RAMP["basalt"], 4, "stone"), "crenels")
        return Podium(Stuff(PEARL, 4, "veins"), "garland", Stuff(RAMP["laurel"], 3))


SET = HeavenAndHell()
