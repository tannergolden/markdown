# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Harvest design's tests: the checks every design of a collection shares, run over Harvest, and its own rules,
which the shared checks cannot know: the day's ashen sky and the night's storm never meet in a file, and by night
alone the lightning lights the clouds round it, the sky flashes as it strikes and the pods glow; a title is glass
tubes of phosphor fluid, a little empty glass at the top of each and the fluid's surface a bright line under it,
outlined dark, its strokes capped in metal and bubbles rising through it in a moving header, the glass a tone down
and the fluid brighter by night; the clouds drift, the lightning strikes twice on its loop, the harvester draws a pod
out of its slot and the machines' eyes blink, each on its own cadence; each header's hero stands where it should, the
tower of pods at the left of an H1 and the harvester at its right, the awakening at the right of an H2 risen the full
height of its sky with the doctor let down from the dark, and the pod tree at the right of an H3 rising the strip's
full height, hung with more pods the taller the strip; a phone's H1 holds the whole of the fields under its words, and
its H2 and H3 their heroes whatever the words say; every footer stands on the trench's cables, with a pod in its
socket after a title block's last cell, glowing by night; a link button carries ribbed conduit along its top and each
of the four takes its own sprite; a badge's top two rows are ribbed conduit; a counter's numerals hold 4.5:1 on their
screens; and the games' boards and podium are the machines' own stuffs."""
from __future__ import annotations

import re
import unittest
from unittest import mock

from tests.unit import design_checks as D
from tests.unit.test_holiday_sets import contents

from domain.banners.content import Header
from domain.canvas import DARK, DAY
from domain.collections.matrix_harvest import SET
from domain.collections.matrix_harvest import art as A
from domain.collections.matrix_harvest.palette import NIGHT_SKY, RAMP, X
from domain.holidays.designs.badges import STYLES as BADGE_STYLES, TOP
from domain.holidays.designs.materials import Podium, Stuff
from domain.holidays.pixel import Pix, contrast

KEY = SET.key
HEADER = Header(tone="standard", holiday=KEY)
CONTENTS = contents(KEY)
FLAME, GLASS, METAL, CONDUIT = (RAMP[n] for n in ("flame", "glass", "metal", "conduit"))
ASH = {c.upper() for c in RAMP["ash"]} | {X["haze_day"].upper()}
STORM = {c.upper() for c in RAMP["storm"]} | {c.upper() for c in NIGHT_SKY}
DRAWN: dict = {}


def header(code, theme, wide=True, motion=True) -> str:
    """The kit's own header in Harvest, drawn once and kept."""
    key = (code, theme["name"], wide, motion)
    if key not in DRAWN:
        DRAWN[key] = SET.header(code, HEADER, theme, wide, motion)
    return DRAWN[key]


def hexes(svg: str) -> set:
    return {c.upper() for c in re.findall(r"#[0-9A-Fa-f]{6}", svg)}


class Shared(D.Shared, unittest.TestCase):
    SET = SET
    ART = A
    PIECES = ("tower", "far_towers", "crown_cables", "horizon", "fields", "harvester", "storm", "awakening",
              "big_pod", "doctor", "pod_tree", "small_pod", "tube_title")
    FOOTINGS = ("_footed",)


class Night(unittest.TestCase):
    def test_the_days_ashen_sky_and_the_nights_storm_never_meet_in_a_file(self):
        """No tone of the ashen sky or of the far fields' haze by day comes into a night's file, and none of the
        storm's violet into a day's: every header, wide and on a phone, moving and still, and every footer."""
        _, f = CONTENTS["repository"]
        for code in ("H1", "H2", "H3"):
            for wide, motion in ((True, True), (True, False), (False, False)):
                what = (code, wide, motion)
                self.assertFalse(STORM & hexes(header(code, DAY, wide, motion)), what)
                self.assertFalse(ASH & hexes(header(code, DARK, wide, motion)), what)
        for code in ("F1", "F2"):
            for wide in (True, False):
                self.assertFalse(STORM & hexes(SET.footer(code, f, DAY, wide, False)), (code, wide))
                self.assertFalse(ASH & hexes(SET.footer(code, f, DARK, wide, False)), (code, wide))

    def test_by_night_alone_the_lightning_lights_the_clouds_the_sky_flashes_and_the_pods_glow(self):
        """By night the lightning lights the clouds round it as it strikes, and in a moving header the whole sky flashes
        faintly with it; by night every header's pods glow round them, flickering. None of it by day."""
        light, flash = f'<g fill="{FLAME[3]}" fill-opacity=".12">', f'fill="{FLAME[3]}" fill-opacity=".05"/>'
        for code in ("H1", "H2", "H3"):
            self.assertIn(light, header(code, DARK), code)
            self.assertIn(flash, header(code, DARK), code)
            self.assertNotIn(flash, header(code, DARK, motion=False), (code, "the still file holds still"))
            self.assertNotIn(light, header(code, DAY), code)
            self.assertNotIn(flash, header(code, DAY), code)
            self.assertFalse(D.flickering(D.wide(SET, code)(HEADER, False, True)), (code, "no glow flickers by day"))
            self.assertTrue(D.flickering(D.wide(SET, code)(HEADER, True, True)), (code, "the pods glow by night"))


