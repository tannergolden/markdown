# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Rain design's own rules, which the checks every design of a collection shares cannot know: by night the sheet is
the terminal's glass and its titles glow, by day the printout's greenbar and its titles are struck in dots, and the
corridor's door blazes white only by night; every stream of the code steps down a glyph every 0.08 to 0.15 seconds, the
man in the corridor stirs on a figure's loop and the tower's light blinks after dark, only in a wide moving header; each
header's hero stands where the words leave it, the room and the city on an H1, the corridor of code with the man in the
long coat on an H2 and the great tower rising the strip's full height on an H3, and on a phone the H1's room and city
and the H2's and H3's heroes stand under the words; the footers stand on the keyboard with the terminal after their last
cell; the links are keys of glass by night and strips of printout by day; a stream of the code runs along every badge's
top two rows with the letters under it; a counter's numerals hold 4.5:1 on their cells; a contributor is a floppy disk
with their initials on its label; and the games are built of the printout and the terminal's beige plastic. The checks
every design of a collection shares run here too."""
from __future__ import annotations

import re
import unittest
from unittest import mock

from tests.unit import design_checks as D
from tests.unit.test_holiday_sets import contents

from domain.canvas import DARK, DAY
from domain.collections.matrix_rain import SET
from domain.collections.matrix_rain import art as A
from domain.collections.matrix_rain.palette import RAMP
from domain.holidays.designs.badges import STYLES as BADGE_STYLES, TOP
from domain.holidays.designs.materials import Podium, Stuff
from domain.holidays.pixel import Pix, contrast, num

KEY = SET.key
FLAME, GLASS, PAPER, RIBBON = RAMP["flame"], RAMP["glass"], RAMP["paper"], RAMP["ribbon"]
HEADERS: dict = {}
# A stream's steps: the values a fall's translation steps through, and how long the whole fall takes.
FALL = re.compile(r'<animateTransform attributeName="transform" type="translate" values="([^"]*)" dur="([\d.]+)s"')


def header(code: str, name: str, night: bool, wide: bool = True, motion: bool = True) -> str:
    """A header's file for one of the shared contents, drawn once and kept."""
    key = (code, name, night, wide, motion)
    if key not in HEADERS:
        h, _ = contents(KEY)[name]
        HEADERS[key] = SET.header(code, h, DARK if night else DAY, wide, motion)
    return HEADERS[key]


def calls(fn: str, draw) -> list:
    """The calls `draw()` makes to the art function `fn`: (args, kwargs), the canvas left out."""
    with mock.patch.object(A, fn, wraps=getattr(A, fn)) as spy:
        draw()
    return [(c.args[1:], c.kwargs) for c in spy.call_args_list]


class Shared(D.Shared, unittest.TestCase):
    """The checks every design of a collection shares, over Rain kept all year."""

    SET = SET
    ART = A
    PIECES = ("falling", "terminal", "city", "corridor", "stranger", "tower")
    FOOTINGS = ("_footed",)


class GlassAndPaper(unittest.TestCase):
    def test_by_night_the_sheet_is_glass_and_its_titles_glow_by_day_paper_and_struck_in_dots(self):
        """By night the sheet is the terminal's glass, scanned in lines, and a title is lit in phosphor with its light
        blooming round it; by day the sheet is greenbar and a title is struck in the dots of a printer's head, with no
        glow."""
        for code in ("H1", "H2", "H3"):
            day, night = header(code, "repository", False), header(code, "repository", True)
            self.assertIn('<pattern id="pg"', day, (code, "the greenbar"))
            self.assertIn('<pattern id="ps"', night, (code, "the glass's scan lines"))
            self.assertIn('<pattern id="paph', night, (code, "the title scanned in phosphor"))
            self.assertIn(f'stroke="{FLAME[3]}" stroke-opacity', night, (code, "its light blooming"))
            self.assertNotIn(f'stroke="{FLAME[3]}" stroke-opacity', day, (code, "no glow by day"))
            self.assertNotIn('<pattern id="paph', day, (code, "struck in dots by day"))

    def test_the_corridors_door_blazes_white_only_by_night(self):
        h, _ = contents(KEY)["repository"]
        night = calls("corridor", lambda: SET.h2(h, True, True))
        self.assertEqual(len(night), 1)
        self.assertIn(FLAME[6], header("H2", "repository", True), "the door blazes")
        self.assertNotIn(FLAME[6], header("H2", "repository", False), "by day the door is bare paper in a frame")


