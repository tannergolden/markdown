# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""brain's own rules, which the checks every set shares cannot know: every header holds the brain in its jar, or
where no jar has room the jar drawn small, the lab lit by day and dark by night; the floor, the jar and the
oscilloscope keep two units clear of every word; the brain fits its glass at every size and is cut by its two deep
fissures; the console shows a face for every mood, all five in turn in a wide moving header and the happy one held
still; a sheet of words carries only faint specks; a written colour keeps its family among its badges; and its
boards and podium are the lab's own stuffs."""
from __future__ import annotations

import re
import unittest
from unittest import mock

from tests import support
from tests.unit.test_holiday_sets import contents

from domain import pixelthemes
from domain.canvas import DARK, DAY
from domain.holidays.designs.badges import nearest
from domain.holidays.pixel import Pix
from domain.holidays.pixel.shade import luminance
from domain.palette import PALETTE
from domain.pixelthemes.brain import brain as BR
from domain.pixelthemes.brain import lab as LB
from domain.pixelthemes.brain import mood as MD
from domain.pixelthemes.brain import scenes as SC
from domain.pixelthemes.brain import sheet as S
from domain.pixelthemes.brain.palette import DAY_SKY, NIGHT_SKY, RAMP, TOKENS, X

support.install()
KEY = "brain"
SET = pixelthemes.drawn_by(KEY)
HEADERS = ("H1", "H2", "H3")


def near(p: Pix, x: float, y: float, margin: int = 2) -> bool:
    """Whether the cell (x, y) comes within `margin` units of any word on `p`."""
    x, y = int(x), int(y)
    return not p.clear_of_words(x - margin, y - margin, x + 1 + margin, y + 1 + margin)


def colours(p: Pix) -> set:
    """Every colour drawn on `p`, in pixels, on any of its layers."""
    return {c.split(":")[0] for layer in p.layers.values() for c in layer.values()}


def every_header():
    """Every header a set is held to, (where, header, code, wide, theme): the kit's own lines, each sample, the most
    a page can say and the least, wide and on a phone, by day and by night."""
    for name, (h, _) in contents(KEY).items():
        for code in HEADERS:
            for wide in (True, False):
                for theme in (DAY, DARK):
                    yield (name, code, wide, theme["name"]), h, code, wide, theme


class TheLab(unittest.TestCase):
    def test_every_header_holds_the_brain_in_its_jar_or_where_none_fits_the_jar_drawn_small(self):
        for where, h, code, wide, theme in every_header():
            with mock.patch.object(BR, "brain", wraps=BR.brain) as full, \
                    mock.patch.object(LB, "tiny_jar", wraps=LB.tiny_jar) as small:
                SET.header(code, h, theme, wide, False)
            self.assertTrue(full.called or small.called, where)

    def test_by_day_the_lab_is_lit_and_by_night_its_lamps_are_out_and_its_titles_burn_amber(self):
        h, _ = contents(KEY)["repository"]
        lit_bulb = RAMP["brass"][6].upper()
        for code in HEADERS:
            for wide in (True, False):
                day = SET.header(code, h, DAY, wide, False).upper()
                dark = SET.header(code, h, DARK, wide, False).upper()
                self.assertIn(DAY_SKY[0].upper(), day, (code, wide))
                self.assertNotIn(NIGHT_SKY[0].upper(), day, (code, wide))
                self.assertIn(NIGHT_SKY[0].upper(), dark, (code, wide))
                self.assertNotIn(DAY_SKY[0].upper(), dark, (code, wide))
                self.assertIn(lit_bulb, day, (code, wide))
                self.assertNotIn(lit_bulb, dark, (code, wide))
                self.assertIn(X["title_night"].upper(), dark, (code, wide))


