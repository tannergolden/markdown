# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Dojo design's tests: the checks every design of a collection shares, run over Dojo, and its own rules, which
the shared checks cannot know: what the night alone shows (the lanterns burning phosphor, the moon over the city and
the code raining past the round window and the pagoda) stays out of the day's files, and the day's clouds out of the
night's; a title is black lacquer edged in gold leaf by day, its dry brush fraying, and gold leaf ringed in lacquer by
night; the petals drift on one of the hand's slow sweeps, the fighters keep their four-second idle and the city's
code rains only in a wide moving header; each header's hero stands where it should, the flying kick over the byobu of
the great wave on an H1, the two fighters before the pine byobu on an H2 and the pagoda rising the strip's full height
on an H3; every footer stands on the dojo's floor, with the alcove after a title block's last cell; a link button
hangs a straw rope along its top and each of the four takes its own sprite; a badge's top two rows are the straw rope;
a counter's numerals hold 4.5:1 on their name plates; and the games' boards and podium are the dojo's own stuffs."""
from __future__ import annotations

import unittest
from unittest import mock

from tests.unit import design_checks as D
from tests.unit.test_holiday_sets import contents

from domain.banners.content import Header
from domain.canvas import DARK, DAY
from domain.holidays.designs.badges import STYLES as BADGE_STYLES, TOP
from domain.holidays.designs.materials import PODIUMS, Stuff
from domain.collections.matrix_dojo import PAGODA_X, SCREEN_X, SET
from domain.collections.matrix_dojo import art as A
from domain.collections.matrix_dojo.palette import C, RAMP
from domain.holidays.pixel import Pix, contrast

KEY = SET.key
HEADER = Header(tone="standard", holiday=KEY)
FLAME, MOON, STRAW, GOLD, LACQUER = (set(RAMP[n]) for n in ("flame", "moon", "straw", "gold", "lacquer"))
RAIN = 'dur="1.54s"'         # the code raining past the round window and the pagoda, by night
CLOUDS = 'dur="53s"'         # the clouds drifting past the round window, by day


class Shared(D.Shared, unittest.TestCase):
    SET = SET
    ART = A
    PIECES = ("byobu", "screen", "pine", "kicker", "guard", "lantern", "window", "chochin", "pagoda_window",
              "pagoda", "tatami", "fallen", "petal_drift", "shimenawa")
    FOOTINGS = ("_footed",)


class Night(unittest.TestCase):
    def test_what_the_night_alone_shows_stays_out_of_the_day_and_the_days_clouds_out_of_the_night(self):
        for code in ("H1", "H2", "H3"):
            day = SET.header(code, HEADER, DAY, True, True)
            night = SET.header(code, HEADER, DARK, True, True)
            self.assertFalse([c for c in FLAME if c in day], (code, "a light burning by day"))
            self.assertFalse([c for c in MOON if c in day], (code, "the moon by day"))
            self.assertNotIn(RAIN, day, (code, "the city's code by day"))
            self.assertTrue([c for c in FLAME if c in night], (code, "the lanterns burn by night"))
            self.assertNotIn(CLOUDS, night, (code, "a cloud by night"))
        day, night = (SET.header("H1", HEADER, theme, True, True) for theme in (DAY, DARK))
        self.assertIn(CLOUDS, day, "the clouds drift past the round window")
        self.assertIn(RAIN, night, "the city's code rains past the round window")
        self.assertTrue([c for c in MOON if c in night], "the moon over the city")
        self.assertIn(RAIN, SET.header("H3", HEADER, DARK, True, True), "and past the pagoda")


class Titles(unittest.TestCase):
    def test_a_title_is_black_lacquer_edged_in_gold_by_day_and_gold_leaf_ringed_in_lacquer_by_night(self):
        day = SET.header("H1", HEADER, DAY, True, True)
        self.assertIn(f'<g stroke="{RAMP["gold"][5]}">', day, "the gold leaf lit along the letters' upper edges")
        self.assertIn(f'<g stroke="{RAMP["gold"][2]}">', day, "and in shade along their lower")
        self.assertIn(f'stroke="{RAMP["lacquer"][1]}"', day, "the letters' black lacquer")
        self.assertRegex(day, r'<path stroke="' + C["paper"] + '"', "the dry brush fraying at a stroke's end")
        night = SET.header("H1", HEADER, DARK, True, True)
        self.assertIn(f'<g stroke="{RAMP["lacquer"][0]}">', night, "the lacquer round the letters in shade")
        self.assertIn(f'<g stroke="{RAMP["lacquer"][2]}">', night, "and lit")
        self.assertRegex(night, r'<pattern id="paleaf\d+n"', "the letters' gold leaf, in bands")


