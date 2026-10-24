# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Rooftop design's tests: the checks every design of a collection shares, run over Rooftop, and its own rules,
which the shared checks cannot know: what the night alone shows (windows and lamps burning phosphor, the searchlights
sweeping the sky and the moon) stays out of the day's files, and the day's clouds and pigeons out of the night's; a
title is towers of blue mirror glass by day and the same glass lit pane by pane in phosphor by night; the leaper
hangs on his four-second loop, the rotor turns, the clouds drift, the searchlights sweep and the bullets creep only in
a wide moving header; each header's hero stands where it should, the jump between the two roofs on an H1, the fight
on the roof before a tower of glass rising full height on an H2 and the water tower rising the strip's full height on
an H3; every footer stands on the parapet, with the water tower and its lamp after a title block's last cell; a link
button hangs from a steel beam and each of the four takes its own sprite; a badge's top two rows are the steel beam;
a counter's numerals hold 4.5:1 on their flaps; and the games' boards and podium are the roof's own stuffs."""
from __future__ import annotations

import re
import unittest
from unittest import mock

from tests.unit import design_checks as D
from tests.unit.test_holiday_sets import contents

from domain.banners.content import Header
from domain.canvas import DARK, DAY
from domain.holidays.designs.badges import STYLES as BADGE_STYLES, TOP
from domain.holidays.designs.materials import Stuff
from domain.collections.matrix_rooftop import H2_X, H3_X, SET
from domain.collections.matrix_rooftop import art as A
from domain.collections.matrix_rooftop.palette import C, RAMP
from domain.holidays.pixel import Pix, contrast

KEY = SET.key
HEADER = Header(tone="standard", holiday=KEY)
FLAME, MOON, PIGEON, STEEL = (set(RAMP[n]) for n in ("flame", "moon", "pigeon", "steel"))
CLOUDS = 'id="cdt"'                                  # the tile of clouds drifting across the sky by day
BEAM = re.compile(r'fill="' + RAMP["flame"][4] + r'" fill-opacity=".17"')   # a searchlight's core by night


class Shared(D.Shared, unittest.TestCase):
    SET = SET
    ART = A
    PIECES = ("far_city", "facade", "parapet", "water_tower", "leaper", "helicopter", "beams", "cloud_drift",
              "bulkhead", "glass_tower", "figure", "bullets", "roof_deck", "roof_tower", "truss")
    FOOTINGS = ("_footed",)


class Night(unittest.TestCase):
    def test_what_the_night_alone_shows_stays_out_of_the_day_and_the_days_clouds_out_of_the_night(self):
        for code in ("H1", "H2", "H3"):
            day = SET.header(code, HEADER, DAY, True, True)
            night = SET.header(code, HEADER, DARK, True, True)
            self.assertFalse([c for c in FLAME if c in day], (code, "a light burning by day"))
            self.assertFalse([c for c in MOON if c in day], (code, "the moon by day"))
            self.assertIsNone(BEAM.search(day), (code, "a searchlight by day"))
            self.assertIn(CLOUDS, day, (code, "the clouds drift"))
            self.assertTrue([c for c in FLAME if c in night], (code, "the windows burn by night"))
            self.assertNotIn(CLOUDS, night, (code, "a cloud by night"))
            scene = D.painted(SET, lambda: D.wide(SET, code)(HEADER, True, True), "scene")
            self.assertFalse([c for c in PIGEON if c in scene], (code, "a pigeon in the scene by night"))
        day, night = (SET.header("H1", HEADER, theme, True, True) for theme in (DAY, DARK))
        self.assertTrue([c for c in PIGEON if c in day], "the pigeons on the parapet")
        self.assertTrue([c for c in MOON if c in night], "the moon over the city")
        for code in ("H1", "H2"):
            self.assertIsNotNone(BEAM.search(SET.header(code, HEADER, DARK, True, True)), (code, "the searchlights"))


class Titles(unittest.TestCase):
    def test_a_title_is_towers_of_mirror_glass_by_day_lit_pane_by_pane_by_night(self):
        day = SET.header("H1", HEADER, DAY, True, True)
        night = SET.header("H1", HEADER, DARK, True, True)
        tile = re.search(r'<pattern id="paglass\d+d".*?</pattern>', day)
        self.assertIsNotNone(tile, "the mirror glass ruled in floors and bays")
        self.assertTrue({c for c in RAMP["glass"] if c in tile.group(0)} >= {RAMP["glass"][5], RAMP["glass"][6]})
        lit = re.search(r'<pattern id="paglass\d+n".*?</pattern>', night)
        self.assertIsNotNone(lit, "the dark glass by night")
        self.assertTrue([c for c in FLAME if c in lit.group(0)], "lit pane by pane in phosphor")