class ClearOfWords(unittest.TestCase):
    def test_the_floor_never_comes_within_two_units_of_a_word(self):
        for night in (False, True):
            p = Pix(415, 132)
            p.text(150, 120, "A WORD LOW OVER THE FLOOR", "#000000", "35")
            SC.floor(p, 5, 410, 128, 6, night, 3, False)
            cells = [q for layer in p.layers.values() for q in layer]
            self.assertTrue(cells, night)
            self.assertFalse([q for q in cells if near(p, *q)], night)
            # the tiles and the skirting are laid as rectangles: every cell of each keeps clear too
            rects = [tuple(map(int, m)) for m in re.findall(
                r'<rect x="(\d+)" y="(\d+)" width="(\d+)" height="(\d+)"', "".join(p.shapes["base"]))]
            self.assertTrue(rects, night)
            for x, y, w, h in rects:
                for yy in range(y, y + h):
                    self.assertFalse([xx for xx in range(x, x + w) if near(p, xx, yy)], (night, x, y, w, h))

    def test_the_jar_and_the_oscilloscope_keep_two_units_clear_of_every_word(self):
        jar, scope = LB.jar, LB.scope
        boxes = []

        def jar_at(p, cx, foot, w, *a, **k):
            boxes.append((p, LB.jar_box(cx, foot, w)))
            return jar(p, cx, foot, w, *a, **k)

        def scope_at(p, x0, y0, w, h, *a, **k):
            boxes.append((p, (x0, y0, x0 + w, y0 + h)))
            return scope(p, x0, y0, w, h, *a, **k)

        with mock.patch.object(LB, "jar", jar_at), mock.patch.object(LB, "scope", scope_at):
            for where, h, code, wide, theme in every_header():
                SET.header(code, h, theme, wide, False)
        self.assertTrue(boxes)
        for p, (x0, y0, x1, y1) in boxes:
            self.assertTrue(p.clear_of_words(x0 - 2, y0 - 2, x1 + 2, y1), (x0, y0, x1, y1))


class TheBrain(unittest.TestCase):
    def test_at_every_width_a_jar_is_drawn_the_brain_fits_inside_its_glass(self):
        for w in range(LB.LEAST, 72, 2):
            z = LB.jar_size(w)
            bw, bh = BR.extent(z["k"])
            self.assertLessEqual(bw, w - 2, w)
            self.assertLessEqual(bh + 1, z["glass"], w)

    def test_the_brain_is_cut_by_its_two_deep_fissures_from_its_crown_to_its_temporal_lobe(self):
        for k in (0.2, 0.36, 0.52, 1.0):
            s = BR.shape(k)
            self.assertTrue(s.fissure, k)
            self.assertLessEqual(s.fissure, s.cerebrum, k)
            # the central sulcus comes down from the crown, and the Sylvian fissure runs back from the temporal pole
            self.assertLess(min(y for _, y in s.fissure), s.h * 0.1, k)
            self.assertGreater(max(y for _, y in s.fissure), s.h * 0.55, k)
            self.assertLess(min(x for x, _ in s.fissure), s.w * 0.3, k)


class TheMoods(unittest.TestCase):
    def test_every_mood_has_a_face_of_its_own_thirteen_by_seven(self):
        self.assertEqual(set(MD.FACES), set(MD.MOODS))
        self.assertEqual(MD.STILL, "happy")
        self.assertEqual(len({tuple(art) for art in MD.FACES.values()}), len(MD.MOODS))
        for mood, art in MD.FACES.items():
            self.assertEqual((len(art), {len(row) for row in art}), (7, {13}), mood)
            self.assertLessEqual(set("".join(art)), set(".#ow"), mood)
            for night in (False, True):
                self.assertIn(MD.ink(mood, night).upper(), TOKENS, (mood, night))

    def test_a_moving_screen_shows_every_face_in_turn_and_a_still_one_the_happy_face(self):
        for night in (False, True):
            moving, still = Pix(120, 60), Pix(120, 60)
            MD.face(night, True)(moving, 10, 10, 32, 18)
            MD.face(night, False)(still, 10, 10, 32, 18)
            placed = {name: [u[1] for u in uses] for name, uses in moving.uses.items() if uses}
            turns = sorted(moving.meta[name][2][1:3] for name in placed)
            self.assertEqual(turns, [MD.window(i) for i in range(len(MD.MOODS))], night)
            kept = [name for name in placed if moving.meta[name][2][4]]
            self.assertEqual([moving.meta[name][2][1:3] for name in kept], [MD.window(MD.MOODS.index(MD.STILL))])
            held = [u[1] for uses in still.uses.values() for u in uses]
            self.assertEqual(held, [still.syms[("face", MD.STILL, night)]], night)

    def test_only_a_wide_moving_header_turns_through_the_moods(self):
        h, _ = contents(KEY)["repository"]
        for theme in (DAY, DARK):
            self.assertEqual(SET.header("H2", h, theme, True, True).count(f'dur="{MD.LOOP:g}s"'),
                             2 * len(MD.MOODS) + 1, theme["name"])
            self.assertNotIn(f'dur="{MD.LOOP:g}s"', SET.header("H2", h, theme, True, False), theme["name"])


