# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Architect set's own rules, which the checks every design of a collection shares cannot know: what the night alone
shows (the screens' green light blooming round the sets, pooled on the floor and laid on what stands near them) stays
out of the day's files, and the shadows the sets throw on the white wall by day stay out of the night's; a title is a
video wall, charcoal cases round green screens by day casting their shadow on the wall and by night the screens
themselves burning in the dark, a few of them flickering in a moving header; what moves (the titles' screens and the
sets' pictures flickering, the code running down January's big set, the ripple of snow through the year's sets, the
light sweeping across the far wall of screens and the console's keys blinking) moves on its own cadence; every header
stands its own hero where the words leave it room (the big sets and the Architect at his console on H1, the Architect
standing before a tower of sets on H2, his empty chair before a column of sets rising an H3's full height) and every
phone header stands the room under its words; a cable hangs under the row of sets along the top, parting round the
month's mark; every footer stands on the edge of the Architect's console, its meter bridge rising where the cells leave
the wall free and a set showing the room itself after a title block's last cell; a link button is a set's charcoal
plastic with vents along its top; a band of charcoal plastic with a green power light lies along every badge's top; a
counter's numerals hold 4.5:1 on their tubes; and the boards and the podium are cut from the room's own stuffs. The set
is a theme, not a holiday on the calendar, so the checks every design of a collection shares (`design_checks`) run here
over the set directly, with the same contents and the same entry points."""
from __future__ import annotations

import contextlib
import re
import unittest
from unittest import mock

from tests import support
from tests.unit import design_checks as D
from tests.unit.test_holiday_sets import contents

from domain.banners.content import Header
from domain.canvas import DARK, DAY
from domain.collections.hand import MATRIX
from domain.collections.matrix_architect import SET
from domain.collections.matrix_architect import art as A
from domain.collections.matrix_architect import surfaces as F
from domain.collections.matrix_architect.palette import RAMP
from domain.holidays.designs.badges import STYLES as BADGE_STYLES, TOP
from domain.holidays.pixel import Pix, contrast, num

support.install()
KEY = SET.key
HEADER = Header(tone="standard", holiday=KEY)
FLAME, PLASTIC, WALL = RAMP["flame"], RAMP["plastic"], RAMP["wall"]
BLOOM = re.compile(r'<ellipse[^>]*fill="' + FLAME[3] + '"')     # a stack of sets' light, or the light it pools
DRAWN: dict = {}


def header(code: str, night: bool, motion: bool = True, h=HEADER) -> str:
    """A header's file, drawn once for every test that only reads it."""
    key = (code, night, motion, id(h))
    if key not in DRAWN:
        DRAWN[key] = SET.header(code, h, DARK if night else DAY, True, motion)
    return DRAWN[key]


def lettered(draw) -> list:
    """What every title `draw()` sets is set with: the keywords `Pix.text` is called with for each line of a video
    wall."""
    calls, text = [], Pix.text

    def watched(self, *args, **kw):
        if "paint" in kw:
            calls.append(kw)
        return text(self, *args, **kw)
    with mock.patch.object(Pix, "text", watched):
        draw()
    return calls


class Shared(D.Shared, unittest.TestCase):
    SET = SET
    ART = A
    PIECES = ("big_wall", "study", "architect", "console", "audience", "vigil", "tower", "loom", "standing",
              "empty_chair")
    FOOTINGS = ("_footed",)


class Night(unittest.TestCase):
    def test_what_the_night_alone_shows_stays_out_of_the_day_and_the_days_shadows_out_of_the_night(self):
        """By night the screens' green light blooms round every stack of sets and pools on the floor at its foot, and
        the last pass lays it on the plastic, the leather and the steel near them; by day none of it is drawn, and the
        sets throw their shadow on the white wall instead, which the night has none of."""
        for code in ("H1", "H2", "H3"):
            self.assertRegex(header(code, True), BLOOM, (code, "the screens' light by night"))
            self.assertNotRegex(header(code, False), BLOOM, (code, "none by day"))
            draw = getattr(SET, code.lower())
            for night in (False, True):
                lit = D.painted(SET, lambda: draw(HEADER, night, True), "finish")
                shadows = D.painted(SET, lambda: draw(HEADER, night, True), "scene")[WALL[3]]
                self.assertEqual(bool(lit), night, (code, night, "the light laid on what stands near the screens"))
                self.assertEqual(bool(shadows), not night, (code, night, "the sets' shadows on the wall"))


class Titles(unittest.TestCase):
    def test_a_title_is_a_video_wall_of_cases_by_day_and_of_burning_screens_by_night(self):
        """Every unit of a title's letters is a little television: by day its charcoal case makes the letter, lit
        along its top and left and shaded along its foot and right, a green screen in its middle, the letters outlined
        in the cases' plastic and casting their shadow on the wall; by night the screens themselves make it, white at
        their hearts and burning on the phosphor, their light blooming round the letters."""
        for night in (False, True):
            calls = lettered(lambda: SET.h1(HEADER, night, True))
            self.assertTrue(calls, night)
            for kw in calls:
                self.assertEqual(kw["paint"].name, "tv", night)
                self.assertEqual(kw["shadow"], RAMP["dusk"][0] if night else RAMP["shell"][2], night)
                self.assertEqual(kw["outline"], PLASTIC[0] if night else PLASTIC[1], night)
                self.assertEqual("glow" in kw, night, night)
            svg = header("H1", night)
            tile = re.search(r'<pattern id="patv4' + ("n" if night else "d") + r'".*?</pattern>', svg).group(0)
            tones = set(re.findall(r'fill="(#[0-9A-F]{6})"', tile))
            want = {FLAME[6], FLAME[5], FLAME[4], PLASTIC[0]} if night else {PLASTIC[4], PLASTIC[1], FLAME[4], FLAME[3]}
            self.assertEqual(tones, want, night)

    def test_a_few_of_a_titles_screens_flicker_only_in_a_moving_header(self):
        """In a moving header a few of every title's screens flicker on their own on the phosphor, as the sets of a
        video wall do; the still file and a phone's hold every screen steady."""
        for night in (False, True):
            with mock.patch.object(A, "title_flicker", wraps=A.title_flicker) as flicker:
                p = SET.h1(HEADER, night, True)
            self.assertTrue(flicker.called, night)
            lit = {c for L, cells in p.layers.items() if L.startswith("fl") for c in cells.values()}
            self.assertTrue({FLAME[6], FLAME[5]} <= lit, night)
            with mock.patch.object(A, "title_flicker", wraps=A.title_flicker) as flicker:
                SET.h1(HEADER, night, False)
                SET.h1_narrow(HEADER, night)
            self.assertFalse(flicker.called, (night, "no screen flickers in a still file"))

    def test_what_moves_moves_on_its_own_cadence(self):
        """In a moving header the titles' screens and the sets' pictures flicker on the engine's flicker, the code
        runs down January's big set a unit every eighth of a second, a ripple of snow passes through the year's sets
        on the hand's period, the light sweeps slowly across the far wall of screens and the console's keys blink;
        a still header holds all of it."""
        cadences = {"1.8s": "the screens flicker", f"{num(A.S.BH * 0.12)}s": "the code runs",
                    f"{num(MATRIX.glint)}s": "the snow ripples", f"{num(A.SWEEP)}s": "the light sweeps",
                    "5.2s": "the keys blink"}
        for night in (False, True):
            moving = header("H1", night)
            for dur, what in cadences.items():
                self.assertIn(f'dur="{dur}"', moving, (night, what))
            self.assertNotIn("<animate", header("H1", night, motion=False))


class Heroes(unittest.TestCase):
    def test_every_header_stands_its_own_hero_where_the_words_leave_it_room(self):
        """An H1 stands the big sets at its left and the Architect at his console under more sets at its right; an H2
        the Architect standing before a tower of sets; an H3 his empty chair before a column of sets; for the kit's own
        lines, by day and by night."""
        named = {"H1": ("big_wall", "study", "console", "architect"), "H2": ("audience", "tower", "standing"),
                 "H3": ("vigil", "tower", "empty_chair")}
        for code, names in named.items():
            for night in (False, True):
                with contextlib.ExitStack() as stack:
                    spies = [stack.enter_context(mock.patch.object(A, n, wraps=getattr(A, n))) for n in names]
                    getattr(SET, code.lower())(HEADER, night, True)
                self.assertTrue(all(spy.called for spy in spies), (code, night))

    def test_an_h2s_tower_of_sets_rises_to_the_ceiling_with_the_architect_before_it(self):
        """The H2's tower of sets stands at the right three across, its cables rising from it to the ceiling under the
        row of sets along the top, and the Architect stands before it, two units clear of every word, for every shared
        content."""
        for name, (h, _) in contents(KEY).items():
            with mock.patch.object(A, "tower", wraps=A.tower) as tower:
                p, pixels, _ = D.sprites(SET, lambda: SET.h2(h, False, True), "scene")
            (call,) = tower.call_args_list
            self.assertEqual(call.args[3], 3, name)
            self.assertLessEqual(min(y for _, y in pixels), A.TOP + 4, name)
            self.assertGreaterEqual(min(x for x, _ in pixels), 318, name)

    def test_an_h3s_column_of_sets_rises_the_strips_full_height(self):
        """At the right of every wide H3 a column of sets stands on its steel stand with the Architect's empty chair
        turned to it, the cables over it rising to the ceiling: from the floor to within a few rows of the row of sets
        along the top, the strip's full height, for every shared content."""
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "tower", wraps=A.tower) as tower:
                    p, pixels, _ = D.sprites(SET, lambda: SET.h3(h, night, True), "scene")
                (call,) = tower.call_args_list
                g, top = call.args[2], min(y for _, y in pixels)
                self.assertEqual(call.args[3], 1, (name, night))
                self.assertLessEqual(top, A.TOP + 4, (name, night))
                self.assertGreaterEqual(g - top, 54, (name, night))
                self.assertGreaterEqual(min(x for x, _ in pixels), 356, (name, night))

    def test_a_phones_headers_stand_the_room_under_their_words(self):
        """A phone's H1 stands the whole room across its width under the words, at least 48 rows tall: the big sets at
        the left, the Architect at his console and a tower of sets at the right; its H2 the Architect standing before
        a tower of sets, his chair waiting behind him; its H3 his empty chair before a column of sets, a big set with
        the code running at the left; for every shared content."""
        for name, (h, _) in contents(KEY).items():
            for code, piece, hook in (("H1", "phone_room", "scene_narrow"), ("H2", "phone_audience", "scene_under"),
                                      ("H3", "phone_vigil", "scene_under")):
                draw = {"H1": SET.h1_narrow, "H2": SET.h2_narrow, "H3": SET.h3_narrow}[code]
                with mock.patch.object(A, piece, wraps=getattr(A, piece)) as scene:
                    p, pixels, _ = D.sprites(SET, lambda: draw(h, False), hook)
                self.assertTrue(scene.called, (name, code))
                xs, ys = [x for x, _ in pixels], [y for _, y in pixels]
                self.assertLessEqual(min(xs), 12, (name, code))
                self.assertGreaterEqual(max(xs), 168, (name, code))
                self.assertGreaterEqual(max(ys) - min(ys) + 1, 48, (name, code))

    def test_a_cable_hangs_under_the_row_of_sets_and_parts_round_the_months_mark(self):
        """Every header slings a cable under its row of sets along the top, sagging between grey ties; as its month's
        design it parts round the month's mark, and kept all year it runs on across the top centre."""
        held = SET.on(D.months_day(SET))
        for code in ("H1", "H2", "H3"):
            for design, parted in ((held, True), (SET, False)):
                p, pixels, _ = D.sprites(design, lambda: getattr(design, code.lower())(HEADER, False, True), "garland")
                self.assertTrue(pixels, code)
                self.assertTrue(all(A.TOP <= y <= A.TOP + A.SAG + 2 for _, y in pixels), code)
                centre = any(p.w // 2 - 4 <= x <= p.w // 2 + 4 for x, _ in pixels)
                self.assertEqual(centre, not parted, (code, design.marked))


class Footers(unittest.TestCase):
    def test_every_footer_stands_on_the_console_with_a_set_after_its_last_cell(self):
        """Every footer stands on the front edge of the Architect's console, a brass rail over its keys along the
        footer's foot; its meter bridge rises behind it where the cells leave the wall free, and a title block stands
        a set showing the room itself after its last cell, the way back up, its picture on the phosphor."""
        _, f = contents(KEY)["repository"]
        for night in (False, True):
            with mock.patch.object(A, "tv", wraps=A.tv) as sets, \
                    mock.patch.object(F, "meter_bridge", wraps=F.meter_bridge) as bridge:
                p = SET.f1(f, night)
            (call,) = sets.call_args_list
            self.assertEqual(call.args[3], "architect", night)
            self.assertGreater(call.args[1], max(b[2] for b in p.words), (night, "after the way back up"))
            self.assertTrue(bridge.called, night)
            for draw in (SET.f1, SET.f2, SET.f1_narrow, SET.f2_narrow):
                drawn = []
                rail = D.painted(SET, lambda: drawn.append(draw(f, night)), "_footed")
                brass = sum(n for c, n in rail.items() if c in RAMP["brass"])
                self.assertGreater(brass, drawn[0].w // 2, (draw.__name__, night, "the brass rail"))


class Links(unittest.TestCase):
    def test_a_link_button_is_a_sets_case_with_vents_along_its_top_and_a_sprite_of_its_own(self):
        """A link button is a set's charcoal plastic by day and a tube's dark glass by night in a rim of pale grey,
        lettered in the phosphor, vents slotted along its top edge, and the sprite at its start one of the room's
        things, a different one for each of four buttons."""
        sprites = {tuple(SET.link_icon(i, False, "#000000")[0]) for i in range(4)}
        self.assertEqual(len(sprites), 4)
        for night in (False, True):
            p = SET.link_button("Issues", 0, night)
            fill, edge, ink, _ = SET.link_colours(night)
            self.assertGreaterEqual(contrast(ink, fill), 4.5, night)
            vents = [c for (x, y), c in p.layers["base"].items() if y == 1]
            self.assertTrue(vents and set(vents) <= set(PLASTIC), night)


class Badges(unittest.TestCase):
    def test_a_band_of_charcoal_plastic_lies_along_every_badges_top_with_its_power_light(self):
        """Every badge, classic, plate and live, wears a band of a set's charcoal plastic along its top two rows, its
        vents slotted in it and a power light burning green at its right end, the letters under it."""
        for style in BADGE_STYLES:
            drawn = [SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                       SET.badge_states()["green"])]
            drawn += [SET.plate_badge(style, "License", "MIT", "scale", mode) for mode in ("day", "night")]
            for p in drawn:
                rows = {c for (x, y), c in p.layers["base"].items() if y in (0, 1)}
                self.assertTrue(rows and rows <= set(PLASTIC) | {FLAME[4]}, (style, rows - set(PLASTIC)))
                self.assertIn(FLAME[4], rows, (style, "the power light"))
                self.assertTrue(all(y >= TOP for _, _, _, y, _ in p.uses["base"]), "the letters sit under the band")

    def test_a_counters_numerals_hold_4_5_on_their_tubes(self):
        for night in (False, True):
            q = Pix(20, 20)
            SET.counter_cell(q, 2, 2, night)
            glass = q.layers["base"][(7, 8)]
            self.assertGreaterEqual(contrast(SET.counter_ink(night, False), glass), 4.5, night)
            self.assertGreaterEqual(contrast(SET.counter_ink(night, True), glass), 2.0, night)


class Games(unittest.TestCase):
    def test_the_boards_and_the_podium_are_cut_from_the_rooms_own_stuffs(self):
        """The boards are the white room's warm white tiles and the frame's brushed pale grey plastic in a frame of a
        set's charcoal, screwed at its corners, and the podium is the wingback's white leather, plain: the room's own
        tones, never those the hand lends every design."""
        lent = set(MATRIX.ramp("flame")) | set(MATRIX.ramp("moon")) | set(MATRIX.body) | set(MATRIX.muted)
        lent |= {c for skin in ("skin0", "skin1", "skin2") for c in MATRIX.ramp(skin)}
        for night in (False, True):
            light, dark = SET.game_squares(night)
            frame, style = SET.game_frame(night)
            podium = SET.game_podium(night)
            self.assertEqual((light.ramp, light.grain), (RAMP["wall"], "tile"))
            self.assertEqual((dark.ramp, dark.grain), (RAMP["shell"], "metal"))
            self.assertEqual((frame.ramp, style), (RAMP["plastic"], "iron"))
            self.assertEqual((podium.stuff.ramp, podium.stuff.grain), (RAMP["leather"], "satin"))
            self.assertEqual(podium.style, "plain")
            for stuff in (light, dark, frame, podium.stuff):
                self.assertFalse(set(stuff.ramp) & lent, stuff)


if __name__ == "__main__":
    unittest.main()
