# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Exit design's tests: the checks every design of a collection shares, run over Exit, and its own rules, which
the shared checks cannot know: the neon burns only by night, white-hot at its cores, and stands unlit by day; a title
is a sign of glass tubes on a dark board, pale glass by day and the hand's phosphor by night, and a move on a game's
sheet is lettered in the tubes without the board; the rain falls, the payphone rings, its handset swings, the steam
breathes and the drops ring out in the puddles on the rule each on its own cadence, and only in a wide moving header;
each header's hero stands where it should, the booth and the tenement on an H1, the booth answered under the
streetlamp beside a pillar of the El rising from the girder on an H2, and the hotel's corner rising the strip's full
height on an H3; a phone's H1 holds the whole street under its words, and its H2 and H3 their heroes whatever the words
say; every footer stands on the El's girder, with the booth after a title block's last cell, lit by night; a link
button is riveted along its top and each of the six takes its own sprite; a badge's top two rows are riveted iron; a
counter's numerals hold 4.5:1 on their boards; and the games' boards and podium are the street's own stuffs."""
from __future__ import annotations

import unittest
from unittest import mock

from tests.unit import design_checks as D
from tests.unit.test_holiday_sets import contents

from domain.banners.content import Header
from domain.canvas import DARK, DAY
from domain.holidays.designs.badges import STYLES as BADGE_STYLES, TOP
from domain.holidays.designs.materials import PODIUMS, Stuff
from domain.collections.matrix_exit import SET
from domain.collections.matrix_exit import art as A
from domain.collections.matrix_exit.palette import C, RAMP
from domain.holidays.pixel import Pix, contrast

KEY = SET.key
HEADER = Header(tone="standard", holiday=KEY)
FLAME, IRON, TUBE, BOARD = (RAMP[n] for n in ("flame", "iron", "tube", "board"))
NIGHT_ONLY = (FLAME[6], FLAME[3])        # the neon's white-hot core and the glow it throws


class Shared(D.Shared, unittest.TestCase):
    SET = SET
    ART = A
    PIECES = ("corner", "tenement", "steam", "hydrant", "signal", "street", "reflections", "callbox", "booth",
              "agent", "pillar", "hotel", "hotel_sign", "fire_escape")
    FOOTINGS = ("_footed",)


class Night(unittest.TestCase):
    def test_the_neon_burns_only_by_night_and_stands_unlit_by_day(self):
        """No neon burns by day, its white-hot cores and their glow kept to the night's files, wide and on a phone;
        by night every header burns them."""
        for code in ("H1", "H2", "H3"):
            for wide, motion in ((True, True), (True, False), (False, False)):
                day = SET.header(code, HEADER, DAY, wide, motion)
                night = SET.header(code, HEADER, DARK, wide, motion)
                self.assertEqual([c for c in NIGHT_ONLY if c in day], [], (code, wide, motion))
                self.assertIn(FLAME[6], night, (code, wide, motion))


class Titles(unittest.TestCase):
    def test_a_title_is_a_sign_of_glass_tubes_on_a_dark_board(self):
        """By day the tubes are pale glass, by night they burn the hand's phosphor with their glow round them; the
        board of dark enamel stands behind them either way."""
        day = SET.header("H1", HEADER, DAY, True, False)
        night = SET.header("H1", HEADER, DARK, True, False)
        for svg in (day, night):
            self.assertIn(f'fill="{BOARD[0]}"', svg, "the board's rim")
        self.assertIn(TUBE[6], day, "the glass catching the light")
        self.assertIn(TUBE[3], day, "the unlit glass")
        self.assertIn(f'stroke="{FLAME[3]}" stroke-opacity=".55"', night, "the tubes' glow on the board")

    def test_a_move_is_lettered_in_the_tubes_without_the_board(self):
        """A game's last move and the Hall's totals are words of the sheet, not its title: lettered without the
        board, in the board's black by day and in the burning tubes by night."""
        for night in (False, True):
            p = Pix(120, 40)
            w = SET.game_title(p, 10, 10, "21. Nd6+", night, 2)
            self.assertGreater(w, 40)
            self.assertEqual(p.shapes.get("board", []), [], (night, "no board"))
            self.assertEqual(p.words[-1], (9, 9, 11 + w, 25), night)
        svg = Pix(120, 40)
        SET.game_title(svg, 10, 10, "12", True, 3)
        self.assertTrue(any(key[0] == "tube" for key in svg.syms), "the tubes by night")