class Motion(unittest.TestCase):
    def test_the_leaper_the_rotor_the_sky_and_the_bullets_move_only_in_a_wide_moving_header(self):
        day = SET.header("H1", HEADER, DAY, True, True)
        night = SET.header("H1", HEADER, DARK, True, True)
        self.assertEqual(day.count(f'dur="{A.num(A.LOOP)}s"'), 2, "the leaper hangs and his coat lifts")
        self.assertIn(f'dur="{A.num(A.DRIFT)}s"', day, "the clouds drift on one of the slow sweeps")
        self.assertIn(f'dur="{A.num(A.ROTOR)}s"', day, "the rotor turns")
        self.assertEqual(len(re.findall(r'type="rotate"[^>]*dur="(36|44)s"', night)), 2, "two searchlights sweep")
        h2 = SET.header("H2", HEADER, DAY, True, True)
        self.assertIn('dur="9s"', h2, "the bullets creep, as time slowed")
        for code in ("H1", "H2", "H3"):
            for still in (SET.header(code, HEADER, DARK, True, False), SET.header(code, HEADER, DAY, False, False)):
                self.assertNotIn("<animate", still, code)


class Heroes(unittest.TestCase):
    def test_an_h1_has_the_jump_between_the_near_roof_and_the_far_one(self):
        h, _ = contents(KEY)["kit"]
        for night in (False, True):
            with mock.patch.object(A, "water_tower", wraps=A.water_tower) as tower, \
                    mock.patch.object(A, "leaper", wraps=A.leaper) as leaper, \
                    mock.patch.object(A, "helicopter", wraps=A.helicopter) as heli:
                SET.h1(h, night, True)
            (t,), (lp,), (hc,) = tower.call_args_list, leaper.call_args_list, heli.call_args_list
            self.assertLess(t.args[1], 12, "the water tower on the near roof, at the left")
            self.assertTrue(t.args[1] < lp.args[1] < 80, "the leaper off its edge")
            self.assertGreater(hc.args[1], 340, "the helicopter over the far roof, at the right")

    def test_an_h2_has_the_fight_on_the_roof_before_a_tower_of_glass_risen_full_height(self):
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "glass_tower", wraps=A.glass_tower) as tower, \
                        mock.patch.object(A, "figure", wraps=A.figure) as figure, \
                        mock.patch.object(A, "bullets", wraps=A.bullets) as bullets:
                    p, pixels, _ = D.sprites(SET, lambda: SET.h2(h, night, True), "scene")
                (t,), (b,) = tower.call_args_list, bullets.call_args_list
                agent, neo = figure.call_args_list
                x0, x1, top, base = t.args[1:5]
                self.assertEqual((top, x1), (22, p.w - 6), (name, night, "from under the truss, at the right"))
                self.assertGreaterEqual(base - top, 50, (name, night, "risen full height"))
                self.assertEqual((agent.args[1], neo.args[1]), ("agent", "neo"), (name, night))
                self.assertTrue(H2_X <= agent.args[2] < b.args[1] < b.args[2] <= neo.args[2] + 8, (name, night))
                self.assertEqual([xy for xy in pixels if D.near(p, xy, 2)], [], (name, night))

    def test_an_h3_has_the_water_tower_rising_the_strips_full_height(self):
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "roof_tower", wraps=A.roof_tower) as roof, \
                        mock.patch.object(A, "water_tower", wraps=A.water_tower) as tower:
                    p, pixels, _ = D.sprites(SET, lambda: SET.h3(h, night, True), "scene")
                (r,) = roof.call_args_list
                big = [c for c in tower.call_args_list if c.kwargs.get("w") == 31]
                x0, x1, top, g = r.args[1:5]
                self.assertTrue(H3_X <= x0 and x1 == p.w - 6, (name, night))
                self.assertEqual(top, 22, (name, night, "from under the truss"))
                self.assertEqual(len(big), 1, (name, night, "the great water tower"))
                self.assertLessEqual(min(y for _, y in pixels), 26, (name, night, "the strip's full height"))