class Motion(unittest.TestCase):
    def test_every_stream_of_the_code_steps_a_glyph_every_eight_to_fifteen_hundredths_of_a_second(self):
        """Down the sheet, the corridor's walls and the tower's sky alike, the code falls a glyph at a time, every
        0.08 to 0.15 seconds, in a wide moving header only."""
        for code in ("H1", "H2", "H3"):
            moving = header(code, "repository", True)
            falls = FALL.findall(moving)
            paces = [float(dur) / len(values.split(";")) for values, dur in falls if values.startswith("0 0;0 8")]
            self.assertTrue(paces, code)
            self.assertTrue(all(0.08 - 1e-9 <= pace <= 0.15 + 1e-9 for pace in paces), (code, paces))
            self.assertNotIn("<animate", header(code, "repository", True, motion=False), code)
            self.assertNotIn("<animate", header(code, "repository", True, wide=False, motion=False), code)

    def test_the_man_in_the_corridor_stirs_on_a_figures_loop_and_the_towers_light_blinks_after_dark(self):
        self.assertTrue(4 <= A.STIR <= 8)
        self.assertIn(f'dur="{num(A.STIR)}s"', header("H2", "repository", False), "his coat stirs")
        h, _ = contents(KEY)["repository"]
        p = SET.h3(h, True, True)
        blinks = [n for n in p.layers if p.meta[n][2] and p.meta[n][2][0] == "blink" and p.layers[n]]
        self.assertTrue(blinks, "the spire's light blinks after dark")
        day = SET.h3(h, False, True)
        self.assertFalse([n for n in day.layers if day.meta[n][2] and day.meta[n][2][0] == "blink" and day.layers[n]])


class Heroes(unittest.TestCase):
    def test_an_h2_stands_the_corridor_of_code_with_the_man_in_it_where_the_words_leave_it(self):
        """On every content's H2 the corridor stands at the right from under the top band down to the floor, two
        units and more clear of every word, the code falling down its walls and the man in the long coat standing in
        it before its door."""
        for name, (h, _) in contents(KEY).items():
            with mock.patch.object(A, "corridor", wraps=A.corridor) as room, \
                    mock.patch.object(A, "stranger", wraps=A.stranger) as man:
                p = SET.h2(h, False, True)
            (call,) = room.call_args_list
            x0, y0, x1, g = call.args[1:5]
            self.assertGreaterEqual(x0, 300, name)
            self.assertEqual(y0, 16, name)
            self.assertTrue(p.clear_of_words(x0 - 2, y0, x1 + 1, g + 1), name)
            self.assertEqual(man.call_count, 1, name)

    def test_an_h3_stands_the_great_tower_rising_the_strips_full_height(self):
        """On every content's H3 the great tower stands at the strip's right, its foot on the ground and its spire's
        tip at row eighteen, under the top band, so it rises the strip's full height; the code passes behind it."""
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "tower", wraps=A.tower) as tower:
                    SET.h3(h, night, True)
                (call,) = tower.call_args_list
                x0, x1, top, g = call.args[1:5]
                self.assertEqual(top, 18, (name, night))
                self.assertGreaterEqual(g - top, 52, (name, night))
                self.assertGreaterEqual(x0, 340, (name, night))

    def test_a_phone_stands_the_room_and_the_city_under_an_h1s_words_and_each_hero_under_an_h2s_and_an_h3s(self):
        """A phone's H1 stands the terminal with the hacker asleep beside it and the city of code across its width
        under its words, forty-eight rows and more; a phone's H2 the corridor with the man in it, and its H3 the great
        tower; by day and by night, for every shared content."""
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                what = (name, night)
                _, pixels, _ = D.sprites(SET, lambda: SET.h1_narrow(h, night), "scene_narrow")
                xs, ys = [x for x, _ in pixels], [y for _, y in pixels]
                self.assertLessEqual(min(xs), 7, what)
                self.assertGreaterEqual(max(xs), 170, what)
                self.assertGreaterEqual(max(ys) - min(ys) + 1, 48, what)
                for fn in ("terminal", "city"):
                    self.assertEqual(len(calls(fn, lambda: SET.h1_narrow(h, night))), 1, (what, fn))
                for fn in ("corridor", "stranger"):
                    self.assertEqual(len(calls(fn, lambda: SET.h2_narrow(h, night))), 1, (what, fn))
                self.assertEqual(len(calls("tower", lambda: SET.h3_narrow(h, night))), 1, what)


class Footers(unittest.TestCase):
    def test_every_footer_stands_on_the_keyboard_with_the_terminal_after_its_last_cell(self):
        """Along every footer's foot lies the keyboard, its keys' lit tops along its row; and a title block whose
        cells leave it room has the terminal standing after its last cell, the code on its glass."""
        for name, (_, f) in contents(KEY).items():
            for draw in (SET.f1, SET.f2, SET.f1_narrow, SET.f2_narrow):
                for night in (False, True):
                    svg = draw(f, night).svg("f", "f", still=True)
                    top = RAMP["case"][4] if night else RAMP["beige"][5]
                    self.assertIn(top, svg, (name, draw.__name__, night, "the keys' lit tops"))
        _, f = contents(KEY)["repository"]
        with mock.patch.object(A, "screen", wraps=A.screen) as glass:
            p = SET.f1(f, False)
        (call,) = glass.call_args_list
        self.assertGreater(call.args[1], max(b[2] for b in p.words), "after the way back up")


