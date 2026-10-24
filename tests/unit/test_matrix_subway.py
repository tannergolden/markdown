# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Subway design's own rules, which the checks every design of a collection shares cannot know: what after hours
alone shows (the tube's flicker and its cone of light, the booth's lit glass, the globes' glow) stays out of the day,
and the July sun pouring down the stair out of the night; a title is laid in mosaic, tessera by tessera, with a
glint of the fluorescent light on it after hours only; the clock's second hand, the fan, the train's arrival, the
waiting man's coat, the woman on the stair and the dust in the light each move on their own cadence, and only in a
wide moving header; each header's hero stands where the words leave it, the train in its tunnel on an H1, the stair
rising to its way out on an H2 and the token booth rising the strip's full height on an H3, and on a phone the H1's
whole station and the H2's and H3's heroes stand under the words; the footers stand on the platform's edge with the
green globes after their last cell where there is room; the links are enamel signs hung on hooks; the frieze lies
along every badge's top two rows with the letters under it; a counter's numerals hold 4.5:1 on their plates; and
the games are built of the station's own glazed tile. The checks every design of a collection shares run here too."""
from __future__ import annotations

import unittest
from unittest import mock

from tests.unit import design_checks as D
from tests.unit.test_holiday_sets import contents

from domain.canvas import DARK, DAY
from domain.collections.matrix_subway import SET
from domain.collections.matrix_subway import art as A
from domain.collections.matrix_subway.palette import RAMP
from domain.holidays.designs.badges import STYLES as BADGE_STYLES, TOP
from domain.holidays.designs.materials import Podium, Stuff
from domain.holidays.pixel import Pix, contrast, num

KEY = SET.key
FLAME = RAMP["flame"]
HEADERS: dict = {}


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


def layers(p: Pix, kind: str) -> list:
    """The names of a drawing's layers that move as `kind` does: twinkle, flicker, blink or seq."""
    return [n for n in p.layers if p.meta[n][2] and p.meta[n][2][0] == kind and (p.layers[n] or p.shapes[n])]


class Shared(D.Shared, unittest.TestCase):
    """The checks every design of a collection shares, over Subway kept all year."""

    SET = SET
    ART = A
    PIECES = ("tunnel", "train", "headlights", "signal", "tube", "cone", "column", "fan", "poster", "clock", "bench",
              "waiting", "newspaper", "platform", "stairs", "globe", "way_out", "rider", "booth", "turnstile",
              "hanging_sign")
    FOOTINGS = ("_footed",)


class AfterHours(unittest.TestCase):
    def test_what_after_hours_alone_shows_stays_out_of_the_day(self):
        """The tube overhead flickers and throws its cone of light, the booth's glass glows from inside and the
        globes blaze only after hours: by day nothing flickers, no light of the phosphor is laid over the wall and
        the booth's glass is clear."""
        h, _ = contents(KEY)["repository"]
        for code, draw in (("H1", SET.h1), ("H2", SET.h2), ("H3", SET.h3)):
            day, night = draw(h, False, True), draw(h, True, True)
            self.assertFalse(layers(day, "flicker"), (code, "nothing flickers by day"))
            self.assertTrue(layers(night, "flicker"), (code, "after hours the lights flicker"))
        self.assertNotIn(f'fill="{FLAME[3]}"', header("H1", "repository", False), "no cone, no phosphor light by day")
        self.assertIn(f'fill="{FLAME[3]}"', header("H1", "repository", True), "the cone and the street's lamps")
        self.assertNotIn(FLAME[1], header("H3", "repository", False), "the booth's glass is clear by day")
        self.assertIn(FLAME[1], header("H3", "repository", True), "and lit from inside after hours")

    def test_the_july_sun_pours_down_the_stair_by_day_only(self):
        day, night = header("H2", "repository", False), header("H2", "repository", True)
        self.assertRegex(day, r'<g clip-path="url\(#dl\d+\)" fill="#FFFFFF">', "the sun down the flight")
        self.assertNotRegex(night, r'<g clip-path="url\(#dl\d+\)"', "no sun after hours")


class Titles(unittest.TestCase):
    def test_a_title_is_laid_in_mosaic_and_glints_after_hours_only(self):
        """A title's letters are stroked with the mosaic's pattern of tesserae, a tile of three by three a font unit
        each, in its grout ring and with its shadow cast; after hours a tessera here and there glints, twinkling, and
        by day none does."""
        day, night = header("H1", "repository", False), header("H1", "repository", True)
        self.assertIn('<pattern id="ms4d"', day)
        self.assertIn('<pattern id="ms4n"', night)
        self.assertIn(f'stroke="{RAMP["terra"][1]}"', day, "the grout ring by day")
        self.assertIn(f'stroke="{RAMP["terra"][0]}"', night, "and after hours")
        h, _ = contents(KEY)["repository"]
        for night in (False, True):
            p = SET.h1(h, night, True)
            x, y, _, scale, w = p.titles[0]
            glints = [xy for n in layers(p, "twinkle") for xy in p.layers[n]
                      if x <= xy[0] < x + w and y <= xy[1] < y + 7 * scale]
            self.assertEqual(bool(glints), night, night)


class Motion(unittest.TestCase):
    def test_each_thing_moves_on_its_own_cadence_and_only_in_a_wide_moving_header(self):
        """The clock's second hand steps round a fifth of a minute at a time over a minute, the fan's blades turn in
        three frames, the train comes up the tunnel on an eight-second loop, the waiting man's coat stirs on four, the
        woman comes down the stair on eight and the dust drifts through the light on a slow sweep of thirty; a still
        file and a phone's move nothing."""
        h1, h2 = header("H1", "repository", True), header("H2", "repository", False)
        self.assertIn(f'dur="{num(A.TICK)}s"', h1, "the second hand")
        self.assertIn(f'dur="{num(A.FAN)}s"', h1, "the fan")
        self.assertIn(f'dur="{num(A.ARRIVE)}s"', h1, "the train's arrival")
        self.assertIn(f'dur="{num(A.LOOP)}s"', h1, "the man's coat")
        self.assertIn(f'dur="{num(A.MOTES)}s"', h1, "the dust")
        self.assertTrue(4 <= A.LOOP <= 8 and 4 <= A.ARRIVE <= 8 and 24 <= A.MOTES <= 48)
        self.assertRegex(h2, r'type="translate" values="[^"]*" dur="8s"', "the woman on the stair")
        for code in ("H1", "H2", "H3"):
            for night in (False, True):
                self.assertNotIn("<animate", header(code, "repository", night, motion=False), (code, night))
                self.assertNotIn("<animate", header(code, "repository", night, wide=False, motion=False), code)


class Heroes(unittest.TestCase):
    def test_an_h1_stands_the_train_in_its_tunnel_and_the_man_waiting_at_the_platforms_far_end(self):
        h, _ = contents(KEY)["repository"]
        tunnels = calls("tunnel", lambda: SET.h1(h, False, True))
        self.assertEqual(len(tunnels), 1)
        (x0, x1, top, base, night), _ = tunnels[0]
        self.assertLessEqual(x0, 8)
        self.assertLessEqual(top, 22, "the arch rises nearly the sheet's height")
        self.assertEqual(len(calls("waiting", lambda: SET.h1(h, False, True))), 1)

    def test_an_h2_stands_the_stair_rising_to_its_way_out_with_the_woman_coming_down_it(self):
        """On every content's H2 the stair stands at the right, its foot on the platform two units and more clear of
        the words, rising eight steps and more to its way out under the frieze, a globe on each newel post, the woman
        in the red dress on it."""
        for name, (h, _) in contents(KEY).items():
            with mock.patch.object(A, "stairs", wraps=A.stairs) as stairs, \
                    mock.patch.object(A, "way_out", wraps=A.way_out) as out, \
                    mock.patch.object(A, "globe", wraps=A.globe) as globe, \
                    mock.patch.object(A, "rider", wraps=A.rider) as rider:
                p = SET.h2(h, False, True)
            (call,) = stairs.call_args_list
            fx, g, n = call.args[1], call.args[2], call.args[3]
            self.assertGreaterEqual(n, 8, name)
            self.assertGreaterEqual(fx, 300, name)
            head = A.stair_top(fx, g, n - 1)
            (arch,) = out.call_args_list
            self.assertGreaterEqual(arch.args[3], 17, (name, "the way out's crown under the frieze"))
            self.assertEqual(arch.args[4], head - 1, (name, "the way out opens on the landing"))
            self.assertEqual(globe.call_count, 2, name)
            self.assertEqual(rider.call_count, 1, name)
            self.assertTrue(p.clear_of_words(fx - 9, arch.args[3] - 6, p.w, g + 2), name)

    def test_an_h3_stands_the_token_booth_rising_the_strips_full_height(self):
        """On every content's H3 the token booth stands at the strip's right, its foot on the platform and its sign's
        top within the top band's reach, so it rises the strip's full height, forty-four rows and more; a sign hangs
        over it where the strip is taller than the booth, and the turnstiles stand before it in a bank of as many as
        three where the words leave them room, all three on a strip that says the least."""
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                booths = calls("booth", lambda: SET.h3(h, night, True))
                self.assertEqual(len(booths), 1, (name, night))
                (x, top, g, *_), _ = booths[0]
                self.assertGreaterEqual(x, 352, name)
                self.assertGreaterEqual(g - top + 1, A.BOOTH_LOW, name)
                signs = calls("hanging_sign", lambda: SET.h3(h, night, True))
                self.assertEqual(bool(signs), top >= A.SIGN_ROOM, (name, top))
                self.assertTrue(top <= 18 or signs, (name, "the booth or its sign reaches the top band"))
                bank = [args[0] for args, _ in calls("turnstile", lambda: SET.h3(h, night, True))]
                self.assertLessEqual(len(bank), 3, name)
                self.assertEqual(bank, [x - 13 * (i + 1) for i in range(len(bank))], (name, "a bank before the booth"))
                if name == "least":
                    self.assertEqual(len(bank), 3, (name, "room for the whole bank"))

    def test_a_phone_stands_the_whole_station_under_an_h1s_words_and_each_hero_under_an_h2s_and_an_h3s(self):
        """A phone's H1 stands the whole station across its width under its words, forty-eight rows and more, the
        tunnel with the train in it, the bench and the man waiting; a phone's H2 the stair with the woman at its head,
        and its H3 the token booth with its turnstile; by day and by night, for every shared content."""
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                what = (name, night)
                _, pixels, _ = D.sprites(SET, lambda: SET.h1_narrow(h, night), "scene_narrow")
                xs, ys = [x for x, _ in pixels], [y for _, y in pixels]
                self.assertLessEqual(min(xs), 6, what)
                self.assertGreaterEqual(max(xs), 172, what)
                self.assertGreaterEqual(max(ys) - min(ys) + 1, 48, what)
                for fn in ("tunnel", "train", "bench", "waiting"):
                    self.assertEqual(len(calls(fn, lambda: SET.h1_narrow(h, night))), 1, (what, fn))
                for fn in ("stairs", "rider"):
                    self.assertEqual(len(calls(fn, lambda: SET.h2_narrow(h, night))), 1, (what, fn))
                for fn in ("booth", "turnstile"):
                    self.assertEqual(len(calls(fn, lambda: SET.h3_narrow(h, night))), 1, (what, fn))


class Footers(unittest.TestCase):
    def test_every_footer_stands_on_the_platforms_edge_with_the_globes_after_its_last_cell(self):
        """Along every footer's foot lies the band of tile under the platform's edge, the yellow line over it where
        the words leave it room; and a title block whose cells leave it room has the pair of green globes on their
        posts after its last cell, a scale bar's sheet one globe beside its scale where a pair has no room."""
        for name, (_, f) in contents(KEY).items():
            for draw in (SET.f1, SET.f2, SET.f1_narrow, SET.f2_narrow):
                for night in (False, True):
                    p = draw(f, night)
                    svg = p.svg("f", "f", still=True)
                    self.assertIn(RAMP["terra"][0], svg, (name, draw.__name__, night, "the band's foot"))
        _, f = contents(KEY)["repository"]
        with mock.patch.object(A, "globes", wraps=A.globes) as pair:
            p = SET.f1(f, False)
        (call,) = pair.call_args_list
        self.assertGreater(call.args[1], max(b[2] for b in p.words), "after the way back up")
        with mock.patch.object(A, "globe_post", wraps=A.globe_post) as one:
            SET.f2(f, False)
        self.assertEqual(one.call_count, 1, "a globe beside the scale")
        night = SET.f1(f, True)
        self.assertIn(f'fill="{FLAME[4]}"', "".join(night.shapes["haze"]), "the globes glow after hours")


class Links(unittest.TestCase):
    def test_a_link_is_an_enamel_sign_hung_on_two_hooks(self):
        for night in (False, True):
            p = SET.link_button("Issues", 0, night)
            fill, edge, ink, shade = SET.link_colours(night)
            self.assertGreaterEqual(contrast(ink, fill), 4.5, night)
            hooks = [x for x in range(p.w) if p.get(x, 0) in RAMP["steel"]]
            self.assertEqual(len(hooks), 4, (night, "two hooks of two units each"))
            self.assertEqual({p.get(x, 3) for x in range(3, p.w - 3)} - {None},
                             {RAMP["enamel"][4] if night else RAMP["enamel"][6]}, "the enamel hairline")
        icons = {tuple(SET.link_icon(i, False, "#000000")[0]) for i in range(4)}
        self.assertEqual(len(icons), 4, "each link its own icon")


class Badges(unittest.TestCase):
    def test_the_frieze_lies_along_every_badges_top_two_rows_with_the_letters_under_it(self):
        frieze = {RAMP["bottle"][2], RAMP["ochre"][4], RAMP["cobalt"][4], RAMP["terra"][4]}
        for style in BADGE_STYLES:
            drawn = [SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                       SET.badge_states()["green"])]
            drawn += [SET.plate_badge(style, "License", "MIT", "scale", mode) for mode in ("day", "night")]
            for p in drawn:
                rows = {c for (x, y), c in p.layers["base"].items() if y in (0, 1)}
                self.assertTrue(rows and rows <= frieze, (style, rows - frieze))
                self.assertTrue(all(y >= TOP for _, _, _, y, _ in p.uses["base"]), "the letters sit under the band")

    def test_a_counters_numerals_hold_4_5_on_their_plates(self):
        for night in (False, True):
            q = Pix(20, 20)
            SET.counter_cell(q, 2, 2, night)
            face = q.layers["base"][(7, 8)]
            self.assertGreaterEqual(contrast(SET.counter_ink(night, False), face), 4.5, night)
            self.assertGreaterEqual(contrast(SET.counter_ink(night, True), face), 2.0, night)


class Games(unittest.TestCase):
    def test_the_boards_and_the_podium_are_of_the_stations_glazed_tile(self):
        """The board's light squares are the wall's celadon and its dark the border's bottle green, each laid as
        tesserae, a tone down after hours; its frame is terracotta tesserae; and the Hall's winners stand on plain
        blocks of the wall's glazed tile."""
        for night in (False, True):
            light, dark = SET.game_squares(night)
            self.assertEqual((light.ramp, light.grain), (RAMP["glaze"], "tile"), night)
            self.assertEqual((dark.ramp, dark.grain), (RAMP["bottle"], "tile"), night)
            self.assertEqual(SET.game_frame(night), (Stuff(RAMP["terra"], 3), "tesserae"))
            self.assertEqual(SET.game_podium(night), Podium(Stuff(RAMP["glaze"], 4, "tile")))
        self.assertGreater(SET.game_squares(False)[0].at, SET.game_squares(True)[0].at, "dimmer after hours")


if __name__ == "__main__":
    unittest.main()