class Titles(unittest.TestCase):
    def test_a_title_is_glass_tubes_of_phosphor_fluid_a_little_empty_glass_at_the_top(self):
        """Row by row down a letter, a little empty glass at the top of the tube, the fluid's surface a bright line
        under it, and the fluid bright under its surface and denser toward the foot; by night the glass a tone down and
        the surface white-hot."""
        for night, glass, surface in ((False, GLASS[5], FLAME[5]), (True, GLASS[3], FLAME[6])):
            self.assertEqual([A._fluid(r, 0, 4, night) for r in (0, 2, 3)], [glass, glass, surface], night)
            self.assertEqual([A._fluid(r, 0, 4, night) for r in (8, 12, 24)], [FLAME[4], FLAME[3], FLAME[2]], night)

    def test_every_letter_is_outlined_dark_capped_in_metal_and_bubbling_in_a_moving_header(self):
        """Every letter is outlined in the glass's darkest tones, deeper by night; the ends of its strokes are capped
        in dark metal; and in a moving header bubbles rise through the tubes on the three twinkling phases, which the
        still file holds still."""
        for night, outline in ((False, GLASS[1]), (True, GLASS[0])):
            p = Pix(415, 60)
            A.tube_title(p, 10, 20, "HARVEST", night, 4, True)
            self.assertIn(outline, {u[0] for u in p.uses["base"]}, night)
            self.assertTrue(set(p.layers["caps"].values()) & set(METAL[:4]), (night, "the caps"))
            self.assertEqual({L for L in p.layers if L.startswith("tw")}, {"tw0", "tw1", "tw2"}, night)
            still = Pix(415, 60)
            A.tube_title(still, 10, 20, "HARVEST", night, 4, False)
            self.assertFalse([L for L in still.layers if L.startswith("tw")], night)


class Motion(unittest.TestCase):
    def test_the_clouds_drift_the_lightning_strikes_and_the_harvester_plucks_each_on_its_cadence(self):
        """In a moving H1 the clouds drift a stretch every forty seconds and the lightning strikes twice on a
        seven-second loop, at the left and then at the right; the harvester draws a pod out of its slot and away in
        three frames on a six-second loop, held halfway in the still file, and its eyes blink."""
        moving = header("H1", DARK)
        self.assertIn('dur="40s"', moving)
        strikes = re.findall(r'keyTimes="0;([\d.]+);[^"]*" dur="7s"', moving)
        self.assertEqual(strikes, ["0.43", "0.86"])
        p = SET.h1(HEADER, False, True)
        frames = [p.meta[f"hv{f}"][2] for f in range(3)]
        self.assertEqual([(a[0], a[3], a[4]) for a in frames], [("seq", 6.0, False), ("seq", 6.0, True),
                                                                 ("seq", 6.0, False)])
        self.assertTrue(any(p.meta[L][2] and p.meta[L][2][0] == "blink" for L in p.layers), "its eyes blink")

    def test_on_an_h2_the_doctors_eyes_blink_and_on_an_h3_the_pods_glow_by_night(self):
        h2, h3 = SET.h2(HEADER, False, True), SET.h3(HEADER, True, True)
        self.assertTrue(any(h2.meta[L][2] and h2.meta[L][2][0] == "blink" for L in h2.layers), "the doctor's eyes")
        self.assertGreaterEqual(len({L for L in h3.layers if L.startswith("fb")}), 2, "the pods glowing by turns")