class Links(unittest.TestCase):
    def test_a_link_is_a_key_of_glass_by_night_and_a_strip_of_printout_by_day(self):
        night, day = SET.link_button("Issues", 0, True), SET.link_button("Issues", 0, False)
        self.assertEqual(night.get(night.w - 4, 1), FLAME[4], "the power light burns")
        self.assertEqual(night.get(5, 1), RAMP["case"][4], "the case's lip over the glass")
        self.assertEqual([day.get(x, 2) for x in range(2, 12, 2)], [PAPER[6]] * 5, "the perforation along the top")
        for n in (False, True):
            fill, edge, ink, shade = SET.link_colours(n)
            self.assertGreaterEqual(contrast(ink, fill), 4.5, n)
        icons = {tuple(SET.link_icon(i, False, "#000000")[0]) for i in range(4)}
        self.assertEqual(len(icons), 4, "each link its own icon")


class Badges(unittest.TestCase):
    def test_a_stream_of_the_code_runs_along_every_badges_top_two_rows_with_the_letters_under_it(self):
        stream = set(FLAME[:5]) | {FLAME[6], GLASS[0]}
        for style in BADGE_STYLES:
            drawn = [SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                       SET.badge_states()["green"])]
            drawn += [SET.plate_badge(style, "License", "MIT", "scale", mode) for mode in ("day", "night")]
            for p in drawn:
                rows = {c for (x, y), c in p.layers["base"].items() if y in (0, 1)}
                self.assertTrue(rows and rows <= stream, (style, rows - stream))
                self.assertTrue(all(y >= TOP for _, _, _, y, _ in p.uses["base"]), "the letters sit under the band")

    def test_a_counters_numerals_hold_4_5_on_their_cells(self):
        for night in (False, True):
            q = Pix(20, 20)
            SET.counter_cell(q, 2, 2, night)
            face = q.layers["base"][(7, 8)]
            self.assertGreaterEqual(contrast(SET.counter_ink(night, False), face), 4.5, night)
            self.assertGreaterEqual(contrast(SET.counter_ink(night, True), face), 2.0, night)


class Elements(unittest.TestCase):
    def test_a_contributor_is_a_floppy_disk_with_their_initials_on_its_label(self):
        """Each contributor is the floppy disk their code was kept on, the shells moulded in the plastics of DISKS by
        turns, the initials written on the white label in the ribbon's ink at 4.5:1 and more, by day and by night, and
        a bot's label carrying one of the code's glyphs; the schematic's free corner holds the terminal itself, the
        code on its glass."""
        for night in (False, True):
            shells = set()
            for i, person in enumerate(({"initials": "IV"}, {"initials": "TO"}, {"initials": "WC"}, {})):
                p = Pix(20, 20)
                SET.avatar(p, 10, 10, i, person, night)
                label = p.get(5, 10)
                shells.add(p.get(4, 4))
                inked = [(x, y) for c, _, x, y, _ in p.uses["base"] if c == RIBBON[0]]
                self.assertTrue(inked and all(5 <= x < 16 and 10 <= y < 17 for x, y in inked), (night, i))
                self.assertGreaterEqual(contrast(RIBBON[0], label), 4.5, (night, i))
            self.assertEqual(len(shells), len(A.DISKS), (night, "each shell its own plastic"))
        self.assertEqual(SET.ornament("schematic", None, 0, 0, False), (len(A.MONITOR[0]), len(A.MONITOR)))
        with mock.patch.object(A, "screen", wraps=A.screen) as glass:
            SET.ornament("schematic", Pix(40, 40), 2, 2, True)
        self.assertEqual(glass.call_count, 1, "the code on the terminal's glass")


class Games(unittest.TestCase):
    def test_the_boards_and_the_podium_are_of_the_printout_and_the_terminals_plastic(self):
        """The board's light squares are the printout's paper, mottled, and its dark the ribbon's green with the
        sheen of fresh ink, a tone down by night; its frame is the terminal's beige plastic; and the Hall's winners
        stand on plain blocks of the beige case, brushed and screwed at their corners."""
        for night in (False, True):
            light, dark = SET.game_squares(night)
            self.assertEqual((light.ramp, light.grain), (PAPER, "vellum"), night)
            self.assertEqual((dark.ramp, dark.grain), (RIBBON, "satin"), night)
            self.assertEqual(SET.game_frame(night), (Stuff(RAMP["beige"], 3), "plain"))
            self.assertEqual(SET.game_podium(night), Podium(Stuff(RAMP["beige"], 4, "metal")))
        self.assertGreater(SET.game_squares(False)[0].at, SET.game_squares(True)[0].at, "dimmer by night")


if __name__ == "__main__":
    unittest.main()