class Motion(unittest.TestCase):
    def test_the_rain_the_ringing_the_swing_the_steam_and_the_drops_move_each_on_its_cadence(self):
        """In a wide moving H1 the rain falls every 1.2 seconds, the payphone rings every second, its handset swings
        every 1.6 and the steam breathes every 2.4; on an H2 the drops ring out in the puddles on the rule every 1.8
        and the wet street ripples every half second. A still file and a phone move not at all."""
        h1 = SET.header("H1", HEADER, DARK, True, True)
        for dur in ("1.2", "1", "1.6", "2.4"):
            self.assertIn(f'dur="{dur}s"', h1, dur)
        h2 = SET.header("H2", HEADER, DAY, True, True)
        for dur in ("1.2", "1.8", ".5"):
            self.assertIn(f'dur="{dur}s"', h2, dur)
        for code in ("H1", "H2", "H3"):
            for wide in (True, False):
                self.assertNotIn("<animate", SET.header(code, HEADER, DARK, wide, False), (code, wide))


class Heroes(unittest.TestCase):
    def test_an_h1_has_the_booth_at_the_left_and_the_tenement_at_the_right(self):
        h, _ = contents(KEY)["kit"]
        for night in (False, True):
            with mock.patch.object(A, "corner", wraps=A.corner) as corner, \
                    mock.patch.object(A, "tenement", wraps=A.tenement) as tenement:
                SET.h1(h, night, True)
            (c,), (t,) = corner.call_args_list, tenement.call_args_list
            self.assertLess(c.args[1], 12, (night, "the corner at the left"))
            self.assertGreater(t.args[1], 330, (night, "the tenement at the right"))

    def test_an_h2_has_the_booth_answered_beside_a_pillar_rising_from_the_girder(self):
        """Wherever the words leave it room, an H2 stands the booth answered at the right, the streetlamp over it
        and a pillar of the El rising from the girder's foot to the kerb, risen the full height."""
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "callbox", wraps=A.callbox) as callbox, \
                        mock.patch.object(A, "booth", wraps=A.booth) as booth, \
                        mock.patch.object(A, "pillar", wraps=A.pillar) as pillar:
                    p = SET.h2(h, night, True)
                if not callbox.called:
                    self.assertEqual(name, "most", "only the most a page can say leaves the booth no room")
                    continue
                (cb,) = callbox.call_args_list
                x0, x1, g = cb.args[1:4]
                self.assertGreaterEqual(x0, 296, (name, night))
                self.assertEqual(x1, p.w - A.EDGE - 1, (name, night))
                self.assertTrue(booth.call_args.kwargs.get("answered"), (name, night, "someone at the phone"))
                if pillar.called:
                    self.assertEqual(pillar.call_args.args[2], A.GIRDER, (name, night, "from the girder"))
                self.assertGreaterEqual(g - A.GIRDER, 56, (name, night, "risen the full height"))

    def test_an_h3_has_the_hotels_corner_rising_the_strips_full_height(self):
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "hotel", wraps=A.hotel) as hotel:
                    p = SET.h3(h, night, True)
                (call,) = hotel.call_args_list
                x0, x1, g = call.args[1:4]
                room = call.kwargs["room"] if "room" in call.kwargs else call.args[6]
                self.assertGreaterEqual(x0, 338, (name, night))
                self.assertEqual(x1, p.w - A.EDGE - 1, (name, night))
                self.assertLessEqual(g - room, A.GIRDER + 1, (name, night, "from the girder down to the street"))


class Phones(unittest.TestCase):
    def test_a_phones_h1_has_the_whole_street_under_its_words(self):
        """A phone's H1 stands the whole street across its width under the words, at least 48 rows tall: the booth
        and its streetlamp at the left and the hotel's corner at the right, for every shared content."""
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "booth", wraps=A.booth) as booth, \
                        mock.patch.object(A, "hotel", wraps=A.hotel) as hotel:
                    p, pixels, _ = D.sprites(SET, lambda: SET.h1_narrow(h, night), "scene_narrow")
                self.assertTrue(booth.called and hotel.called, (name, night))
                xs, ys = [x for x, _ in pixels], [y for _, y in pixels]
                self.assertLessEqual(min(xs), 6, (name, night))
                self.assertGreaterEqual(max(xs), 173, (name, night))
                self.assertGreaterEqual(max(ys) - min(ys) + 1, 48, (name, night))

    def test_a_phones_h2_and_h3_stand_their_heroes_under_their_words_whatever_they_say(self):
        for code, hero in (("H2", "callbox"), ("H3", "hotel")):
            self.assertEqual(SET.phone_rows(code, 0), SET.phone_rows(code, 400), code)
            for name, (h, _) in contents(KEY).items():
                for night in (False, True):
                    with mock.patch.object(A, hero, wraps=getattr(A, hero)) as drawn:
                        p, pixels, _ = D.sprites(SET, lambda: D.phone(SET, code)(h, night), "scene_under")
                    self.assertTrue(drawn.called, (code, name, night))
                    ys = [y for _, y in pixels]
                    self.assertGreaterEqual(max(ys) - min(ys) + 1, 44, (code, name, night))


