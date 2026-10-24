# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Rabbit design's tests: the checks every design of a collection shares, run over Rabbit, and its own rules,
which the shared checks cannot know: the moon hangs in the rose arch, the hookah's coal and the gardeners' lantern burn
and only the Cheshire Cat's grin is left by night alone, and the butterfly flutters round the arch by day alone; every
letter of a title is printed on a playing card, red or black by its suit, the cards dealt askew at a title's sizes and
a tone down in the garden's dusk by night; the pack of cards blows round the sky, every card turning over, the White
Rabbit bounds, the code steps up out of the rabbit hole, the Caterpillar's smoke rises and the Two of Spades dabs his
brush, each on its own cadence; each header's hero stands where it should, the White Rabbit under his arch at the
left of an H1 and the old tree at its right, the Caterpillar on his mushroom at the right of an H2, his smoke rising to
the hedge, and the rose tree with its gardener at the right of an H3, rising the strip's full height in more heads the
taller the strip; a phone's H1 holds the whole of Wonderland under its words, and its H2 and H3 their heroes whatever
the words say; every footer stands on the hedge's top, with the rabbit hole after a title block's last cell, its code
burning by night; a link button carries a sprig of the hedge along its top and each of the four takes its own sprite;
a badge's top two rows are the hedge set with roses; a counter's numerals hold 4.5:1 on their cards; and the games'
boards and podium are the garden's own stuffs."""
from __future__ import annotations

import re
import unittest
from unittest import mock

from tests.unit import design_checks as D
from tests.unit.test_holiday_sets import contents

from domain.banners.content import Header
from domain.canvas import DARK, DAY
from domain.collections import rain
from domain.collections.matrix_rabbit import SET
from domain.collections.matrix_rabbit import art as A
from domain.collections.matrix_rabbit.palette import RAMP
from domain.holidays.designs.badges import STYLES as BADGE_STYLES, TOP
from domain.holidays.designs.materials import Podium, Stuff
from domain.holidays.pixel import Pix, contrast

KEY = SET.key
HEADER = Header(tone="standard", holiday=KEY)
CONTENTS = contents(KEY)
CARD, ROSE, SPADE, HEDGE = (RAMP[n] for n in ("card", "rose", "spade", "hedge"))
MOON = {c.upper() for c in RAMP["moon"]}
DRAWN: dict = {}


def header(code, theme, wide=True, motion=True) -> str:
    """The kit's own header in Rabbit, drawn once and kept."""
    key = (code, theme["name"], wide, motion)
    if key not in DRAWN:
        DRAWN[key] = SET.header(code, HEADER, theme, wide, motion)
    return DRAWN[key]


def hexes(svg: str) -> set:
    return {c.upper() for c in re.findall(r"#[0-9A-Fa-f]{6}", svg)}


class Shared(D.Shared, unittest.TestCase):
    SET = SET
    ART = A
    PIECES = ("warren", "white_rabbit", "rose_arch", "tree", "fallen_cards", "fireflies", "moon", "meadow",
              "caterpillar_scene", "mushroom", "_rings", "rose_garden", "rose_tree", "card_gardener", "lantern",
              "card_title")
    FOOTINGS = ("_footed",)


class Night(unittest.TestCase):
    def test_what_the_night_alone_shows_stays_out_of_the_day_and_the_days_butterfly_out_of_the_night(self):
        """The moon hangs in the rose arch by night alone, wide and on a phone, moving and still; the hookah's coal on
        an H2 and the lantern in an H3's rose tree burn and flicker by night alone; and the butterfly flutters round
        the arch in a moving header by day alone."""
        for wide, motion in ((True, True), (True, False), (False, False)):
            self.assertFalse(MOON & hexes(header("H1", DAY, wide, motion)), (wide, motion, "no moon by day"))
            self.assertTrue(MOON & hexes(header("H1", DARK, wide, motion)), (wide, motion, "the moon by night"))
        self.assertIn('dur="32s"', header("H1", DAY), "the butterfly's round")
        self.assertNotIn('dur="32s"', header("H1", DARK))
        for code in ("H2", "H3"):
            self.assertFalse(D.flickering(D.wide(SET, code)(HEADER, False, True)), (code, "no light burns by day"))
            self.assertTrue(D.flickering(D.wide(SET, code)(HEADER, True, True)), (code, "a light burns by night"))

    def test_the_cheshire_cat_sits_on_his_bough_by_day_and_by_night_only_his_grin_is_left(self):
        """By day the cat sits whole on the old tree's bough; by night only his grin hangs there, wide and on a
        phone, and in a moving header the cat comes and goes round it on an eight-second loop."""
        for draw in (lambda night: SET.h1(HEADER, night, True), lambda night: SET.h1_narrow(HEADER, night)):
            self.assertNotIn("grin", draw(False).layers)
            self.assertIn("grin", draw(True).layers)
        night = SET.h1(HEADER, True, True)
        self.assertEqual(night.meta["cat"][2][0::3], ("seq", 8.0), "the cat comes and goes")
        self.assertNotIn("cat", SET.h1(HEADER, True, False).layers, "and the still file keeps only the grin")