class Motion(unittest.TestCase):
    def test_the_petals_drift_the_fighters_breathe_and_the_code_rains_only_in_a_wide_moving_header(self):
        moving = SET.header("H1", HEADER, DARK, True, True)
        self.assertEqual(moving.count(f'dur="{A.num(A.DRIFT)}s"'), 1, "the petals drift on one of the slow sweeps")
        self.assertEqual(moving.count(f'dur="{A.num(A.LOOP)}s"'), 2, "the fighters' idle, each on its own beat")
        self.assertIn(RAIN, moving)
        for still in (SET.header("H1", HEADER, DARK, True, False), SET.header("H1", HEADER, DARK, False, False)):
            self.assertNotIn("<animate", still)
            self.assertTrue([c for c in FLAME if c in still], "the lanterns still burn, holding still")


class Heroes(unittest.TestCase):
    def test_an_h1_has_the_flying_kick_over_the_byobu_and_the_guard_under_the_round_window(self):
        h, _ = contents(KEY)["kit"]
        for night in (False, True):
            with mock.patch.object(A, "byobu", wraps=A.byobu) as byobu, \
                    mock.patch.object(A, "kicker", wraps=A.kicker) as kicker, \
                    mock.patch.object(A, "guard", wraps=A.guard) as guard, \
                    mock.patch.object(A, "window", wraps=A.window) as window:
                SET.h1(h, night, True)
            (b,), (k,), (g,), (w,) = (m.call_args_list for m in (byobu, kicker, guard, window))
            self.assertLess(b.args[1], 12, "the byobu at the left")
            self.assertTrue(b.args[1] < k.args[1] < b.args[1] + 50, "the fighter in the air over it")
            self.assertGreater(g.args[1], 340, "his opponent at the right")
            self.assertTrue(abs(w.args[1] - g.args[1]) < 30, "under the round window")

    def test_an_h2_has_the_two_fighters_before_the_pine_byobu_at_the_right(self):
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "screen", wraps=A.screen) as screen, \
                        mock.patch.object(A, "kicker", wraps=A.kicker) as kicker, \
                        mock.patch.object(A, "guard", wraps=A.guard) as guard:
                    p, pixels, _ = D.sprites(SET, lambda: SET.h2(h, night, True), "scene")
                if not screen.called:
                    self.assertEqual(name, "most", "only the most a page can say leaves the clash no room")
                    continue
                (s,), (k,), (g,) = (m.call_args_list for m in (screen, kicker, guard))
                x0, top, g_ = s.args[1], s.args[2], s.args[3]
                self.assertTrue(SCREEN_X <= x0 < SCREEN_X + 12, (name, night, x0))
                self.assertEqual(top, 24, (name, night, "from under the rope"))
                self.assertGreaterEqual(g_ - top, 50, (name, night, "risen full height"))
                self.assertTrue(x0 < k.args[1] < g.args[1] < p.w - 20, (name, night, "the kick at the guard"))
                self.assertEqual([xy for xy in pixels if D.near(p, xy, 2)], [], (name, night))

    def test_an_h3_has_the_pagoda_rising_the_strips_full_height(self):
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "pagoda_window", wraps=A.pagoda_window) as window, \
                        mock.patch.object(A, "pagoda", wraps=A.pagoda) as pagoda:
                    p, pixels, _ = D.sprites(SET, lambda: SET.h3(h, night, True), "scene")
                (w,), (pg,) = window.call_args_list, pagoda.call_args_list
                x0, x1, top, g = w.args[1:5]
                self.assertGreaterEqual(x0, PAGODA_X, (name, night))
                self.assertEqual(x1, p.w - 6, (name, night))
                self.assertEqual(top, 24, (name, night, "from under the rope"))
                self.assertGreaterEqual(g - top, 40, (name, night, "the strip's full height"))
                self.assertGreaterEqual(pg.args[3], g - top - 12, (name, night, "the pagoda nearly as tall"))


class Phones(unittest.TestCase):
    def test_a_phones_h1_has_the_whole_dojo_under_its_words(self):
        """A phone's H1 stands the whole dojo across its width under the words, at least 48 rows tall: the byobu
        with the fighter in the air before it, and his opponent before the round window, for every shared
        content."""
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "kicker", wraps=A.kicker) as kicker, \
                        mock.patch.object(A, "guard", wraps=A.guard) as guard:
                    p, pixels, _ = D.sprites(SET, lambda: SET.h1_narrow(h, night), "scene_narrow")
                self.assertTrue(kicker.called and guard.called, (name, night))
                xs, ys = [x for x, _ in pixels], [y for _, y in pixels]
                self.assertLessEqual(min(xs), 6, (name, night))
                self.assertGreaterEqual(max(xs), 173, (name, night))
                self.assertGreaterEqual(max(ys) - min(ys) + 1, 48, (name, night))

    def test_a_phones_h2_and_h3_stand_their_heroes_under_their_words_whatever_they_say(self):
        for code, hero in (("H2", "screen"), ("H3", "pagoda_window")):
            self.assertEqual(SET.phone_rows(code, 0), SET.phone_rows(code, 400), code)
            for name, (h, _) in contents(KEY).items():
                for night in (False, True):
                    with mock.patch.object(A, hero, wraps=getattr(A, hero)) as drawn:
                        p, pixels, _ = D.sprites(SET, lambda: D.phone(SET, code)(h, night), "scene_under")
                    self.assertTrue(drawn.called, (code, name, night))
                    ys = [y for _, y in pixels]
                    self.assertGreaterEqual(max(ys) - min(ys) + 1, 48, (code, name, night))


