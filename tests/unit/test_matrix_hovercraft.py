# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Hovercraft design's tests: the checks every design of a collection shares, run over Hovercraft, and its own
rules, which the shared checks cannot know: the tunnel's concrete is the day's and its black the night's, and the dust
glinting in the searchlight's beam is the night's alone; a title is stencilled in drab paint by day and lit green by
night, the stencil's bridges cut through it to the steel plate it is painted on; the searchlight sweeps the tunnel on
its slow loop, the code falls down the deck's screens and the hanging machine's gaze swings over the water, each in a
wide moving header only; each header's hero stands where it should, the ship at the left and the machine coming out of
the drain at the right on an H1, the main deck cut away at the right, risen the full height, on an H2, and the machine
hanging from the pipes over the water, the strip's full height, on an H3; a phone's H1 holds the whole tunnel under its
words and its H2 and H3 stand their heroes under theirs; every footer stands on the channel's water, with the ship
after a title block's last cell, its lights burning by night; a link button is riveted along its top and each of the
four takes its own sprite; a badge's top two rows are the tunnel's pipe; a counter's numerals hold 4.5:1 on their
readout; and the games' boards and podium are the ship's own stuffs."""
from __future__ import annotations

import unittest
from unittest import mock

from tests.unit import design_checks as D
from tests.unit.test_holiday_sets import contents

from domain.banners.content import Header
from domain.canvas import DARK, DAY
from domain.collections.matrix_hovercraft import SET
from domain.collections.matrix_hovercraft import art as A
from domain.collections.matrix_hovercraft import deck as DK
from domain.collections.matrix_hovercraft.palette import C, NIGHT_SKY, RAMP
from domain.holidays.designs.badges import STYLES as BADGE_STYLES, TOP
from domain.holidays.designs.materials import PODIUMS, Stuff
from domain.holidays.pixel import Pix, contrast

KEY = SET.key
HEADER = Header(tone="standard", holiday=KEY)
FLAME, STEEL, WATER, TUNNEL = (set(RAMP[n]) for n in ("flame", "steel", "water", "tunnel"))
DUST = 'dur="1.5s"'          # the dust glinting in the searchlight's beam, by night


def dur(seconds: float) -> str:
    return f'dur="{A.num(seconds)}s"'


class Shared(D.Shared, unittest.TestCase):
    SET = SET
    ART = A
    PIECES = ("title_plate", "beam", "ship", "wash", "steam", "drips", "headwall", "outlet", "sentinel", "lurker",
              "water", "mist", "deck", "hanging", "phone_world", "phone_hunter", "straws")
    FOOTINGS = ("_footed",)


class Night(unittest.TestCase):
    def test_the_concrete_is_the_days_the_tunnels_black_the_nights_and_the_dust_in_the_beam_the_nights_alone(self):
        for code in ("H1", "H2", "H3"):
            day = SET.header(code, HEADER, DAY, True, True)
            night = SET.header(code, HEADER, DARK, True, True)
            self.assertIn(C["paper"], day, (code, "the concrete by day"))
            self.assertFalse([c for c in NIGHT_SKY if c in day], (code, "the tunnel's black by day"))
            self.assertNotIn(C["paper"], night, (code, "the concrete by night"))
            self.assertTrue([c for c in NIGHT_SKY if c in night], (code, "the tunnel's black by night"))
            self.assertNotIn(DUST, day, (code, "dust glinting by day"))
        self.assertIn(DUST, SET.header("H1", HEADER, DARK, True, True), "the dust glinting in the beam by night")


class Titles(unittest.TestCase):
    def test_a_title_is_stencilled_in_drab_by_day_and_lit_green_by_night_its_bridges_cut_to_the_plate(self):
        for night in (False, True):
            p = Pix(200, 60)
            p.plate = (0, 0, 200, 60)
            A.stencil_title(p, 10, 10, "BANNERS", night, 3)
            face = {stroke for stroke, *_ in p.uses["base"]}
            self.assertEqual(face, {RAMP["flame"][3] if night else RAMP["drab"][1]}, night)
            cuts = set(p.layers["stencil"].values())
            self.assertEqual(cuts, {C["plate_night"] if night else RAMP["plate"][4]}, "cut through to the plate")
            lit = set(p.layers.get("base~", {}).values())
            self.assertEqual(RAMP["flame"][5] in lit, night, "the lamps' light on the letters' upper edges by night")

    def test_an_h1s_title_stands_on_its_steel_plate_and_no_other_title_does(self):
        for code in ("H1", "H2", "H3"):
            with mock.patch.object(A, "title_plate", wraps=A.title_plate) as plate:
                SET.header(code, HEADER, DAY, True, True)
            self.assertEqual(plate.called, code == "H1", code)


class Motion(unittest.TestCase):
    def test_the_beam_sweeps_the_code_falls_and_the_gaze_swings_only_in_a_wide_moving_header(self):
        for code, beat in (("H1", A.SWEEP), ("H2", DK.CODE_LOOP), ("H3", A.SCAN)):
            moving = SET.header(code, HEADER, DARK, True, True)
            self.assertIn(dur(beat), moving, code)
            for still in (SET.header(code, HEADER, DARK, True, False), SET.header(code, HEADER, DARK, False, False)):
                self.assertNotIn("<animate", still, code)
        self.assertEqual(SET.header("H1", HEADER, DAY, True, True).count(dur(A.SWEEP)), 1, "one beam")


class Heroes(unittest.TestCase):
    def test_an_h1_has_the_ship_at_the_left_and_the_machine_coming_out_of_the_drain_at_the_right(self):
        h, _ = contents(KEY)["kit"]
        for night in (False, True):
            with mock.patch.object(A, "ship", wraps=A.ship) as ship, \
                    mock.patch.object(A, "sentinel", wraps=A.sentinel) as machine, \
                    mock.patch.object(A, "outlet", wraps=A.outlet) as drain:
                SET.h1(h, night, True)
            (s,), (m,), (d,) = (c.call_args_list for c in (ship, machine, drain))
            self.assertLess(s.args[1], 20, "the ship at the left")
            self.assertGreater(d.args[1], 370, "the drain at the right")
            self.assertTrue(340 < m.args[1] < d.args[1], "the machine coming out of it")

    def test_an_h2_has_the_main_deck_cut_away_at_the_right_risen_the_full_height(self):
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "deck", wraps=A.deck) as deck, \
                        mock.patch.object(DK, "chair", wraps=DK.chair) as chair, \
                        mock.patch.object(DK, "operator", wraps=DK.operator) as operator:
                    p, pixels, _ = D.sprites(SET, lambda: SET.h2(h, night, True), "scene")
                if not deck.called:
                    self.assertEqual(name, "most", "only the most a page can say leaves the deck no room")
                    continue
                (call,) = deck.call_args_list
                x0, x1, g, top = call.args[1], call.args[2], call.args[3], call.args[6]
                self.assertTrue(306 <= x0 < 330 and x1 == 410, (name, night, x0))
                self.assertEqual(top, A.TOP + 2, (name, night, "from under the pipes"))
                self.assertGreaterEqual(g - top, 80, (name, night, "risen the full height"))
                self.assertTrue(chair.called and operator.called, (name, night, "the operator and the chair"))
                self.assertEqual([xy for xy in pixels if D.near(p, xy, 2)], [], (name, night))

    def test_an_h3_has_the_machine_hanging_from_the_pipes_over_the_water_the_strips_full_height(self):
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "hanging", wraps=A.hanging) as hanging, \
                        mock.patch.object(A, "water", wraps=A.water) as water:
                    SET.h3(h, night, True)
                (call,) = hanging.call_args_list
                x, grip, floor = call.args[1], call.args[5], call.args[6]
                self.assertGreater(x, 350, (name, night, "at the right"))
                self.assertEqual(grip, 11, (name, night, "coiled round the copper line"))
                self.assertGreaterEqual(floor - grip, 45, (name, night, "the strip's full height"))
                self.assertTrue(water.called, (name, night, "over the water"))


class Phones(unittest.TestCase):
    def test_a_phones_h1_has_the_whole_tunnel_under_its_words(self):
        """A phone's H1 stands the whole tunnel across its width under the words, at least 48 rows tall: the ship
        hovering over the water at the left and the machine at the drain at the right, for every shared content."""
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "ship", wraps=A.ship) as ship, \
                        mock.patch.object(A, "outlet", wraps=A.outlet) as drain:
                    p, pixels, _ = D.sprites(SET, lambda: SET.h1_narrow(h, night), "scene_narrow")
                self.assertTrue(ship.called and drain.called, (name, night))
                xs, ys = [x for x, _ in pixels], [y for _, y in pixels]
                self.assertLessEqual(min(xs), 6, (name, night))
                self.assertGreaterEqual(max(xs), 173, (name, night))
                self.assertGreaterEqual(max(ys) - min(ys) + 1, 48, (name, night))

    def test_a_phones_h2_and_h3_stand_their_heroes_under_their_words_whatever_they_say(self):
        for code, hero in (("H2", "deck"), ("H3", "hanging")):
            self.assertEqual(SET.phone_rows(code, 0), SET.phone_rows(code, 400), code)
            for name, (h, _) in contents(KEY).items():
                for night in (False, True):
                    with mock.patch.object(A, hero, wraps=getattr(A, hero)) as drawn:
                        p, pixels, _ = D.sprites(SET, lambda: D.phone(SET, code)(h, night), "scene_under")
                    self.assertTrue(drawn.called, (code, name, night))
                    ys = [y for _, y in pixels]
                    self.assertGreaterEqual(max(ys) - min(ys) + 1, 48, (code, name, night))


class Footers(unittest.TestCase):
    def test_every_footer_stands_on_the_water_with_the_ship_after_its_last_cell_its_lights_burning_by_night(self):
        """Every footer stands on the channel's black water along its foot, and on a title block whose cells leave it
        room the ship hovers after its last cell, its searchlight on the drain where the machine's eyes burn; by
        night its lights burn and flicker on the hand's flame."""
        h, f = contents(KEY)["repository"]
        for night in (False, True):
            with mock.patch.object(A, "mini_ship", wraps=A.mini_ship) as ship:
                p = SET.f1(f, night)
            (call,) = ship.call_args_list
            self.assertGreater(call.args[1], max(b[2] for b in p.words), "after the last cell")
            lit = D.flickering(p)
            self.assertEqual(bool(lit), night, "its lights flicker by night")
            self.assertTrue(lit <= FLAME, lit - FLAME)
            water = (TUNNEL if night else WATER)
            for draw in (SET.f1, SET.f2, SET.f1_narrow, SET.f2_narrow):
                q = draw(f, night)
                foot = [(x, y) for x in range(A.EDGE, q.w - A.EDGE) for y in range(q.h - A.EDGE - 3, q.h - A.EDGE)
                        if q.layers["base"].get((x, y)) in water]
                self.assertGreaterEqual(len(foot), q.w // 2, (draw.__name__, night, "the water"))


class Links(unittest.TestCase):
    def test_a_link_button_is_riveted_along_its_top_and_takes_its_own_sprite(self):
        for night in (False, True):
            for i in range(4):
                p = SET.link_button("Docs", i, night)
                heads = [x for x in range(p.w) if p.layers["base"].get((x, 2)) == (RAMP["plate"][6] if not night
                                                                                   else RAMP["steel"][6])]
                self.assertGreaterEqual(len(heads), 2, (night, i, "rivets along its top"))
        sprites = [tuple(SET.link_icon(i, False, C["white"])[0]) for i in range(4)]
        self.assertEqual(len(set(sprites)), 4, "four sprites of their own")


class Badges(unittest.TestCase):
    def test_the_tunnels_pipe_lies_along_every_badges_top_two_rows_with_the_letters_under_it(self):
        for style in BADGE_STYLES:
            drawn = [SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                       SET.badge_states()["green"])]
            drawn += [SET.plate_badge(style, "License", "MIT", "scale", mode) for mode in ("day", "night")]
            for p in drawn:
                rows = {c for (x, y), c in p.layers["base"].items() if y in (0, 1)}
                self.assertTrue(rows and rows <= STEEL, (style, rows - STEEL))
                self.assertTrue(all(y >= TOP for _, _, _, y, _ in p.uses["base"]), "the letters sit under the pipe")

    def test_a_counters_numerals_hold_4_5_on_their_readout(self):
        for night in (False, True):
            q = Pix(20, 20)
            SET.counter_cell(q, 2, 2, night)
            face = q.layers["base"][(7, 8)]
            self.assertGreaterEqual(contrast(SET.counter_ink(night, False), face), 4.5, night)
            self.assertGreaterEqual(contrast(SET.counter_ink(night, True), face), 2.0, night)