class Titles(unittest.TestCase):
    def test_every_letter_of_a_title_is_printed_on_a_playing_card_red_or_black_by_its_suit(self):
        """Each letter is laid on a card of its own, in the roses' red for hearts and diamonds and the spades' black for
        spades and clubs, a pip of its suit in the card's corner, the cards dealt a little askew at a title's sizes and
        square when small; one box holds the line, round its cards."""
        for night in (False, True):
            p = Pix(415, 60)
            A.card_title(p, 10, 20, "RABBIT", night, 4)
            cards = [k for k in p.syms if isinstance(k, tuple) and k[0] == "card"]
            self.assertTrue(any(k[3] for k in cards), (night, "dealt askew"))
            self.assertTrue(any(isinstance(k, tuple) and k[0] == "pip" for k in p.syms), (night, "pips"))
            self.assertEqual({u[0] for u in p.uses["base"] if u[0]}, {ROSE[3], SPADE[1]}, night)
            self.assertEqual(len(p.words), 1, night)
        p = Pix(415, 40)
        A.card_title(p, 10, 10, "RABBIT", False, 2)
        self.assertFalse(any(isinstance(k, tuple) and k[0] == "card" and k[3] for k in p.syms), "square when small")

    def test_by_night_the_cards_lie_a_tone_down_in_the_gardens_dusk(self):
        """A card's face is the card's white by day and a tone down by night, its rim the card's grey either way."""
        for night, face in ((False, CARD[5]), (True, CARD[4])):
            cells = A._card(14, 18, 0.0, night)
            self.assertEqual(cells[(7, 9)], face, night)
            self.assertEqual(cells[(7, 0)], CARD[1], night)


class Motion(unittest.TestCase):
    def test_the_cards_blow_round_the_sky_the_rabbit_bounds_and_the_code_rises_each_on_its_cadence(self):
        """Across a moving H1's sky the pack of cards is blown round every forty seconds, every card turning over every
        1.6; the White Rabbit bounds every 2.2; and the code steps up out of the rabbit hole a glyph every 0.12
        seconds."""
        moving = header("H1", DARK)
        for dur in ("40", "1.6", "2.2"):
            self.assertIn(f'dur="{dur}s"', moving, dur)
        rising = re.search(rf'values="(0 0;0 -{rain.PITCH}(?:;0 -\d+)*)" dur="([\d.]+)s"', moving)
        self.assertIsNotNone(rising, "the code rising out of the hole")
        self.assertAlmostEqual(float(rising.group(2)) / len(rising.group(1).split(";")), 0.12, places=3)

    def test_the_caterpillars_smoke_rises_and_the_gardener_dabs_each_on_a_figures_loop(self):
        """On an H2 the smoke rises from the Caterpillar's lips a step every half second round a six-second loop; on an
        H3 the Two of Spades dabs his brush round a four-second loop, the rose under it turning from white to red on
        the same loop and half painted in the still file."""
        smoke = re.search(r'values="(0 0;-2 -4;[^"]*)" dur="6s"', header("H2", DAY))
        self.assertIsNotNone(smoke, "the smoke rising")
        self.assertEqual(len(smoke.group(1).split(";")), 12, "a step every half second")
        p = SET.h3(HEADER, False, True)
        self.assertEqual(p.meta["dab"][2][0::2], ("bob", 4.0))
        self.assertEqual([p.meta[f"paint{i}"][2][3] for i in range(3)], [4.0] * 3)
        self.assertEqual([p.meta[f"paint{i}"][2][4] for i in range(3)], [False, True, False], "half painted, still")


