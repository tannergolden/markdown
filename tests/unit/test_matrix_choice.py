# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Choice design's tests: the checks every design of a collection shares, run over Choice, and its own rules,
which the shared checks cannot know: what the night alone shows (the lamp, the fire and the candles burning the hand's
phosphor, the lightning, the code falling through the cracked mirror) stays out of the day's files, and the day's grey
storm out of the night's; a title is glossy gel capsules of candy red, streaked white by day and with the lamp's green
by night; the lightning strikes, the code falls, the rain runs down the glass, the umbrella drips and the cheval glass
ripples each on its own cadence, and only in a wide moving header; each header's hero stands where it should, the
wingback under the mirror and the window in the storm on an H1, the fireside at the right with a club chair either
side facing the other and the pier mirror rising over the mantel on an H2, and the cheval glass rising the strip's
full height on an H3; a phone's H1 holds the whole room under its words, and its H2 and H3 their heroes whatever the
words say; every footer stands on a mahogany skirting, with the open box and the two pills after a title block's last
cell and the banker's lamp lit beside it by night; a link button is nailed in brass along its top and each of the six
takes its own sprite; a badge's top two rows are nailed leather; a counter's numerals hold 4.5:1 on their cells; and
the games' boards and podium are the room's own stuffs."""
from __future__ import annotations

import unittest
from unittest import mock

from tests.unit import design_checks as D
from tests.unit.test_holiday_sets import contents

from domain.banners.content import Header
from domain.canvas import DARK, DAY
from domain.holidays.designs.badges import STYLES as BADGE_STYLES, TOP
from domain.holidays.designs.materials import PODIUMS, Stuff
from domain.collections.matrix_choice import SET
from domain.collections.matrix_choice import art as A
from domain.collections.matrix_choice.palette import C, RAMP
from domain.holidays.pixel import Pix, contrast

KEY = SET.key
HEADER = Header(tone="standard", holiday=KEY)
FLAME, STORM, OX, BRASS, WOOD = (RAMP[n] for n in ("flame", "storm", "oxblood", "brass", "mahogany"))
STRIKE = f'dur="{A.num(A.STRIKE)}s"'     # the lightning, by night


class Shared(D.Shared, unittest.TestCase):
    SET = SET
    ART = A
    PIECES = ("room", "storm_window", "suitcase", "umbrella", "mirror", "fireplace", "club_chair", "tea_table",
              "cheval")
    FOOTINGS = ("_footed",)


class Night(unittest.TestCase):
    def test_what_the_night_alone_shows_stays_out_of_the_day_and_the_days_storm_out_of_the_night(self):
        """By day no light burns, no lightning strikes and no code falls in the mirror; by night the lamp, the fire
        and the candles burn the hand's phosphor, and the storm outside is the night's, not the day's grey."""
        for code in ("H1", "H2", "H3"):
            for wide, motion in ((True, True), (True, False), (False, False)):
                day = SET.header(code, HEADER, DAY, wide, motion)
                night = SET.header(code, HEADER, DARK, wide, motion)
                what = (code, wide, motion)
                self.assertEqual([c for c in (FLAME[5], FLAME[6]) if c in day], [], what)
                self.assertNotIn(STRIKE, day, what)
                self.assertNotIn('id="mc"', day, what)
                self.assertIn(FLAME[6] if code != "H3" or not wide else FLAME[5], night, what)
                if code != "H3":
                    self.assertEqual([c for c in STORM[3:] if c in night], [], (what, "the day's grey storm"))
        night = SET.header("H1", HEADER, DARK, True, True)
        self.assertIn('id="mc"', night, "the code falling through the mirror")
        self.assertIn(STRIKE, night, "the lightning")


class Titles(unittest.TestCase):
    def test_a_title_is_glossy_gel_capsules_streaked_white_by_day_and_green_by_night(self):
        day = SET.header("H1", HEADER, DAY, True, False)
        night = SET.header("H1", HEADER, DARK, True, False)
        for svg in (day, night):
            self.assertIn(f'<g stroke="{RAMP["candy"][0]}"', svg, "the gel's rim")
            self.assertRegex(svg, r'<g mask="url\(#pc\d+\)">', "the gel laid inside the letters")
        self.assertIn(f'<g stroke="{C["white"]}">', day, "the white streak of light")
        self.assertIn(f'<g stroke="{FLAME[6]}">', night, "the lamp's green streak")