class Heroes(unittest.TestCase):
    def test_an_h1_has_the_tower_of_pods_at_the_left_and_the_harvester_at_the_right(self):
        h, _ = CONTENTS["kit"]
        for night in (False, True):
            with mock.patch.object(A, "tower", wraps=A.tower) as tower, \
                    mock.patch.object(A, "harvester", wraps=A.harvester) as harvester:
                SET.h1(h, night, True)
            near, far = tower.call_args_list
            self.assertLess(near.args[1], 40, (night, "the near tower at the left"))
            self.assertGreater(far.args[1], 400, (night, "the tower the harvester clings to at the right"))
            (call,) = harvester.call_args_list
            self.assertGreaterEqual(call.args[1], 296, night)
            self.assertEqual(call.args[5][0], far.args[1], (night, "clinging to that tower"))

    def test_an_h2_has_the_awakening_at_the_right_risen_the_full_height_of_its_sky(self):
        """At the right of every H2 the tower of pods rises into the dark, its crown's cables run up to two rows under
        the top, the pod stands open before it with the sleeper risen out of it, and the doctor is let down over him
        from the top, for every shared content."""
        for name, (h, _) in CONTENTS.items():
            with mock.patch.object(A, "awakening", wraps=A.awakening) as awakening, \
                    mock.patch.object(A, "crown_cables", wraps=A.crown_cables) as cables, \
                    mock.patch.object(A, "doctor", wraps=A.doctor) as doctor:
                p = SET.h2(h, False, True)
            (call,) = awakening.call_args_list
            x0, x1, g = call.args[1:4]
            self.assertGreaterEqual(x0, 296, name)
            self.assertEqual(x1, p.w - A.EDGE - 1, name)
            self.assertGreaterEqual(g - A.TOP, 90, (name, "risen the full height"))
            self.assertEqual(cables.call_args.kwargs["sky"], A.TOP + 2, (name, "the cables up into the dark"))
            self.assertEqual(doctor.call_args.kwargs["sky"], A.TOP + 1, (name, "the doctor let down from the top"))

    def test_an_h3_has_the_pod_tree_rising_the_strips_full_height_hung_with_more_pods_the_taller(self):
        """At the right of every H3 the pod tree stands on the strip's ground, its crown two rows under the top, its
        cables running on up into the dark; the taller the strip, the more boughs it arches out and the more pods hang
        from them."""
        pods = {}
        for name, (h, _) in CONTENTS.items():
            with mock.patch.object(A, "pod_tree", wraps=A.pod_tree) as tree, \
                    mock.patch.object(A, "pod", wraps=A.pod) as pod, \
                    mock.patch.object(SET, "scene", wraps=SET.scene) as scene:
                SET.h3(h, False, True)
            (call,) = tree.call_args_list
            x0, g, top = call.args[1], call.args[3], call.args[6]
            self.assertGreaterEqual(x0, 338, name)
            self.assertEqual(top, A.TOP + 2, (name, "from the top"))
            self.assertEqual(g, scene.call_args.args[2] - 1, (name, "down to the ground on the strip's rule"))
            pods[name] = len(pod.call_args_list)
        self.assertGreater(pods["most"], pods["least"])


class Phones(unittest.TestCase):
    def test_a_phones_h1_has_the_whole_of_the_fields_under_its_words(self):
        """A phone's H1 stands a tower of pods, the harvester at the next tower and the fields to the horizon across its
        width under the words, at least 48 rows tall, for every shared content."""
        for name, (h, _) in CONTENTS.items():
            for night in (False, True):
                with mock.patch.object(A, "phone_fields", wraps=A.phone_fields) as world, \
                        mock.patch.object(A, "harvester", wraps=A.harvester) as harvester, \
                        mock.patch.object(A, "fields", wraps=A.fields) as fields:
                    p, pixels, _ = D.sprites(SET, lambda: SET.h1_narrow(h, night), "scene_narrow")
                self.assertTrue(world.called and harvester.called, (name, night))
                self.assertEqual(fields.call_args.args[1:3], (A.EDGE, p.w - A.EDGE), (name, night, "the fields"))
                xs, ys = [x for x, _ in pixels], [y for _, y in pixels]
                self.assertLessEqual(min(xs), 12, (name, night, "the tower at the left"))
                self.assertGreaterEqual(max(xs), 168, (name, night, "the harvester's tower at the right"))
                self.assertGreaterEqual(max(ys) - min(ys) + 1, 48, (name, night))

    def test_a_phones_h2_and_h3_stand_their_heroes_under_their_words_whatever_they_say(self):
        """Whatever the words, a phone's H2 stands the awakening under them and its H3 the pod tree, each across the
        phone."""
        for code, hero in (("H2", "phone_awakening"), ("H3", "phone_tree")):
            for name, (h, _) in CONTENTS.items():
                with mock.patch.object(A, hero, wraps=getattr(A, hero)) as drawn:
                    _, pixels, _ = D.sprites(SET, lambda: D.phone(SET, code)(h, False), "scene_under")
                self.assertTrue(drawn.called, (code, name))
                xs, ys = [x for x, _ in pixels], [y for _, y in pixels]
                self.assertGreaterEqual(max(ys) - min(ys) + 1, 44, (code, name))
                self.assertGreaterEqual(max(xs) - min(xs), 160, (code, name))