class Heroes(unittest.TestCase):
    def test_an_h1_has_the_white_rabbit_at_the_left_and_the_old_tree_at_the_right(self):
        h, _ = CONTENTS["kit"]
        for night in (False, True):
            with mock.patch.object(A, "warren", wraps=A.warren) as warren, \
                    mock.patch.object(A, "tree", wraps=A.tree) as tree:
                p = SET.h1(h, night, True)
            (w,), (t,) = warren.call_args_list, tree.call_args_list
            self.assertLess(w.args[1], 12, (night, "the rabbit under his arch at the left"))
            self.assertGreater(t.args[1], 340, (night, "the old tree at the right"))
            self.assertEqual(t.args[2], p.w - A.EDGE - 1, night)

    def test_an_h2_has_the_caterpillar_on_his_mushroom_at_the_right_his_smoke_rising_to_the_hedge(self):
        """At the right of every H2 the giant mushroom stands on the grass with the Caterpillar on its cap, and his
        smoke rises from his lips to two rows under the hedge at the page's top, for every shared content."""
        for name, (h, _) in CONTENTS.items():
            with mock.patch.object(A, "caterpillar_scene", wraps=A.caterpillar_scene) as scene, \
                    mock.patch.object(A, "_rings", wraps=A._rings) as smoke:
                p = SET.h2(h, False, True)
            (call,) = scene.call_args_list
            x0, x1, g = call.args[1:4]
            self.assertGreaterEqual(x0, 296, name)
            self.assertEqual(x1, p.w - A.EDGE - 1, name)
            self.assertGreaterEqual(g - A.TOP, 90, (name, "risen the full height"))
            self.assertEqual(smoke.call_args.args[1][1], A.TOP + 2, (name, "the smoke rising to the hedge"))

    def test_an_h3_has_the_rose_tree_and_its_gardener_rising_the_strips_full_height(self):
        """At the right of every H3 the rose tree stands in its tub on the strip's grass, its crown two rows under the
        hedge at the top, the Two of Spades painting it; the taller the strip, the more heads it is trained in."""
        heads = {}
        for name, (h, _) in CONTENTS.items():
            with mock.patch.object(A, "rose_tree", wraps=A.rose_tree) as tree, \
                    mock.patch.object(A, "card_gardener", wraps=A.card_gardener) as gardener, \
                    mock.patch.object(SET, "scene", wraps=SET.scene) as scene:
                SET.h3(h, False, True)
            (call,) = tree.call_args_list
            cx, g, top = call.args[1], call.args[2], call.args[5]
            self.assertGreater(cx, 360, name)
            self.assertEqual(top, A.TOP + 2, (name, "from the hedge"))
            self.assertEqual(g, scene.call_args.args[2] - 1, (name, "down to the grass on the strip's rule"))
            self.assertEqual(len(gardener.call_args_list), 1, name)
            heads[name] = 1 if g - 9 - top <= 66 else 2 if g - 9 - top <= 108 else 3
        self.assertGreater(heads["most"], heads["least"])


class Phones(unittest.TestCase):
    def test_a_phones_h1_has_the_whole_of_wonderland_under_its_words(self):
        """A phone's H1 stands the rose arch with the White Rabbit, the trail of cards and the old tree with its rabbit
        hole across its width under the words, at least 48 rows tall, for every shared content."""
        for name, (h, _) in CONTENTS.items():
            for night in (False, True):
                with mock.patch.object(A, "phone_world", wraps=A.phone_world) as world:
                    _, pixels, _ = D.sprites(SET, lambda: SET.h1_narrow(h, night), "scene_narrow")
                self.assertTrue(world.called, (name, night))
                xs, ys = [x for x, _ in pixels], [y for _, y in pixels]
                self.assertLessEqual(min(xs), 6, (name, night))
                self.assertGreaterEqual(max(xs), 173, (name, night))
                self.assertGreaterEqual(max(ys) - min(ys) + 1, 48, (name, night))

    def test_a_phones_h2_and_h3_stand_their_heroes_under_their_words_whatever_they_say(self):
        """Whatever the words, a phone's H2 stands the Caterpillar on his mushroom under them and its H3 the Five of
        Spades at a rose bush and the Two at the rose tree, painting the roses red, each across the phone."""
        for code, hero in (("H2", "phone_caterpillar"), ("H3", "phone_garden")):
            for name, (h, _) in CONTENTS.items():
                with mock.patch.object(A, hero, wraps=getattr(A, hero)) as drawn, \
                        mock.patch.object(A, "card_gardener", wraps=A.card_gardener) as gardener:
                    _, pixels, _ = D.sprites(SET, lambda: D.phone(SET, code)(h, False), "scene_under")
                self.assertTrue(drawn.called, (code, name))
                ys = [y for _, y in pixels]
                self.assertGreaterEqual(max(ys) - min(ys) + 1, 44, (code, name))
                faces = sorted(c.kwargs.get("face", "two") for c in gardener.call_args_list)
                self.assertEqual(faces, ["five", "two"] if code == "H3" else [], (code, name))