class Motion(unittest.TestCase):
    def test_the_lightning_the_code_the_rain_the_drips_and_the_glass_move_each_on_its_cadence(self):
        """By night in a wide moving H1 the lightning strikes every 9 seconds and the code steps down the mirror a
        glyph every 0.12; by day the umbrella drips every 3.6; the cheval glass ripples every 2.5 on an H3. A still
        file and a phone move not at all."""
        night = SET.header("H1", HEADER, DARK, True, True)
        self.assertIn(STRIKE, night)
        self.assertRegex(night, r'<g clip-path="url\(#mc\)"><g>.*?dur="[\d.]+s"', "the code falling")
        self.assertIn('dur="3.6s"', SET.header("H1", HEADER, DAY, True, True), "the umbrella's drips")
        self.assertIn('dur="2.5s"', SET.header("H3", HEADER, DAY, True, True), "the glass going to liquid")
        for code in ("H1", "H2", "H3"):
            for wide in (True, False):
                self.assertNotIn("<animate", SET.header(code, HEADER, DARK, wide, False), (code, wide))


class Heroes(unittest.TestCase):
    def test_an_h1_has_the_wingback_at_the_left_and_the_window_at_the_right(self):
        h, _ = contents(KEY)["kit"]
        for night in (False, True):
            with mock.patch.object(A, "room", wraps=A.room) as room, \
                    mock.patch.object(A, "storm_window", wraps=A.storm_window) as window:
                SET.h1(h, night, True)
            (r,), (w,) = room.call_args_list, window.call_args_list
            self.assertLess(r.args[1], 12, (night, "the chair at the left"))
            self.assertGreater(w.args[1], 350, (night, "the window at the right"))

    def test_an_h2_has_the_fireside_with_a_chair_either_side_facing_the_other(self):
        """Wherever the words leave it room, an H2 stands the fireside at the right: the fireplace with its pier
        mirror rising over the mantel nearly to the tufted panel, a club chair either side facing the other across
        the hearth, and the low table with the glass and the two pills between them."""
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "fireplace", wraps=A.fireplace) as fireplace, \
                        mock.patch.object(A, "club_chair", wraps=A.club_chair) as chairs, \
                        mock.patch.object(A, "tea_table", wraps=A.tea_table) as table:
                    p = SET.h2(h, night, True)
                if not fireplace.called:
                    self.assertEqual(name, "most", "only the most a page can say leaves the fireside no room")
                    continue
                (fp,) = fireplace.call_args_list
                self.assertGreaterEqual(fp.args[1], 330, (name, night))
                self.assertLessEqual(fp.kwargs["top"], A.BAND + 6, (name, night, "the mirror risen the full height"))
                facing = sorted(c.kwargs["right"] for c in chairs.call_args_list)
                self.assertEqual(facing, [False, True], (name, night, "a chair either side, facing in"))
                self.assertTrue(table.called, (name, night))

    def test_an_h3_has_the_cheval_glass_rising_the_strips_full_height(self):
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "cheval", wraps=A.cheval) as cheval:
                    p = SET.h3(h, night, True)
                (call,) = cheval.call_args_list
                x0, g, top = call.args[1], call.args[2], call.args[5]
                self.assertEqual(x0 + 26, p.w - A.EDGE - 1, (name, night, "at the right"))
                self.assertLessEqual(top, A.BAND + 6, (name, night, "from under the tufted panel"))
                self.assertGreaterEqual(g - top, 50, (name, night, "the strip's full height"))


class Phones(unittest.TestCase):
    def test_a_phones_h1_has_the_whole_room_under_its_words(self):
        """A phone's H1 stands the whole room across its width under the words, at least 48 rows tall: the wingback
        and its lamp at the left and the window in the storm at the right, for every shared content."""
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "room", wraps=A.room) as room, \
                        mock.patch.object(A, "storm_window", wraps=A.storm_window) as window:
                    p, pixels, _ = D.sprites(SET, lambda: SET.h1_narrow(h, night), "scene_narrow")
                self.assertTrue(room.called and window.called, (name, night))
                xs, ys = [x for x, _ in pixels], [y for _, y in pixels]
                self.assertLessEqual(min(xs), 6, (name, night))
                self.assertGreaterEqual(max(xs), 173, (name, night))
                self.assertGreaterEqual(max(ys) - min(ys) + 1, 48, (name, night))

    def test_a_phones_h2_and_h3_stand_their_heroes_under_their_words_whatever_they_say(self):
        for code, hero in (("H2", "fireplace"), ("H3", "cheval")):
            self.assertEqual(SET.phone_rows(code, 0), SET.phone_rows(code, 400), code)
            for name, (h, _) in contents(KEY).items():
                for night in (False, True):
                    with mock.patch.object(A, hero, wraps=getattr(A, hero)) as drawn:
                        p, pixels, _ = D.sprites(SET, lambda: D.phone(SET, code)(h, night), "scene_under")
                    self.assertTrue(drawn.called, (code, name, night))
                    ys = [y for _, y in pixels]
                    self.assertGreaterEqual(max(ys) - min(ys) + 1, 44, (code, name, night))


