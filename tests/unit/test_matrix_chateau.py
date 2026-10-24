# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Chateau set's own rules, which the checks every design of a collection shares cannot know: what the night alone
shows (the moon in the hall's window, the candles' glow on the silk and their light pooled on the floor) stays out of
the day's files; a title is gold leaf on carved letters by day and by night, the candles glinting on it in a moving
header; the candles flicker and the crystal glitters on the engine's cadences; every header stands its own hero where
the words leave it room (the hall and the banquet on H1, the fireplace between its torcheres on H2, the suit of armour
rising an H3's full height) and every phone header stands one of the chateau's scenes under its words; the valance
hangs under the frieze; every footer stands on the red carpet, a balustrade rising behind it where the cells leave room
and the emblem after a title block's last cell; a link button is red velvet in gilt; a string of gilt beads lies along
every badge's top; a counter's numerals hold 4.5:1 on their tiles; and the boards and the podium are cut from the
chateau's own stuffs. The set is a theme, not a holiday on the calendar, so the checks every design of a collection
shares (`design_checks`) run here over the set directly, with the same contents and the same entry points."""
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
from domain.collections.matrix_chateau import SET
from domain.collections.matrix_chateau import art as A
from domain.collections.matrix_chateau import surfaces as F
from domain.collections.matrix_chateau.palette import RAMP
from domain.holidays.designs.badges import STYLES as BADGE_STYLES, TOP
from domain.holidays.pixel import Pix, contrast

support.install()
KEY = SET.key
HEADER = Header(tone="standard", holiday=KEY)
FLAME, GOLD, MOON = set(RAMP["flame"]), set(RAMP["gold"]), set(RAMP["moon"])
GLOW = re.compile(r'<ellipse[^>]*fill="' + RAMP["flame"][3] + '"')     # a candle's glow, or its light on the floor
DRAWN: dict = {}


def header(code: str, night: bool, motion: bool = True, h=HEADER) -> str:
    """A header's file, drawn once for every test that only reads it."""
    key = (code, night, motion, id(h))
    if key not in DRAWN:
        DRAWN[key] = SET.header(code, h, DARK if night else DAY, True, motion)
    return DRAWN[key]


class Shared(D.Shared, unittest.TestCase):
    SET = SET
    ART = A
    PIECES = ("hall", "banquet", "chandelier", "guest", "fireplace", "mirror", "torchere", "armour")
    FOOTINGS = ("_footed",)


class Night(unittest.TestCase):
    def test_what_the_night_alone_shows_stays_out_of_the_day(self):
        """By night the hand's moon hangs in the hall's window and the candles throw their glow on the silk and pool
        their light on the floor; by day none of it is drawn, the window holding the day's pale sky."""
        night, day = header("H1", True), header("H1", False)
        self.assertTrue(any(c in night for c in MOON), "the moon in the window")
        self.assertRegex(night, GLOW, "the candles' glow and the light they pool")
        self.assertFalse(any(c in day for c in MOON), "no moon by day")
        self.assertNotRegex(day, GLOW, "no glow by day")
        self.assertIn(RAMP["crystal"][6], day, "the day's pale sky in the window")
        for code in ("H2", "H3"):
            self.assertRegex(header(code, True), GLOW, (code, "the fire's and the torcheres' light by night"))
            self.assertNotRegex(header(code, False), GLOW, (code, "none by day"))


class Titles(unittest.TestCase):
    def test_a_title_is_gold_leaf_on_carved_letters_and_the_candles_glint_on_it(self):
        """The title is gilt by day and by night, its letters carved in the gilt's tones; in a moving header the
        candles glint on every other letter's corner, gold by day and green by night, twinkling, and the still file
        and a phone's carry no glint."""
        for night in (False, True):
            with mock.patch.object(A, "sparkles", wraps=A.sparkles) as glints:
                p = SET.h1(HEADER, night, True)
            self.assertTrue(glints.called, night)
            lit = {c for L, cells in p.layers.items() if L.startswith("tw") for c in cells.values()}
            self.assertIn(RAMP["gold"][6] if not night else RAMP["flame"][5], lit, night)
            defs = "".join(p.defs)
            self.assertTrue(all(c in defs for c in (RAMP["gold"][5], RAMP["gold"][0])), (night, "the gilt's tones"))
            with mock.patch.object(A, "sparkles", wraps=A.sparkles) as glints:
                SET.h1(HEADER, night, False)
                SET.h1_narrow(HEADER, night)
            self.assertFalse(glints.called, (night, "no glint holds still"))

    def test_the_candles_flicker_and_the_crystal_glitters_on_the_engines_cadences(self):
        """In a moving header every candle's flame flickers on the engine's flicker and the crystal glitters on its
        twinkle; a still header holds them where they are."""
        for night in (False, True):
            moving = header("H1", night)
            self.assertIn('dur="1.8s"', moving, (night, "the flames flicker"))
            self.assertIn('dur="1.5s"', moving, (night, "the crystal glitters"))
            self.assertNotIn("<animate", header("H1", night, motion=False))


class Heroes(unittest.TestCase):
    def test_every_header_stands_its_own_hero_where_the_words_leave_it_room(self):
        """An H1 stands the hall at its left and the banquet at its right; an H2 the fireplace between its torcheres
        with the pier glass over its mantel; an H3 the suit of armour with its torchere, for the kit's own lines."""
        named = {"H1": ("hall", "banquet"), "H2": ("fireplace", "mirror", "torchere"), "H3": ("armour", "torchere")}
        for code, names in named.items():
            for night in (False, True):
                with contextlib.ExitStack() as stack:
                    spies = [stack.enter_context(mock.patch.object(A, n, wraps=getattr(A, n))) for n in names]
                    getattr(SET, code.lower())(HEADER, night, True)
                self.assertTrue(all(spy.called for spy in spies), (code, night))

    def test_an_h2s_fireplace_rises_from_the_floor_toward_the_frieze(self):
        """The H2's fireplace, its glass and its torcheres stand at the right from the floor to within ten rows of the
        frieze, two units clear of every word, for every shared content."""
        for name, (h, _) in contents(KEY).items():
            p, pixels, _ = D.sprites(SET, lambda: SET.h2(h, False, True), "scene")
            ys = [y for _, y in pixels]
            self.assertLessEqual(min(ys), A.TOP + 10, name)
            self.assertGreaterEqual(min(x for x, _ in pixels), 314, name)

    def test_an_h3_has_its_suit_of_armour_rising_the_strips_full_height(self):
        """At the right of every wide H3 stands the suit of armour with its halberd and its torchere, rising from the
        floor to within a few rows of the frieze: the strip's full height, for every shared content."""
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "armour", wraps=A.armour) as suit:
                    p, pixels, _ = D.sprites(SET, lambda: SET.h3(h, night, True), "scene")
                (call,) = suit.call_args_list
                g = call.args[2]
                top = min(y for _, y in pixels)
                self.assertLessEqual(top, A.TOP + 6, (name, night))
                self.assertGreaterEqual(g - top, 54, (name, night))
                self.assertGreaterEqual(min(x for x, _ in pixels), 358, (name, night))

    def test_a_phones_headers_stand_the_chateaus_scenes_under_their_words(self):
        """A phone's H1 stands the whole chateau across its width under the words, at least 48 rows tall, the hall at
        the left and the banquet at the right; its H2 the fireplace with the guest warming himself; its H3 two suits of
        armour guarding the trophy of swords; for every shared content."""
        for name, (h, _) in contents(KEY).items():
            for code, piece, hook in (("H1", "phone_chateau", "scene_narrow"), ("H2", "phone_salon", "scene_under"),
                                      ("H3", "phone_armoury", "scene_under")):
                draw = {"H1": SET.h1_narrow, "H2": SET.h2_narrow, "H3": SET.h3_narrow}[code]
                with mock.patch.object(A, piece, wraps=getattr(A, piece)) as scene:
                    p, pixels, _ = D.sprites(SET, lambda: draw(h, False), hook)
                self.assertTrue(scene.called, (name, code))
                xs, ys = [x for x, _ in pixels], [y for _, y in pixels]
                self.assertLessEqual(min(xs), 12, (name, code))
                self.assertGreaterEqual(max(xs), 168, (name, code))
                self.assertGreaterEqual(max(ys) - min(ys) + 1, 48, (name, code))

    def test_the_valance_hangs_under_the_frieze_and_parts_round_the_months_mark(self):
        """Every header hangs its valance of velvet swags in the rows under the frieze; as its month's design the
        swags part round the month's mark and its scrolls, and kept all year they run on across the top centre."""
        held = SET.on(D.months_day(SET))
        for code in ("H1", "H2", "H3"):
            for design, parted in ((held, True), (SET, False)):
                p, pixels, _ = D.sprites(design, lambda: getattr(design, code.lower())(HEADER, False, True), "garland")
                self.assertTrue(pixels, code)
                self.assertTrue(all(A.TOP <= y <= A.TOP + A.SWAG + 3 for _, y in pixels), code)
                centre = any(p.w // 2 - 4 <= x <= p.w // 2 + 4 for x, _ in pixels)
                self.assertEqual(centre, not parted, (code, design.marked))


class Footers(unittest.TestCase):
    def test_every_footer_stands_on_the_carpet_with_the_emblem_after_its_last_cell(self):
        """Every footer stands on the red carpet's border under a gilt rod along its foot, laid on a layer of its own;
        a title block hangs the chateau's emblem after its last cell where its cells leave it the room, and its sconces
        burn by night; a balustrade rises behind the carpet where the cells leave the wall free."""
        _, f = contents(KEY)["repository"]
        for night in (False, True):
            with mock.patch.object(F, "emblem", wraps=F.emblem) as mark, \
                    mock.patch.object(F, "balustrade", wraps=F.balustrade) as rail:
                p = SET.f1(f, night)
            (call,) = mark.call_args_list
            self.assertGreater(call.args[1][0], max(b[2] for b in p.words), (night, "after the way back up"))
            self.assertTrue(call.args[1][3], (night, "with its sconces"))
            self.assertTrue(rail.called, night)
            rod = [c for (x, y), c in p.layers["foot"].items() if c in GOLD]
            self.assertGreater(len(rod), p.w // 2, (night, "the gilt rod"))
            flames = {c for c in p.layers["base"].values() if c in FLAME}
            self.assertTrue(flames, (night, "the sconces burn"))


class Links(unittest.TestCase):
    def test_a_link_button_is_red_velvet_in_gilt_beads_with_a_sprite_of_its_own(self):
        """A link button is red velvet by day and wine by night in a rim of gilt, a string of gilt beads along its top
        edge, and the sprite at its start is one of the banquet's things, a different one for each of four buttons."""
        sprites = {tuple(SET.link_icon(i, False, "#000000")[0]) for i in range(4)}
        self.assertEqual(len(sprites), 4)
        for night in (False, True):
            p = SET.link_button("Issues", 0, night)
            fill, edge, ink, _ = SET.link_colours(night)
            self.assertGreaterEqual(contrast(ink, fill), 4.5, night)
            beads = [c for (x, y), c in p.layers["base"].items() if y == 1]
            self.assertTrue(beads and set(beads) <= GOLD, night)


class Badges(unittest.TestCase):
    def test_a_string_of_gilt_beads_lies_along_every_badges_top_two_rows_with_the_letters_under_it(self):
        for style in BADGE_STYLES:
            drawn = [SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                       SET.badge_states()["green"])]
            drawn += [SET.plate_badge(style, "License", "MIT", "scale", mode) for mode in ("day", "night")]
            for p in drawn:
                rows = {c for (x, y), c in p.layers["base"].items() if y in (0, 1)}
                self.assertTrue(rows and rows <= GOLD, (style, rows - GOLD))
                self.assertTrue(all(y >= TOP for _, _, _, y, _ in p.uses["base"]), "the letters sit under the band")

    def test_a_counters_numerals_hold_4_5_on_their_tiles(self):
        for night in (False, True):
            q = Pix(20, 20)
            SET.counter_cell(q, 2, 2, night)
            face = q.layers["base"][(7, 8)]
            self.assertGreaterEqual(contrast(SET.counter_ink(night, False), face), 4.5, night)
            self.assertGreaterEqual(contrast(SET.counter_ink(night, True), face), 2.0, night)


class Games(unittest.TestCase):
    def test_the_boards_and_the_podium_are_cut_from_the_chateaus_own_stuffs(self):
        """The boards are polished white marble and mahogany parquet in a gilt frame of beads, and the Hall's podium
        is veined white marble, crenellated: the chateau's own tones, never those the hand lends every design."""
        lent = set(MATRIX.ramp("flame")) | set(MATRIX.ramp("moon")) | set(MATRIX.body) | set(MATRIX.muted)
        lent |= {c for skin in ("skin0", "skin1", "skin2") for c in MATRIX.ramp(skin)}
        for night in (False, True):
            light, dark = SET.game_squares(night)
            frame, style = SET.game_frame(night)
            podium = SET.game_podium(night)
            self.assertEqual((light.ramp, light.grain), (RAMP["marble"], "satin"))
            self.assertEqual((dark.ramp, dark.grain), (RAMP["wood"], "wood"))
            self.assertEqual((frame.ramp, style), (RAMP["gold"], "gilt"))
            self.assertEqual((podium.stuff.ramp, podium.stuff.grain), (RAMP["marble"], "stone"))
            self.assertEqual(podium.style, "crenels")
            for stuff in (light, dark, frame, podium.stuff):
                self.assertFalse(set(stuff.ramp) & lent, stuff)


if __name__ == "__main__":
    unittest.main()