class Phones(unittest.TestCase):
    def test_a_phones_h1_has_the_whole_jump_under_its_words(self):
        """A phone's H1 stands the whole jump across its width under the words, at least 48 rows tall: the near
        roof with its water tower, the leaper and the far roof, for every shared content."""
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "leaper", wraps=A.leaper) as leaper:
                    p, pixels, _ = D.sprites(SET, lambda: SET.h1_narrow(h, night), "scene_narrow")
                self.assertTrue(leaper.called, (name, night))
                xs, ys = [x for x, _ in pixels], [y for _, y in pixels]
                self.assertLessEqual(min(xs), 6, (name, night))
                self.assertGreaterEqual(max(xs), 173, (name, night))
                self.assertGreaterEqual(max(ys) - min(ys) + 1, 48, (name, night))

    def test_a_phones_h2_and_h3_stand_their_heroes_under_their_words_whatever_they_say(self):
        for code, hero in (("H2", "bullet_time"), ("H3", "roof_tower")):
            self.assertEqual(SET.phone_rows(code, 0), SET.phone_rows(code, 400), code)
            for name, (h, _) in contents(KEY).items():
                for night in (False, True):
                    with mock.patch.object(A, hero, wraps=getattr(A, hero)) as drawn:
                        p, pixels, _ = D.sprites(SET, lambda: D.phone(SET, code)(h, night), "scene_under")
                    self.assertTrue(drawn.called, (code, name, night))
                    ys = [y for _, y in pixels]
                    self.assertGreaterEqual(max(ys) - min(ys) + 1, 44, (code, name, night))


class Footers(unittest.TestCase):
    def test_every_footer_stands_on_the_parapet_with_the_water_tower_after_its_last_cell(self):
        """Every footer stands on the parapet, its coping lit along its top, and on a title block whose cells leave
        it room the small water tower and its lamp after its last cell, the lamp burning by night."""
        h, f = contents(KEY)["repository"]
        for night in (False, True):
            with mock.patch.object(A, "water_tower", wraps=A.water_tower) as tower, \
                    mock.patch.object(A, "lamp", wraps=A.lamp) as lamp:
                p = SET.f1(f, night)
            (call,) = tower.call_args_list
            self.assertGreater(call.args[1], max(b[2] for b in p.words), "after the last cell")
            self.assertEqual(len(lamp.call_args_list), 1, "its lamp beside it")
            self.assertEqual(bool([c for c in p.layers["base"].values() if c in FLAME]), night, "lit by night")
        for name, (_, f) in contents(KEY).items():
            for draw in (SET.f1, SET.f2, SET.f1_narrow, SET.f2_narrow):
                for night in (False, True):
                    q = draw(f, night)
                    coping = {c for c in q.layers["foot"].values()} & set(RAMP["concrete"])
                    self.assertTrue(coping, (name, draw.__name__, night, "the parapet's coping"))


class Links(unittest.TestCase):
    def test_a_link_button_hangs_from_a_steel_beam_and_takes_its_own_sprite(self):
        for night in (False, True):
            for i in range(4):
                p = SET.link_button("Docs", i, night)
                rows = {c for (x, y), c in p.layers["base"].items() if y in (0, 1)}
                self.assertTrue(rows and rows <= STEEL, (night, i, rows - STEEL))
        sprites = [tuple(SET.link_icon(i, False, C["white"])[0]) for i in range(4)]
        self.assertEqual(len(set(sprites)), 4, "four sprites of their own")


class Badges(unittest.TestCase):
    def test_a_steel_beam_lies_along_every_badges_top_two_rows_with_the_letters_under_it(self):
        for style in BADGE_STYLES:
            drawn = [SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                       SET.badge_states()["green"])]
            drawn += [SET.plate_badge(style, "License", "MIT", "scale", mode) for mode in ("day", "night")]
            for p in drawn:
                rows = {c for (x, y), c in p.layers["base"].items() if y in (0, 1)}
                self.assertTrue(rows and rows <= STEEL, (style, rows - STEEL))
                self.assertTrue(all(y >= TOP for _, _, _, y, _ in p.uses["base"]), "the letters sit under the beam")

    def test_a_counters_numerals_hold_4_5_on_their_flaps(self):
        for night in (False, True):
            q = Pix(20, 20)
            SET.counter_cell(q, 2, 2, night)
            face = q.layers["base"][(7, 5)]
            self.assertGreaterEqual(contrast(SET.counter_ink(night, False), face), 4.5, night)
            self.assertGreaterEqual(contrast(SET.counter_ink(night, True), face), 2.0, night)


class Games(unittest.TestCase):
    def test_the_boards_and_the_podium_are_the_roofs_own_stuffs(self):
        own = set(SET.tokens) - set(SET.hand.tokens)
        for night in (False, True):
            light, dark = SET.game_squares(night)
            frame, style = SET.game_frame(night)
            podium = SET.game_podium(night)
            for stuff in (light, dark, frame, podium.stuff):
                self.assertIsInstance(stuff, Stuff)
                self.assertTrue({c.upper() for c in stuff.ramp} <= own, (night, stuff.base))
            self.assertEqual((light.grain, dark.grain), ("stone", "glass"), "concrete and glass")
            self.assertEqual(style, "iron", "a frame of steel, riveted")
            self.assertEqual((podium.stuff.base, podium.stuff.grain, podium.style), (RAMP["cedar"][3], "wood",
                                                                                     "plain"))


if __name__ == "__main__":
    unittest.main()