class TheSheets(unittest.TestCase):
    def test_a_sheet_of_words_carries_only_faint_specks_that_hold_still(self):
        for night in (False, True):
            p = Pix(415, 100)
            S.motes(p, 6, 6, 409, 94, 60, night, faint=True)
            dim = {RAMP["room"][4], RAMP["room"][5], RAMP["arc"][1]} if night else {RAMP["sage"][4]}
            self.assertTrue(colours(p), night)
            self.assertLessEqual(colours(p), dim, night)
            self.assertFalse([name for name in p.layers if p.meta[name][2]], night)


class TheBadges(unittest.TestCase):
    def test_a_written_colour_keeps_its_family(self):
        swatches = SET.badge_swatches()
        for colour, swatch in (("red", "tissue"), ("pink", "tissue"), ("teal", "fluid"), ("green", "aqua"),
                               ("navy", "enamel"), ("sky", "blue"), ("gold", "gold"), ("yellow", "gold"),
                               ("orange", "amber"), ("brown", "nixie"), ("white", "cream"), ("black", "room"),
                               ("gray", "chrome"), ("slate", "steel"), ("purple", "arc"), ("lavender", "lilac"),
                               ("sand", "sage")):
            self.assertEqual(nearest(PALETTE[colour], swatches), swatch, colour)


class TheGames(unittest.TestCase):
    def test_its_boards_are_the_labs_floor_by_day_and_the_jars_glass_by_night(self):
        day, dark = SET.game_board(False), SET.game_board(True)
        self.assertEqual((day["light_stuff"].grain, day["dark_stuff"].grain, day["style"]), ("tile", "metal", "iron"))
        self.assertEqual((dark["light_stuff"].grain, dark["dark_stuff"].grain, dark["style"]),
                         ("glass", "metal", "iron"))
        self.assertEqual(day["light_stuff"].ramp, RAMP["sage"])
        self.assertEqual(dark["light_stuff"].ramp, RAMP["fluid"])
        for b in (day, dark):
            self.assertGreater(luminance(b["light"]), luminance(b["dark"]))

    def test_its_podium_is_the_machines_cabinets_their_gauges_brass_by_day_and_amber_by_night(self):
        day, dark = SET.game_podium(False), SET.game_podium(True)
        self.assertEqual((day.style, day.stuff.grain, day.stuff.ramp, day.trim.base),
                         ("shields", "metal", RAMP["enamel"], RAMP["brass"][4]))
        self.assertEqual((dark.style, dark.stuff.grain, dark.trim.base), ("shields", "metal", RAMP["nixie"][4]))


class ThePalette(unittest.TestCase):
    def test_every_ramp_runs_dark_to_light(self):
        for name, ramp in RAMP.items():
            self.assertEqual(len(ramp), 7, name)
            shades = [luminance(c) for c in ramp]
            self.assertEqual(shades, sorted(shades), name)


if __name__ == "__main__":
    unittest.main()