class Footers(unittest.TestCase):
    def test_every_footer_stands_on_the_dojos_floor_with_the_alcove_after_its_last_cell(self):
        """Every footer stands on the dojo's floor, the rush of the tatami with its brocade edge along its foot,
        and on a title block whose cells leave it room the alcove, a hanging scroll between two paper lanterns,
        after its last cell; the lanterns burn by night."""
        h, f = contents(KEY)["repository"]
        for night in (False, True):
            with mock.patch.object(A, "kakejiku", wraps=A.kakejiku) as scroll, \
                    mock.patch.object(A, "chochin", wraps=A.chochin) as lanterns:
                p = SET.f1(f, night)
            (call,) = scroll.call_args_list
            self.assertGreater(call.args[1], max(b[2] for b in p.words), "after the last cell")
            self.assertEqual(len(lanterns.call_args_list), 2, "a paper lantern either side")
            self.assertEqual(bool(D.flickering(p)), False, "a footer holds still")
            self.assertEqual(bool([c for c in p.layers["base"].values() if c in FLAME]), night, "lit by night")
            rush = set(RAMP["tatami"])
            for draw in (SET.f1, SET.f2, SET.f1_narrow, SET.f2_narrow):
                q = draw(f, night)
                floor = [x for x in range(8, q.w - 8) if any(q.layers["base"].get((x, y)) in rush
                                                             for y in range(q.h - 6, q.h - 1))]
                self.assertGreater(len(floor), q.w // 2, (draw.__name__, night, "the tatami's rush"))


class Links(unittest.TestCase):
    def test_a_link_button_hangs_a_straw_rope_along_its_top_and_takes_its_own_sprite(self):
        for night in (False, True):
            for i in range(4):
                p = SET.link_button("Docs", i, night)
                rows = {c for (x, y), c in p.layers["base"].items() if y in (0, 1)}
                self.assertTrue(rows and rows <= STRAW, (night, i, rows - STRAW))
        sprites = [tuple(SET.link_icon(i, False, C["white"])[0]) for i in range(4)]
        self.assertEqual(len(set(sprites)), 4, "four sprites of their own")


class Badges(unittest.TestCase):
    def test_a_straw_rope_lies_along_every_badges_top_two_rows_with_the_letters_under_it(self):
        for style in BADGE_STYLES:
            drawn = [SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                       SET.badge_states()["green"])]
            drawn += [SET.plate_badge(style, "License", "MIT", "scale", mode) for mode in ("day", "night")]
            for p in drawn:
                rows = {c for (x, y), c in p.layers["base"].items() if y in (0, 1)}
                self.assertTrue(rows and rows <= STRAW, (style, rows - STRAW))
                self.assertTrue(all(y >= TOP for _, _, _, y, _ in p.uses["base"]), "the letters sit under the rope")

    def test_a_counters_numerals_hold_4_5_on_their_name_plates(self):
        for night in (False, True):
            q = Pix(20, 20)
            SET.counter_cell(q, 2, 2, night)
            face = q.layers["base"][(7, 8)]
            self.assertGreaterEqual(contrast(SET.counter_ink(night, False), face), 4.5, night)
            self.assertGreaterEqual(contrast(SET.counter_ink(night, True), face), 2.0, night)


class Games(unittest.TestCase):
    def test_the_boards_and_the_podium_are_the_dojos_own_stuffs(self):
        own = set(SET.tokens) - set(SET.hand.tokens)
        for night in (False, True):
            light, dark = SET.game_squares(night)
            frame, style = SET.game_frame(night)
            podium = SET.game_podium(night)
            for stuff in (light, dark, frame, podium.stuff, podium.trim):
                self.assertIsInstance(stuff, Stuff)
                self.assertTrue({c.upper() for c in stuff.ramp} <= own, (night, stuff.base))
            self.assertEqual((light.grain, dark.grain), ("weave", "satin"), "tatami and lacquer")
            self.assertIn(podium.style, PODIUMS)
            self.assertEqual((podium.stuff.base, podium.stuff.grain, podium.style), (RAMP["lacquer"][2], "satin",
                                                                                     "banners"))


if __name__ == "__main__":
    unittest.main()