class Footers(unittest.TestCase):
    def test_every_footer_stands_on_the_girder_with_the_booth_after_its_last_cell_lit_by_night(self):
        """Every footer stands on the El's girder along its foot, along more than half its width where its cells
        leave the foot free (a phone's title block, whose last cells come down to the kerb, between them), and on a
        title block whose cells leave it room the phone booth stands on it after the last cell, its light burning
        green by night."""
        _, f = contents(KEY)["repository"]
        for night in (False, True):
            with mock.patch.object(A, "booth_mark", wraps=A.booth_mark) as mark:
                p = SET.f1(f, night)
            (call,) = mark.call_args_list
            self.assertGreater(call.args[1], max(b[2] for b in p.words), (night, "after the last cell"))
            lit = [c for L in p.layers.values() for c in L.values() if c == FLAME[1]]
            self.assertEqual(bool(lit), night, (night, "the booth's light burning green inside it by night"))
            iron = set(IRON)
            for draw, most in ((SET.f1, 2), (SET.f2, 2), (SET.f2_narrow, 2), (SET.f1_narrow, 9)):
                q = draw(f, night)
                girder = [x for x in range(8, q.w - 8) if any(q.layers["base"].get((x, y)) in iron
                                                              for y in range(q.h - 12, q.h - 4))]
                self.assertGreater(len(girder), q.w // most, (draw.__name__, night, "the girder along the foot"))


class Links(unittest.TestCase):
    def test_a_link_button_is_riveted_along_its_top_and_takes_its_own_sprite(self):
        for night in (False, True):
            p = SET.link_button("Docs", 0, night)
            heads = [x for (x, y), c in p.layers["base"].items() if y == 4 and c in (IRON[6], FLAME[3])]
            self.assertGreaterEqual(len(heads), 4, (night, "rivets or lit studs along the top"))
        sprites = [tuple(SET.link_icon(i, False, C["white"])[0]) for i in range(6)]
        self.assertEqual(len(set(sprites)), 6, "six sprites of their own")


class Badges(unittest.TestCase):
    def test_riveted_iron_lies_along_every_badges_top_two_rows_with_the_letters_under_it(self):
        iron = set(IRON)
        for style in BADGE_STYLES:
            drawn = [SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                       SET.badge_states()["green"])]
            drawn += [SET.plate_badge(style, "License", "MIT", "scale", mode) for mode in ("day", "night")]
            for p in drawn:
                rows = {c for (x, y), c in p.layers["base"].items() if y in (0, 1)}
                self.assertTrue(rows and rows <= iron, (style, rows - iron))
                self.assertTrue(all(y >= TOP for _, _, _, y, _ in p.uses["base"]), "the letters sit under the band")

    def test_a_counters_numerals_hold_4_5_on_their_boards(self):
        for night in (False, True):
            q = Pix(20, 20)
            SET.counter_cell(q, 2, 2, night)
            face = q.layers["base"][(7, 8)]
            self.assertGreaterEqual(contrast(SET.counter_ink(night, False), face), 4.5, night)
            self.assertGreaterEqual(contrast(SET.counter_ink(night, True), face), 2.0, night)


class Games(unittest.TestCase):
    def test_the_boards_and_the_podium_are_the_streets_own_stuffs(self):
        own = set(SET.tokens) - set(SET.hand.tokens)
        for night in (False, True):
            light, dark = SET.game_squares(night)
            frame, style = SET.game_frame(night)
            podium = SET.game_podium(night)
            for stuff in (light, dark, frame, podium.stuff):
                self.assertIsInstance(stuff, Stuff)
                self.assertTrue({c.upper() for c in stuff.ramp} <= own, (night, stuff.base))
            self.assertEqual((light.grain, dark.grain, style), ("stone", "metal", "iron"), "concrete and the El")
            self.assertIn(podium.style, PODIUMS)
            self.assertEqual((podium.stuff.base, podium.stuff.grain, podium.style), (RAMP["brick"][3], "tile",
                                                                                     "bunting"))


if __name__ == "__main__":
    unittest.main()
