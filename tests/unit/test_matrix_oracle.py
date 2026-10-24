# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Oracle design's tests: the checks every design of a collection shares, run over Oracle, and its own rules,
which the shared checks cannot know: the window shows the hazy city by day and the code falling past it by night, and
the wallpaper's warm dark is the night's alone; a title is baked as cookies, its rim dark and its depth brown by day,
and caught by the oven's green light by night, the move a game letters appearing with its rim; the steam rises and the
child bends his spoon on their own loops on an H1, the vase tips off the table on an H2, all in a wide moving header
only; each header's hero stands where it should, the kitchen at the left and the room beyond at the right on an H1,
the dresser wall at the right, risen the full height, on an H2, and the refrigerator's corner at the right, the
strip's full height, on an H3; a phone's H1 holds the whole kitchen under its words and its H2 and H3 stand their
heroes under theirs; every footer stands on the kitchen's linoleum, with the kitchen's corner after a title block's
last cell, its night light burning by night; a link button is iced along its top and each of the four takes its own
sprite; a badge's top two rows are a jar's gingham cap; a counter's numerals hold 4.5:1 on their tile; and the
games' boards and podium are the kitchen's own stuffs."""
from __future__ import annotations

import unittest
from unittest import mock

from tests.unit import design_checks as D
from tests.unit.test_holiday_sets import contents

from domain.banners.content import Header
from domain.canvas import DARK, DAY
from domain.collections.matrix_oracle import SET
from domain.collections.matrix_oracle import art as A
from domain.collections.matrix_oracle.palette import C, NIGHT_SKY, RAMP
from domain.holidays.designs.badges import STYLES as BADGE_STYLES, TOP
from domain.holidays.designs.materials import PODIUMS, Stuff
from domain.holidays.pixel import Pix, contrast

KEY = SET.key
HEADER = Header(tone="standard", holiday=KEY)
FLAME, CHOC, GLAZE, BLUE, RED = (set(RAMP[n]) for n in ("flame", "choc", "glaze", "blue", "red"))


def dur(seconds: float) -> str:
    return f'dur="{A.num(seconds)}s"'


class Shared(D.Shared, unittest.TestCase):
    SET = SET
    ART = A
    PIECES = ("kitchen", "oven", "hood", "window", "counter", "room", "doorway", "child", "cat_walk", "blocks",
              "dresser_wall", "dresser", "kitchen_table", "pendant", "fridge_corner", "fridge", "vapour")
    FOOTINGS = ("_footed",)


class Night(unittest.TestCase):
    def test_the_window_shows_the_city_by_day_and_the_code_falling_past_it_by_night(self):
        h, _ = contents(KEY)["kit"]
        for night in (False, True):
            with mock.patch.object(A.rain, "Rain", wraps=A.rain.Rain) as code:
                svg = SET.header("H1", HEADER, DARK if night else DAY, True, True)
            self.assertEqual(code.called, night, "the code falls past the window by night only")
            self.assertEqual(bool([c for c in RAMP["sky"] if c in svg]), not night, "the city by day only")

    def test_the_wallpapers_warm_dark_is_the_nights_alone(self):
        for code in ("H1", "H2", "H3"):
            day = SET.header(code, HEADER, DAY, True, True)
            night = SET.header(code, HEADER, DARK, True, True)
            self.assertIn(C["paper"], day, code)
            self.assertFalse([c for c in NIGHT_SKY if c in day], code)
            self.assertNotIn(C["paper"], night, code)
            self.assertTrue([c for c in NIGHT_SKY if c in night], code)


class Titles(unittest.TestCase):
    def test_a_title_is_baked_as_cookies_dark_rimmed_by_day_and_caught_by_the_ovens_light_by_night(self):
        for night in (False, True):
            p = Pix(200, 60)
            A.cookie_title(p, 10, 10, "BANNERS", night, 3)
            rim = {stroke for stroke, *_ in p.uses["dough"]}
            want = {RAMP["dough"][0], RAMP["dough"][1]} if night else {RAMP["paper"][2], RAMP["choc"][2]}
            self.assertEqual(rim, want, night)
            face = {stroke for stroke, *_ in p.uses["base"]}
            self.assertTrue(all(s.startswith("url(#") for s in face), "the dough studded with chips, as a paint")
            glow = {stroke.split(":")[0] for stroke, *_ in p.uses["haze"]}
            self.assertEqual(RAMP["flame"][3] in glow, night, "the oven's green glow round the letters by night")

    def test_a_move_appears_with_the_rim_it_is_baked_with(self):
        p = Pix(200, 60)
        p.layer("sec1", ("once", "", ""), z=0.6)
        with p.onto("sec1"):
            A.cookie_title(p, 10, 10, "21. Nd6+", False, 2)
        self.assertTrue(p.uses.get("sec1dough"), "the rim appears with the move")
        self.assertFalse(p.uses.get("dough"), "and never before it")


class Motion(unittest.TestCase):
    def test_the_steam_rises_the_spoon_bends_and_the_vase_tips_only_in_a_wide_moving_header(self):
        h1 = SET.header("H1", HEADER, DAY, True, True)
        self.assertIn(dur(A.STEAM_LOOP), h1, "the steam off the tray and the mug")
        self.assertIn(dur(A.BEND_LOOP), h1, "the spoon bending")
        self.assertIn(dur(A.FALL_LOOP), SET.header("H2", HEADER, DAY, True, True), "the vase tipping off the table")
        for code in ("H1", "H2", "H3"):
            for still in (SET.header(code, HEADER, DARK, True, False), SET.header(code, HEADER, DARK, False, False)):
                self.assertNotIn("<animate", still, code)


class Heroes(unittest.TestCase):
    def test_an_h1_has_the_kitchen_at_the_left_and_the_room_beyond_at_the_right(self):
        h, _ = contents(KEY)["kit"]
        for night in (False, True):
            with mock.patch.object(A, "kitchen", wraps=A.kitchen) as kitchen, \
                    mock.patch.object(A, "room", wraps=A.room) as room, \
                    mock.patch.object(A, "child", wraps=A.child) as child:
                SET.h1(h, night, True)
            (k,), (r,) = kitchen.call_args_list, room.call_args_list
            self.assertLess(k.args[1], 10, "the kitchen at the left")
            self.assertGreater(r.args[1], 350, "the room beyond at the right")
            self.assertTrue(child.called, "the child bending his spoon")

    def test_an_h2_has_the_dresser_wall_at_the_right_risen_the_full_height(self):
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "dresser_wall", wraps=A.dresser_wall) as wall:
                    p, pixels, _ = D.sprites(SET, lambda: SET.h2(h, night, True), "scene")
                if not wall.called:
                    self.assertEqual(name, "most", "only the most a page can say leaves the dresser no room")
                    continue
                (call,) = wall.call_args_list
                x0, g, top = call.args[1], call.args[3], call.args[6]
                self.assertTrue(308 <= x0 < 330, (name, night, x0))
                self.assertLessEqual(top, A.TOP + 3, (name, night, "from under the rail"))
                self.assertGreaterEqual(g - top, 80, (name, night, "risen the full height"))
                self.assertEqual([xy for xy in pixels if D.near(p, xy, 2)], [], (name, night))

    def test_an_h3_has_the_refrigerators_corner_at_the_right_the_strips_full_height(self):
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "fridge_corner", wraps=A.fridge_corner) as corner:
                    SET.h3(h, night, True)
                (call,) = corner.call_args_list
                x0, g, top = call.args[1], call.args[3], call.args[6]
                self.assertGreaterEqual(x0, 352, (name, night))
                self.assertEqual(top, A.TOP + 3, (name, night, "from under the rail"))
                self.assertGreaterEqual(g - top, 45, (name, night, "the strip's full height"))


class Phones(unittest.TestCase):
    def test_a_phones_h1_has_the_whole_kitchen_under_its_words(self):
        """A phone's H1 stands the whole kitchen across its width under the words, at least 48 rows tall: the range
        and the counter at the left, the table in the middle and the doorway with the child at the right, for every
        shared content."""
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "kitchen", wraps=A.kitchen) as kitchen, \
                        mock.patch.object(A, "room", wraps=A.room) as room:
                    p, pixels, _ = D.sprites(SET, lambda: SET.h1_narrow(h, night), "scene_narrow")
                self.assertTrue(kitchen.called and room.called, (name, night))
                xs, ys = [x for x, _ in pixels], [y for _, y in pixels]
                self.assertLessEqual(min(xs), 6, (name, night))
                self.assertGreaterEqual(max(xs), 170, (name, night))
                self.assertGreaterEqual(max(ys) - min(ys) + 1, 48, (name, night))

    def test_a_phones_h2_and_h3_stand_their_heroes_under_their_words_whatever_they_say(self):
        for code, hero in (("H2", "dresser_wall"), ("H3", "fridge_corner")):
            self.assertEqual(SET.phone_rows(code, 0), SET.phone_rows(code, 400), code)
            for name, (h, _) in contents(KEY).items():
                for night in (False, True):
                    with mock.patch.object(A, hero, wraps=getattr(A, hero)) as drawn:
                        p, pixels, _ = D.sprites(SET, lambda: D.phone(SET, code)(h, night), "scene_under")
                    self.assertTrue(drawn.called, (code, name, night))
                    ys = [y for _, y in pixels]
                    self.assertGreaterEqual(max(ys) - min(ys) + 1, 48, (code, name, night))


class Footers(unittest.TestCase):
    def test_every_footer_stands_on_the_linoleum_with_the_kitchens_corner_after_its_last_cell(self):
        """Every footer stands on the kitchen's linoleum along its foot, and on a title block whose cells leave it
        room the kitchen's corner, the cabinet with the jar and the mug and the cat beside it, after its last cell;
        by night the night light over it burns and flickers on the hand's flame."""
        h, f = contents(KEY)["repository"]
        lino = {RAMP["glaze"][5], RAMP["blue"][5], RAMP["glaze"][1], RAMP["blue"][1]}
        for night in (False, True):
            with mock.patch.object(A, "sitter", wraps=A.sitter) as cat, \
                    mock.patch.object(A, "jar", wraps=A.jar) as jar:
                p = SET.f1(f, night)
            self.assertTrue(cat.called and jar.called, night)
            self.assertGreater(jar.call_args.args[1], max(b[2] for b in p.words), "after the last cell")
            lit = D.flickering(p)
            self.assertEqual(bool(lit), night, "the night light flickers by night")
            self.assertTrue(lit <= FLAME, lit - FLAME)
            for draw in (SET.f1, SET.f2, SET.f1_narrow, SET.f2_narrow):
                q = draw(f, night)
                foot = [(x, y) for x in range(A.EDGE, q.w - A.EDGE) for y in range(q.h - A.EDGE - 3, q.h - A.EDGE)
                        if q.layers["base"].get((x, y)) in lino]
                self.assertGreaterEqual(len(foot), q.w // 2, (draw.__name__, night, "the linoleum"))


class Links(unittest.TestCase):
    def test_a_link_button_is_iced_along_its_top_and_takes_its_own_sprite(self):
        for night in (False, True):
            for i in range(4):
                p = SET.link_button("Docs", i, night)
                top = [x for x in range(p.w) if p.layers["base"].get((x, 3)) in CHOC]
                self.assertGreater(len(top), p.w - 6, (night, i, "the icing along its top"))
                self.assertFalse([1 for x in range(15, p.w - 6) if p.layers["base"].get((x, 4)) in CHOC],
                                 (night, i, "and none on its letters"))
        sprites = [tuple(SET.link_icon(i, False, C["white"])[0]) for i in range(4)]
        self.assertEqual(len(set(sprites)), 4, "four sprites of their own")


class Badges(unittest.TestCase):
    def test_a_jars_gingham_cap_lies_along_every_badges_top_two_rows_with_the_letters_under_it(self):
        cloth = RED | GLAZE
        for style in BADGE_STYLES:
            drawn = [SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                       SET.badge_states()["green"])]
            drawn += [SET.plate_badge(style, "License", "MIT", "scale", mode) for mode in ("day", "night")]
            for p in drawn:
                rows = {c for (x, y), c in p.layers["base"].items() if y in (0, 1)}
                self.assertTrue(rows and rows <= cloth, (style, rows - cloth))
                self.assertTrue(all(y >= TOP for _, _, _, y, _ in p.uses["base"]), "the letters sit under the cap")

    def test_a_counters_numerals_hold_4_5_on_their_tile(self):
        for night in (False, True):
            q = Pix(20, 20)
            SET.counter_cell(q, 2, 2, night)
            face = q.layers["base"][(7, 8)]
            self.assertGreaterEqual(contrast(SET.counter_ink(night, False), face), 4.5, night)
            self.assertGreaterEqual(contrast(SET.counter_ink(night, True), face), 2.0, night)


class Games(unittest.TestCase):
    def test_the_boards_and_the_podium_are_the_kitchens_own_stuffs(self):
        own = set(SET.tokens) - set(SET.hand.tokens)
        for night in (False, True):
            light, dark = SET.game_squares(night)
            frame, style = SET.game_frame(night)
            podium = SET.game_podium(night)
            for stuff in (light, dark, frame, podium.stuff, podium.trim):
                self.assertIsInstance(stuff, Stuff)
                self.assertTrue({c.upper() for c in stuff.ramp} <= own, (night, stuff))
            self.assertEqual((light.ramp, dark.ramp), (RAMP["glaze"], RAMP["blue"]), "the tiles, cream and Delft")
            self.assertIn(podium.style, PODIUMS)
            self.assertEqual((podium.stuff.ramp, podium.stuff.grain, podium.style), (RAMP["choc"], "satin", "lace"))


if __name__ == "__main__":
    unittest.main()