class Footers(unittest.TestCase):
    def test_every_footer_stands_on_the_skirting_with_the_pills_after_its_last_cell_and_the_lamp_lit_by_night(self):
        """Every footer stands on a skirting of mahogany along its foot, along more than half its width where its
        cells leave the foot free (a phone's title block, whose last cells come down to the roll, between them), and
        on a title block whose cells leave it room the open box with the two pills stands on it after the last cell,
        the banker's lamp beside it burning the hand's phosphor by night."""
        _, f = contents(KEY)["repository"]
        for night in (False, True):
            with mock.patch.object(A, "pill_box", wraps=A.pill_box) as box, \
                    mock.patch.object(A, "lamp_mark", wraps=A.lamp_mark) as lamp:
                p = SET.f1(f, night)
            (call,) = box.call_args_list
            self.assertGreater(call.args[1], max(b[2] for b in p.words), (night, "after the last cell"))
            self.assertTrue(lamp.called, night)
            lit = [c for L in p.layers.values() for c in L.values() if c == FLAME[6]]
            self.assertEqual(bool(lit), night, (night, "the lamp lit by night"))
            wood = set(WOOD)
            for draw, most in ((SET.f1, 2), (SET.f2, 2), (SET.f2_narrow, 2), (SET.f1_narrow, 9)):
                q = draw(f, night)
                skirting = [x for x in range(8, q.w - 8) if any(q.layers["base"].get((x, y)) in wood
                                                                for y in range(q.h - 12, q.h - 4))]
                self.assertGreater(len(skirting), q.w // most, (draw.__name__, night, "the skirting along the foot"))


class Links(unittest.TestCase):
    def test_a_link_button_is_nailed_in_brass_along_its_top_and_takes_its_own_sprite(self):
        for night in (False, True):
            p = SET.link_button("Docs", 0, night)
            heads = [x for (x, y), c in p.layers["base"].items() if y == 4 and c == BRASS[5 if night else 6]]
            self.assertGreaterEqual(len(heads), 4, (night, "brass nails along the top"))
        sprites = [tuple(SET.link_icon(i, False, C["white"])[0]) for i in range(6)]
        self.assertEqual(len(set(sprites)), 6, "six sprites of their own")


class Badges(unittest.TestCase):
    def test_nailed_leather_lies_along_every_badges_top_two_rows_with_the_letters_under_it(self):
        leather = set(OX) | set(BRASS)
        for style in BADGE_STYLES:
            drawn = [SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                       SET.badge_states()["green"])]
            drawn += [SET.plate_badge(style, "License", "MIT", "scale", mode) for mode in ("day", "night")]
            for p in drawn:
                rows = {c for (x, y), c in p.layers["base"].items() if y in (0, 1)}
                self.assertTrue(rows and rows <= leather, (style, rows - leather))
                self.assertTrue(all(y >= TOP for _, _, _, y, _ in p.uses["base"]), "the letters sit under the band")

    def test_a_counters_numerals_hold_4_5_on_their_cells(self):
        for night in (False, True):
            q = Pix(20, 20)
            SET.counter_cell(q, 2, 2, night)
            face = q.layers["base"][(7, 8)]
            self.assertGreaterEqual(contrast(SET.counter_ink(night, False), face), 4.5, night)
            self.assertGreaterEqual(contrast(SET.counter_ink(night, True), face), 2.0, night)


class Games(unittest.TestCase):
    def test_the_boards_and_the_podium_are_the_rooms_own_stuffs(self):
        own = set(SET.tokens) - set(SET.hand.tokens)
        for night in (False, True):
            light, dark = SET.game_squares(night)
            frame, style = SET.game_frame(night)
            podium = SET.game_podium(night)
            for stuff in (light, dark, frame, podium.stuff, podium.trim):
                self.assertIsInstance(stuff, Stuff)
                self.assertTrue({c.upper() for c in stuff.ramp} <= own, (night, stuff.base))
            self.assertEqual((light.grain, dark.grain, style), ("satin", "stitch", "wood"), "satin, leather, wood")
            self.assertIn(podium.style, PODIUMS)
            self.assertEqual((podium.stuff.base, podium.stuff.grain, podium.style), (OX[3], "stitch", "ribbon"))


if __name__ == "__main__":
    unittest.main()