class Footers(unittest.TestCase):
    def test_every_footer_stands_on_the_trenchs_cables_with_a_pod_after_its_last_cell(self):
        """Along every footer's foot runs the trench's heavy cable, lit along its top, a pulse of phosphor in it every
        so often; on a title block whose cells leave it room a pod stands plugged into its socket after the last cell,
        the way back up, and by night it and the pulses burn and flicker on the hand's flame."""
        _, f = CONTENTS["repository"]
        cable = set(CONDUIT) | set(FLAME)
        for night in (False, True):
            with mock.patch.object(A, "socket_pod", wraps=A.socket_pod) as socket:
                p = SET.f1(f, night)
            (call,) = socket.call_args_list
            self.assertGreater(call.args[1], max(b[2] for b in p.words), (night, "after the last cell"))
            self.assertEqual(bool(D.flickering(p)), night, (night, "burning by night"))
            for draw in (SET.f1, SET.f2, SET.f1_narrow, SET.f2_narrow):
                q = draw(f, night)
                trench = [x for x in range(q.w) if any(q.layers["base"].get((x, y)) in cable
                                                       for y in range(q.h - A.EDGE, q.h - 1))]
                self.assertGreater(len(trench), q.w * 9 // 10, (draw.__name__, night, "the cables along the foot"))


class Links(unittest.TestCase):
    def test_a_link_button_is_a_metal_plate_under_ribbed_conduit_and_takes_its_own_sprite(self):
        """A link button carries a run of ribbed conduit along its two top rows, clamped in dark metal at its ends, over
        a plate of dark metal, its letters lit in phosphor at 4.5:1 and more; each of the four takes a sprite of its
        own."""
        for night in (False, True):
            p = SET.link_button("Docs", 0, night)
            top = {c for (x, y), c in p.layers["base"].items() if y < 2}
            self.assertTrue(top and top <= set(CONDUIT) | set(METAL), (night, top))
            fill, _, ink, _ = SET.link_colours(night)
            self.assertGreaterEqual(contrast(ink, fill), 4.5, night)
        sprites = [tuple(SET.link_icon(i, False, FLAME[4])[0]) for i in range(4)]
        self.assertEqual(len(set(sprites)), 4, "four sprites of their own")


class Badges(unittest.TestCase):
    def test_ribbed_conduit_lies_along_every_badges_top_two_rows_with_the_letters_under_it(self):
        conduit = set(CONDUIT) | {FLAME[2], FLAME[4]}
        for style in BADGE_STYLES:
            drawn = [SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                       SET.badge_states()["green"])]
            drawn += [SET.plate_badge(style, "License", "MIT", "scale", mode) for mode in ("day", "night")]
            for p in drawn:
                rows = {c for (x, y), c in p.layers["base"].items() if y in (0, 1)}
                self.assertTrue(rows and rows <= conduit, (style, rows - conduit))
                self.assertTrue(all(y >= TOP for _, _, _, y, _ in p.uses["base"]), "the letters sit under the band")

    def test_a_counters_numerals_hold_4_5_on_their_screens(self):
        for night in (False, True):
            q = Pix(20, 20)
            SET.counter_cell(q, 2, 2, night)
            face = q.layers["base"][(7, 9)]
            self.assertGreaterEqual(contrast(SET.counter_ink(night, False), face), 4.5, night)
            self.assertGreaterEqual(contrast(SET.counter_ink(night, True), face), 2.0, night)


class Games(unittest.TestCase):
    def test_the_boards_and_the_podium_are_the_machines_own_stuffs(self):
        """The squares are the pods' glass in its leads and the towers' riveted metal, the frame is the conduit's
        rubber, riveted, and the winners stand on a podium of the towers' dark metal, cobwebbed in its corners and
        trimmed in glass: all of the design's own tones, none the hand lends every design."""
        own = set(SET.tokens) - set(SET.hand.tokens)
        for night in (False, True):
            light, dark = SET.game_squares(night)
            frame, style = SET.game_frame(night)
            podium = SET.game_podium(night)
            self.assertIsInstance(podium, Podium)
            for stuff in (light, dark, frame, podium.stuff, podium.trim):
                self.assertIsInstance(stuff, Stuff)
                self.assertTrue(stuff.tokens <= own, (night, stuff.base))
            self.assertEqual((light.grain, dark.grain, style), ("glass", "metal", "iron"))
            self.assertEqual((podium.stuff.base, podium.stuff.grain, podium.style), (METAL[4], "metal", "cobwebs"))
            self.assertEqual(podium.trim.ramp, GLASS, "trimmed in glass")


if __name__ == "__main__":
    unittest.main()