class Footers(unittest.TestCase):
    def test_every_footer_stands_on_the_hedge_with_the_rabbit_hole_after_its_last_cell(self):
        """Along every footer's foot lies the hedge's top, lit and set with roses, in its lower rows where a word comes
        down onto it; on a title block whose cells leave it room the rabbit hole stands in its mound after the last
        cell, the way back up, and by night its code burns and flickers on the hand's flame."""
        _, f = CONTENTS["repository"]
        foot = set(HEDGE) | set(ROSE) | set(CARD)
        for night in (False, True):
            with mock.patch.object(A, "hole_mound", wraps=A.hole_mound) as mound:
                p = SET.f1(f, night)
            (call,) = mound.call_args_list
            self.assertGreater(call.args[1], max(b[2] for b in p.words), (night, "after the last cell"))
            self.assertEqual(bool(D.flickering(p)), night, (night, "the code burning by night"))
            for draw in (SET.f1, SET.f2, SET.f1_narrow, SET.f2_narrow):
                q = draw(f, night)
                hedge = [x for x in range(q.w) if any(q.layers["base"].get((x, y)) in foot
                                                      for y in range(q.h - A.EDGE, q.h - 1))]
                self.assertGreater(len(hedge), q.w * 9 // 10, (draw.__name__, night, "the hedge along the foot"))


class Links(unittest.TestCase):
    def test_a_link_button_is_a_playing_card_under_a_sprig_of_hedge_and_takes_its_own_sprite(self):
        """A link button carries a sprig of the clipped hedge set with roses along its two top rows, over a card's face
        by day and the garden's indigo by night, its letters holding 4.5:1 on it; each of the four takes a sprite of
        its own."""
        for night in (False, True):
            p = SET.link_button("Docs", 0, night)
            top = {c for (x, y), c in p.layers["base"].items() if y < 2}
            self.assertTrue(top and top <= set(HEDGE) | set(ROSE) | set(CARD), (night, top))
            fill, _, ink, _ = SET.link_colours(night)
            self.assertGreaterEqual(contrast(ink, fill), 4.5, night)
        sprites = [tuple(SET.link_icon(i, False, CARD[6])[0]) for i in range(4)]
        self.assertEqual(len(set(sprites)), 4, "four sprites of their own")


class Badges(unittest.TestCase):
    def test_the_hedge_lies_along_every_badges_top_two_rows_with_the_letters_under_it(self):
        hedge = set(HEDGE) | set(ROSE)
        for style in BADGE_STYLES:
            drawn = [SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                       SET.badge_states()["green"])]
            drawn += [SET.plate_badge(style, "License", "MIT", "scale", mode) for mode in ("day", "night")]
            for p in drawn:
                rows = {c for (x, y), c in p.layers["base"].items() if y in (0, 1)}
                self.assertTrue(rows and rows <= hedge, (style, rows - hedge))
                self.assertTrue(all(y >= TOP for _, _, _, y, _ in p.uses["base"]), "the letters sit under the band")

    def test_a_counters_numerals_hold_4_5_on_their_cards(self):
        for night in (False, True):
            q = Pix(20, 20)
            SET.counter_cell(q, 2, 2, night)
            face = q.layers["base"][(7, 9)]
            self.assertGreaterEqual(contrast(SET.counter_ink(night, False), face), 4.5, night)
            self.assertGreaterEqual(contrast(SET.counter_ink(night, True), face), 2.0, night)


class Games(unittest.TestCase):
    def test_the_boards_and_the_podium_are_the_gardens_own_stuffs(self):
        """The squares are the Looking-Glass country's, spring meadow and clipped hedge; the frame is painted in stripes
        of red and white, as the gardeners paint the roses; and the winners stand on a podium of clipped hedge hung
        with a garland of roses: all of the design's own tones, none the hand lends every design."""
        own = set(SET.tokens) - set(SET.hand.tokens)
        for night in (False, True):
            light, dark = SET.game_squares(night)
            frame, style = SET.game_frame(night)
            podium = SET.game_podium(night)
            self.assertIsInstance(podium, Podium)
            for stuff in (light, dark, frame, podium.stuff, podium.trim):
                self.assertIsInstance(stuff, Stuff)
                self.assertTrue(stuff.tokens <= own, (night, stuff.base))
            self.assertEqual((light.grain, dark.grain, style), ("sand", "needles", "stripes"))
            self.assertEqual((podium.stuff.base, podium.stuff.grain, podium.style), (HEDGE[3], "needles", "garland"))
            self.assertEqual(podium.trim.ramp, ROSE, "a garland of roses")


if __name__ == "__main__":
    unittest.main()