class Games(unittest.TestCase):
    def test_the_boards_and_the_podium_are_the_ships_own_stuffs(self):
        own = set(SET.tokens) - set(SET.hand.tokens)
        for night in (False, True):
            light, dark = SET.game_squares(night)
            frame, style = SET.game_frame(night)
            podium = SET.game_podium(night)
            for stuff in (light, dark, frame, podium.stuff, podium.trim):
                self.assertIsInstance(stuff, Stuff)
                self.assertTrue({c.upper() for c in stuff.ramp} <= own, (night, stuff))
            self.assertEqual((light.grain, dark.grain), ("metal", "flecks"), "deck plate and drab paint")
            self.assertIn(podium.style, PODIUMS)
            self.assertEqual((podium.stuff.ramp, podium.stuff.grain, podium.style), (RAMP["steel"], "metal",
                                                                                     "shields"))

    def test_a_move_is_stencilled_as_the_titles_are_and_cut_with_the_panel_it_appears_on(self):
        p = Pix(200, 60)
        p.layer("sec1", ("once", "", ""), z=0.6)
        with p.onto("sec1"):
            A.stencil_title(p, 10, 10, "21. Nd6+", True, 3)
        self.assertTrue(p.layers.get("sec1stencil"), "the stencil's cuts appear with the move")
        self.assertFalse(p.layers.get("stencil"), "and never before it")


if __name__ == "__main__":
    unittest.main()
