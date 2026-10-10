# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Stronghold set's own rules, which the checks every set shares cannot know: what the night alone shows
(torches, candlelit windows, the moon, the dragon and the gold inlay) stays out of the day's files, and what the
day alone shows (clouds and the hawk) out of the night's; a title is carved into the stone by day and inlaid
with gold by night; the pennants wave at three moments only in a wide moving header; the sky's life keeps clear
of a wide title; every phone header stands a scene of the set's, and a phone's H2 and H3 stand their heroes under
their words whatever they say; the most a page can say keeps its whole scene and its motion within the budget,
an ordinary page keeps its full weight with room to spare, and a drawing made lighter thins only texture; an
iron band lies along every badge's top two rows; and a counter's numerals hold 4.5:1 on their tablets. The set is
a theme, not a holiday on the calendar, so the checks every registered set shares run here over the set directly,
with the same contents and the same entry points."""
from __future__ import annotations

import datetime as dt
import re
import unittest
import xml.dom.minidom as minidom
from collections import Counter
from unittest import mock

from tests import support
from tests.unit.test_holiday_sets import DASHES, ELEMENTS, HEIGHTS, STAMP, contents

from domain import KIT, KIT_VERSION
from domain.badges import data as BD
from domain.banners.content import Header
from domain.banners.designs import DESIGNS, variants
from domain.canvas import BUDGET, DARK, DAY, colours, lint
from domain.elements import draw as E
from domain.holidays.designs.badges import PLATE, STATES, STYLES as BADGE_STYLES, TOP
from domain.collections.hand import MEDIEVAL, CollectionSet, check, lab
from domain.collections.medieval_stronghold import SET
from domain.collections.medieval_stronghold import art as A
from domain.collections.medieval_stronghold.palette import C, NIGHT_SKY, RAMP, X
from domain.holidays.pixel import Pix, contrast
from domain.palette import PALETTE

support.install()
KEY = SET.key
HEADER = Header(tone="standard", holiday=KEY)
# A title that fills a header's width on two lines, leaving the sky over the scene no room.
LONG = HEADER.with_(title="w" * 40)
IRON = set(RAMP["iron"])
EARTHSHINE = RAMP["moon"][0]                        # the moon's dark limb, the darkest tone of the hand's moon
DRAGON = re.compile(r'<clipPath id="gl\d+">')       # the window of sky the dragon crosses
JULY = dt.date(2026, 7, 1)                          # a day that makes the design its month's


def draw_banners() -> list:
    """Every banner file the set draws for the shared contents: (content, code, file name, svg), as the kit
    would ask for them, variant by variant."""
    out = []
    for name, (h, f) in contents(KEY).items():
        for code, design in DESIGNS.items():
            content = h if design.kind == "header" else f
            drawer = SET.header if design.kind == "header" else SET.footer
            for suffix, wide, motion, theme in variants(design):
                out.append((name, code, f"{design.kind}-{suffix}.svg", drawer(code, content, theme, wide, motion)))
            if design.kind == "footer" and design.chip and content.on("links"):
                for i, (label, _) in enumerate(content.links):
                    for theme in (DAY, DARK):
                        out.append((name, code, f"link-{i}-{theme['name']}.svg", SET.link(label, theme, i)))
    return out


DRAWN: list = []


def every_banner() -> list:
    if not DRAWN:
        DRAWN.extend(draw_banners())
    return DRAWN


def sprites(draw, *hooks) -> tuple:
    """`draw()`'s drawing, and every pixel of the sprites the set's `hooks` (names of its drawing hooks) put
    on it, gathered as they draw: their pixels on every layer and the cells of the symbols they place."""
    pixels, cells = set(), {}
    symbol = Pix.symbol

    def kept(self, key, cells_=None, shapes="", mono=False):
        sid = symbol(self, key, cells_, shapes, mono)
        cells.setdefault(sid, set(cells_ or ()))
        return sid

    def watched(hook):
        def drawn(*args, **kw):
            p = next(a for a in args if isinstance(a, Pix))
            before = {L: set(c) for L, c in p.layers.items()}
            placed = {L: len(u) for L, u in p.uses.items()}
            out = hook(*args, **kw)
            for L, c in p.layers.items():
                pixels.update(set(c) - before.get(L, set()))
            for L, uses in p.uses.items():
                for (_, sid, x, y, s) in uses[placed.get(L, 0):]:
                    pixels.update((x + dx * s, y + dy * s) for dx, dy in cells.get(sid, ()))
            return out
        return drawn

    with mock.patch.object(Pix, "symbol", kept), \
            mock.patch.multiple(SET, **{name: watched(getattr(SET, name)) for name in hooks}):
        p = draw()
    return p, pixels


def off_words(p: Pix, pixels, margin=2) -> list:
    """The pixels among `pixels` that lie within `margin` units of a word's box."""
    return sorted(xy for xy in pixels if not p.clear_of_words(xy[0] - margin, xy[1] - margin, xy[0] + margin + 1,
                                                             xy[1] + margin + 1))


def painted(draw, *hooks) -> Counter:
    """How many pixels of each colour the set's `hooks` paint while `draw()` draws, on every layer."""
    cells = {}

    def watched(hook):
        def drawn(*args, **kw):
            p = next(a for a in args if isinstance(a, Pix))
            before = {L: dict(c) for L, c in p.layers.items()}
            out = hook(*args, **kw)
            for L, c in p.layers.items():
                cells.update({(L, xy): col for xy, col in c.items() if before.get(L, {}).get(xy) != col})
            return out
        return drawn
    with mock.patch.multiple(SET, **{name: watched(getattr(SET, name)) for name in hooks}):
        draw()
    return Counter(cells.values())


# The pieces of a scene, as the set's art draws them: the buildings and their masonry, the figures and beasts, the
# pennants and banners, the sky's life, the torches and their light, and the title's carving and glints.
PIECES = ("castle", "guard", "gatehouse", "watchtower", "tower", "wall", "arch", "drawbridge", "moat", "knight",
          "sentry", "pennants", "flag", "clouds", "hawk", "dragon", "moon", "stars", "torch", "lit_window",
          "glimmer", "lamplight", "carve", "glints")


def pieces(draw) -> tuple:
    """`draw()`'s file, and the pieces of the scene in the drawing it was made from (the last drawn, when the kit
    draws a file again lighter): each call of the set's art named in `PIECES`, with its arguments but the
    canvas, in the order drawn."""
    calls = []

    def watched(name, art):
        def drawn(p, *args, **kw):
            calls.append((p, name, args, sorted(kw.items())))
            return art(p, *args, **kw)
        return drawn
    with mock.patch.multiple(A, **{name: watched(name, getattr(A, name)) for name in PIECES}):
        svg = draw()
    last = calls[-1][0] if calls else None
    return svg, [call[1:] for call in calls if call[0] is last]


def draw_elements() -> dict:
    """Every element file for the shared specimen, by the kit's name, drawn as the kit asks for them."""
    out = {}
    for eid, d in ELEMENTS.items():
        kind = d["kind"]
        spec = E.describe(kind, d)
        kinds = ("wide", "narrow", "half") if kind in ("roster", "certificate") else E.variants(kind, d)
        for variant in kinds:
            for theme in (DAY, DARK):
                out[(eid, kind, variant, theme["name"])] = SET.element(kind, spec, theme, variant)
    return out


class Night(unittest.TestCase):
    def test_what_the_night_alone_shows_stays_out_of_the_day_and_the_days_clouds_out_of_the_night(self):
        for code in ("H1", "H2", "H3"):
            day = SET.header(code, HEADER, DAY, True, True)
            night = SET.header(code, HEADER, DARK, True, True)
            self.assertNotIn(RAMP["flame"][6], day, (code, "a torch's flame"))
            self.assertNotIn(EARTHSHINE, day, (code, "the moon"))
            self.assertNotRegex(day, DRAGON, (code, "the dragon"))
            self.assertNotIn("painlay", day, (code, "the gold inlay"))
            self.assertIn(RAMP["flame"][6], night, code)
            self.assertIn("painlay", night, code)
            self.assertNotIn(RAMP["cloud"][5], night, (code, "a cloud"))
            self.assertNotIn('dur="1.4s"', night, (code, "the hawk's wingbeat"))
        day, night = (SET.header("H1", HEADER, theme, True, True) for theme in (DAY, DARK))
        self.assertIn('clip-path="url(#clc)"', day, "clouds drift")
        self.assertIn('dur="1.4s"', day, "the hawk soars")
        self.assertIn(EARTHSHINE, night)
        self.assertRegex(night, DRAGON, "the dragon crosses")

    def test_the_sky_life_keeps_clear_of_a_wide_title(self):
        self.assertNotRegex(SET.header("H1", LONG, DARK, True, True), DRAGON, "no dragon over a wide title")
        self.assertNotIn('dur="1.4s"', SET.header("H1", LONG, DAY, True, True), "no hawk over a wide title")
        self.assertIn(EARTHSHINE, SET.header("H1", HEADER, DARK, True, True), "the moon, where it has room")
        self.assertIn(EARTHSHINE, SET.header("H2", HEADER, DARK, True, True))


class Phones(unittest.TestCase):
    def test_every_sprite_keeps_two_units_clear_of_every_word_on_a_phone(self):
        """On a phone the castle, the gatehouse, the tower, the scene under the words, the pennants and the
        section mark are built to the rows the words leave free: no pixel of theirs lies within two units of a
        word's box, for any of the shared contents, by day or by night."""
        drawers = {"H1": SET.h1_narrow, "H2": SET.h2_narrow, "H3": SET.h3_narrow}
        for name, (h, _) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    p, pixels = sprites(lambda: drawer(h, night), "scene_narrow", "scene_under", "garland",
                                        "section_mark")
                    hits = off_words(p, pixels)
                    self.assertEqual(hits[:6], [], (name, code, night, len(hits)))

    def test_every_phone_header_stands_a_scene_of_the_sets_by_day_and_by_night(self):
        """Every phone header of every shared content, H1, H2 and H3, by day and by night, stands a scene of the
        set's own: towers of its stone over the moat, the H1's stronghold in the rows it keeps under its words and
        the H2's and H3's heroes in the rows they ask for under theirs, never both, and by night a torch burning by
        it."""
        drawers = {"H1": SET.h1_narrow, "H2": SET.h2_narrow, "H3": SET.h3_narrow}
        stone, water, flame = (set(RAMP["stone"]) | set(RAMP["slate"])), set(RAMP["water"]), set(RAMP["flame"])
        for name, (h, _) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    what = (name, code, night)
                    beside = painted(lambda: drawer(h, night), "scene_narrow")
                    under = painted(lambda: drawer(h, night), "scene_under")
                    self.assertNotEqual(bool(beside), bool(under), what)
                    scene = beside or under
                    self.assertGreaterEqual(sum(n for c, n in scene.items() if c in stone), 150, what)
                    self.assertGreaterEqual(sum(n for c, n in scene.items() if c in water), 50, what)
                    self.assertEqual(any(c in flame for c in scene), night, what)

    def test_a_phones_h2_and_h3_stand_their_heroes_under_their_words_whatever_they_say(self):
        """Whatever the words, a phone's H2 and H3 ask for the same rows under them and stand their heroes there,
        never beside them: nothing of a scene stands beside a title or SECTION A-A, for any shared content."""
        for name, (h, _) in contents(KEY).items():
            for code in ("H2", "H3"):
                self.assertEqual(SET.phone_rows(code, 0), SET.phone_rows(code, 400), (name, code))
                self.assertFalse(painted(lambda: SET.header(code, h, DAY, False, False), "scene_narrow"), (name, code))
                self.assertTrue(painted(lambda: SET.header(code, h, DAY, False, False), "scene_under"), (name, code))

    def test_a_phones_h2_stands_the_gatehouse_at_its_full_height_with_the_knight_riding_to_it(self):
        """Under a phone's H2's words stands the gatehouse of a wide H2 at its full height, sixty rows and more over
        the water, its keep's tower, its sentry and its banners, the knight riding along the near bank toward its
        gate; across the phone, two units clear of every word, for every shared content, by day and by night."""
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                what = (name, night)
                with mock.patch.object(A, "gatehouse", wraps=A.gatehouse) as gate, \
                        mock.patch.object(A, "knight", wraps=A.knight) as knight, \
                        mock.patch.object(A, "sentry", wraps=A.sentry) as sentry:
                    p, pixels = sprites(lambda: SET.h2_narrow(h, night), "scene_under")
                (call,) = gate.call_args_list
                self.assertEqual(call.kwargs["room"], A.GATE_FULL, what)
                self.assertTrue(sentry.called, what)
                self.assertEqual([c.kwargs.get("flip") for c in knight.call_args_list], [True], (what, "to the gate"))
                xs, ys = [x for x, _ in pixels], [y for _, y in pixels]
                self.assertLessEqual(min(xs), 6, what)
                self.assertGreaterEqual(max(xs), 173, what)
                self.assertGreaterEqual(max(ys) - min(ys) + 1, 60, what)
                self.assertEqual(off_words(p, pixels), [], what)

    def test_a_phones_h3_stands_the_great_keep_with_the_watchtower_and_the_knight(self):
        """Under a phone's H3's words stands the great keep of a wide H3, sixty rows and more over the water, with
        its curtain wall, its gate and its drum tower; the watchtower with its sentry at the left; and the knight
        riding between them toward the keep's gate; across the phone, two units clear of every word, for every
        shared content, by day and by night."""
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                what = (name, night)
                with mock.patch.object(A, "great_keep", wraps=A.great_keep) as keep, \
                        mock.patch.object(A, "watchtower", wraps=A.watchtower) as tower, \
                        mock.patch.object(A, "knight", wraps=A.knight) as knight:
                    p, pixels = sprites(lambda: SET.h3_narrow(h, night), "scene_under")
                (call,) = keep.call_args_list
                self.assertGreaterEqual(call.kwargs["room"], 60, what)
                self.assertGreaterEqual(call.kwargs["left"], 40, (what, "the wall, its gate and the drum tower"))
                self.assertTrue(tower.call_args.kwargs["guard"], (what, "the watchtower's sentry"))
                self.assertEqual([c.kwargs.get("flip") for c in knight.call_args_list], [True], (what, "to the gate"))
                xs, ys = [x for x, _ in pixels], [y for _, y in pixels]
                self.assertLessEqual(min(xs), 6, what)
                self.assertGreaterEqual(max(xs), 173, what)
                self.assertGreaterEqual(max(ys) - min(ys) + 1, 60, what)
                self.assertEqual(off_words(p, pixels), [], what)

    def test_every_sprite_keeps_two_units_clear_of_every_word_on_a_wide_header_too(self):
        """The scenes, the pennants, the marks beside a title and the ivy on the rules keep the same two units
        from every word across a wide header."""
        drawers = {"H1": SET.h1, "H2": SET.h2, "H3": SET.h3}
        for name, (h, _) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    p, pixels = sprites(lambda: drawer(h, night, True), "scene", "garland", "section_mark",
                                        "strip_mark", "rule_decor")
                    hits = off_words(p, pixels)
                    self.assertEqual(hits[:6], [], (name, code, night, len(hits)))

    def test_the_castle_the_gatehouse_and_the_tower_stand_where_the_words_leave_them_room(self):
        """The kit's own lines leave each phone its scene, built with banners flying; the least a page can say
        leaves the castle its full height; and the castle, which cannot fit beside the most a page can say,
        is left out rather than built over a word."""
        h, _ = contents(KEY)["kit"]
        for code in ("H1", "H2", "H3"):
            self.assertIn(RAMP["water"][4], SET.header(code, h, DAY, False, False), (code, "a moat"))
        least, _ = contents(KEY)["least"]
        p, pixels = sprites(lambda: SET.h1_narrow(least, False), "scene_narrow")
        self.assertIn(RAMP["gold"][4], {p.get(*xy) for xy in pixels}, "a gold banner flies from the keep")
        most, _ = contents(KEY)["most"]
        p, pixels = sprites(lambda: SET.h1_narrow(most, False), "scene_narrow")
        self.assertEqual(off_words(p, pixels), [])


class Weight(unittest.TestCase):
    def test_the_most_a_page_can_say_keeps_its_whole_scene_and_its_motion_within_the_budget(self):
        """The most content's wide H1 and H2, by day and by night, moving and still, drawn as the kit draws them,
        come out within the budget; a moving one moves just as it would at full weight; and each holds every
        piece of the scene its full weight holds, drawn the same: the castle and its towers, the gatehouse, the
        knight and the sentries, the pennants and the banners, the clouds and the hawk by day, the moon, the
        dragon and the torches with their light by night, and the carved title."""
        most, _ = contents(KEY)["most"]
        every = {"tower", "wall", "moat", "sentry", "pennants", "flag", "carve"}
        named = {("H1", DAY["name"]): {"castle", "guard", "knight", "clouds"},
                 ("H1", DARK["name"]): {"castle", "guard", "knight", "torch", "lit_window", "lamplight", "moon",
                                        "glints"},
                 ("H2", DAY["name"]): {"gatehouse", "hawk", "clouds"},
                 ("H2", DARK["name"]): {"gatehouse", "dragon", "torch", "lit_window", "lamplight", "moon", "glints"}}
        for code in ("H1", "H2"):
            for theme in (DAY, DARK):
                for motion in (True, False):
                    what = (code, theme["name"], motion)
                    svg, drawn = pieces(lambda: SET.header(code, most, theme, True, motion))
                    with mock.patch.dict(BUDGET, {"header": 10**9}):
                        full, whole = pieces(lambda: SET.header(code, most, theme, True, motion))
                    self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"], what)
                    self.assertEqual(drawn, whole, what)
                    self.assertEqual(svg.count("<animate"), full.count("<animate"), what)
                    self.assertEqual("<animate" in svg, motion, what)
                    must = every | named[(code, theme["name"])]
                    self.assertLessEqual(must, {name for name, _, _ in drawn}, what)

    def test_an_ordinary_page_is_drawn_at_full_weight_with_room_to_spare(self):
        """Every header of the kit's own lines and of the samples, wide or on a phone, moving or still, by day
        and by night, is drawn at its full weight, with its motion, at least 1,500 bytes under the budget."""
        for name in ("kit", "repository", "profile", "least"):
            h, _ = contents(KEY)[name]
            for code in ("H1", "H2", "H3"):
                for theme in (DAY, DARK):
                    for wide, motion in ((True, True), (True, False), (False, False)):
                        what = (name, code, theme["name"], wide, motion)
                        svg = SET.header(code, h, theme, wide, motion)
                        with mock.patch.dict(BUDGET, {"header": 10**9}):
                            self.assertEqual(svg, SET.header(code, h, theme, wide, motion), what)
                        self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"] - 1500, what)

    def test_a_drawing_made_lighter_thins_only_its_texture(self):
        """Made lighter to fit a budget a byte short of its full weight, a header keeps every piece of its scene,
        drawn the same, its title's carving, inlay and glow, and all its motion; only texture no one misses at
        1x is thinned (the stone's stipple, the outer ring of each torch's light and the faintest stars)."""
        h, _ = contents(KEY)["repository"]
        glow = f'<g stroke="{RAMP["gold"][4]}" stroke-opacity=".14">'
        for code in ("H1", "H2", "H3"):
            full, whole = pieces(lambda: SET.header(code, h, DARK, True, True))
            with mock.patch.dict(BUDGET, {"header": len(full.encode("utf-8")) - 1}):
                lighter, drawn = pieces(lambda: SET.header(code, h, DARK, True, True))
            self.assertLess(len(lighter), len(full), code)
            self.assertEqual(drawn, whole, code)
            self.assertEqual(lighter.count("<animate"), full.count("<animate"), code)
            self.assertIn(glow, lighter, code)
            self.assertIn('id="painlay', lighter, code)
        self.assertFalse(SET._lite, "the set is left drawing lighter")


class Titles(unittest.TestCase):
    def test_a_title_is_carved_by_day_and_inlaid_with_gold_by_night(self):
        day = SET.header("H1", HEADER, DAY, True, True)
        self.assertIn(f'<g stroke="{C["white"]}">', day, "the lit wall of the cut")
        self.assertIn(f'<g stroke="{RAMP["stone"][0]}">', day, "the shaded wall of the cut")
        self.assertIn(f'<g stroke="{RAMP["gold"][3]}">', day, "a hairline of gold inlay along the lit edge")
        self.assertIn(f'<g stroke="{X["recess"]}">', day, "the floor of the cut, lighter than its shaded wall")
        self.assertNotIn("stroke-opacity", day.split("<defs>")[0], "no glow by day")
        night = SET.header("H1", HEADER, DARK, True, True)
        self.assertIn('id="painlay4n"', night, "gold inlay, a band a row of the face")
        self.assertIn(f'<g stroke="{RAMP["slate"][5]}">', night, "the moonlit wall of the cut")
        self.assertIn(f'<g stroke="{RAMP["gold"][4]}" stroke-opacity=".14">', night, "the inlay's glow")

    def test_the_pennants_wave_at_three_moments_only_in_a_wide_moving_header(self):
        moving = SET.header("H1", HEADER, DAY, True, True)
        self.assertEqual(moving.count('dur="1.35s"'), 3, "three moments of the wave")
        for still in (SET.header("H1", HEADER, DAY, True, False), SET.header("H1", HEADER, DAY, False, False)):
            self.assertNotIn("<animate", still)
            self.assertIn(RAMP["gules"][5], still, "the pennants still hang, at the first moment")


class Badges(unittest.TestCase):
    def test_an_iron_band_lies_along_every_badges_top_two_rows_with_the_letters_under_it(self):
        for style in BADGE_STYLES:
            drawn = [SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                       SET.badge_states()["green"])]
            drawn += [SET.plate_badge(style, "License", "MIT", "scale", mode) for mode in ("day", "night")]
            for p in drawn:
                rows = {c for (x, y), c in p.layers["base"].items() if y in (0, 1)}
                self.assertTrue(rows and rows <= IRON, (style, rows - IRON))
                self.assertTrue(all(y >= TOP for _, _, _, y, _ in p.uses["base"]), "the letters sit under the band")

    def test_a_counters_numerals_hold_4_5_on_their_tablets(self):
        for night in (False, True):
            q = Pix(20, 20)
            SET.counter_cell(q, 2, 2, night)
            face = q.layers["base"][(7, 8)]
            self.assertGreaterEqual(contrast(SET.counter_ink(night, False), face), 4.5, night)
            self.assertGreaterEqual(contrast(SET.counter_ink(night, True), face), 2.0, night)


def flickering(p: Pix) -> set:
    """Every colour on a drawing's flickering layers: the flames, their glows and the light they lay."""
    layers = [L for L in p.layers if p.meta[L][2] and p.meta[L][2][0] == "flicker"]
    found = {c.split(":")[0] for L in layers for c in p.layers[L].values()}
    return found | {c for L in layers for c in re.findall(r'fill="(#[0-9A-F]{6})"', "".join(p.shapes[L]))}


class Hand(unittest.TestCase):
    """The design is drawn in the medieval collection's hand (`collections.hand`): its words in the hand's inks, its
    stone within the hand's grounds, its fires on the hand's flame and its moon the hand's, its title's glint, its
    figures and its clouds on the hand's times, the month's mark at its headers' top centre, clear of every scene,
    and the composition the hand asks of every design: a great keep the strip's full height on an H3, the whole
    stronghold across a phone's H1, the gatehouse and the great keep under a phone's H2's and H3's words (see
    `Phones`), and a footing and a banner on every footer."""

    def test_it_keeps_to_its_hand_as_its_months_design_and_kept_all_year(self):
        self.assertIsInstance(SET, CollectionSet)
        self.assertEqual((SET.collection, SET.month), ("medieval", 7))
        self.assertEqual(check(SET.on(JULY)), [])
        self.assertEqual(check(SET), [])

    def test_its_words_are_in_the_hands_inks(self):
        for night in (False, True):
            k = SET.ink(night)
            self.assertEqual((k["body"], k["muted"]), (MEDIEVAL.body[night], MEDIEVAL.muted[night]), night)

    def test_its_stone_falls_within_the_hands_grounds(self):
        """By day the limestone behind the words, and by night every band of the moonlit stone, fall within the
        hand's bands of lightness and colour."""
        for night, grounds in ((False, (C["paper"],)), (True, NIGHT_SKY)):
            lo, hi, most = MEDIEVAL.night_ground if night else MEDIEVAL.day_ground
            for c in grounds:
                light, chroma, hue = lab(c)
                self.assertTrue(lo <= light <= hi, (night, c, light))
                self.assertLessEqual(chroma, most, (night, c))
                self.assertTrue(night or chroma >= 6 or 40 <= hue <= 110, (c, "a nearly colourless day leans warm"))

    def test_every_flame_burns_on_the_hands_flame_and_the_moon_is_the_hands(self):
        """The torches, the candlelit windows, the light they lay on the stone and the water, the footer's torches
        and the dragon's breath burn on the hand's flame, and the moon is drawn on the hand's moon."""
        self.assertEqual(RAMP["flame"], MEDIEVAL.ramp("flame"))
        self.assertEqual(RAMP["moon"], MEDIEVAL.ramp("moon"))
        flame, moon = set(MEDIEVAL.ramp("flame")), set(MEDIEVAL.ramp("moon"))
        for name in ("kit", "least"):
            h, f = contents(KEY)[name]
            for what, p in (("H1", SET.h1(h, True, True)), ("H2", SET.h2(h, True, True)),
                            ("H3", SET.h3(h, True, True)), ("H1 phone", SET.h1_narrow(h, True))):
                lit = flickering(p)
                self.assertTrue(lit, (name, what))
                self.assertLessEqual(lit, flame, (name, what))
            for what, p in (("F1", SET.f1(f, True)), ("F2", SET.f2(f, True))):
                self.assertLessEqual(flickering(p), flame, (name, what))
        q = Pix(60, 30)
        A._dragon_symbol(q, 0, False)
        breath = {c for c in re.findall(r'stroke="(#[0-9A-F]{6})"', "".join(q.defs))} - set(RAMP["dragon"])
        self.assertTrue(breath and breath <= flame, breath)
        q = Pix(40, 40)
        A.moon(q, 20, 20, 7)
        self.assertLessEqual(set(q.layers["base"].values()), moon)
        self.assertTrue(all(c in moon for c in re.findall(r'fill="(#[0-9A-F]{6})"', "".join(q.shapes["haze"]))))

    def test_its_title_glint_its_figures_and_its_clouds_move_on_the_hands_times(self):
        """A glint passes along the title's gold every `glint` seconds of the hand, by day and by night, and the still
        file keeps only the night's sparkles; the hawk circles and the dragon crosses in a figure's loop of four to
        eight seconds; and the clouds drift across the sky in a slow sweep of no more than forty-eight."""
        for theme in (DAY, DARK):
            svg = SET.header("H1", HEADER, theme, True, True)
            glint = re.search(r'<clipPath id="tg\d+"><rect[^>]*><animateTransform[^>]*dur="([\d.]+)s"', svg)
            self.assertEqual(float(glint.group(1)), MEDIEVAL.glint, theme["name"])
            p = SET.h1(HEADER, theme["dark"], True)
            sparkles = [still for _, _, moving, still in p.raws if 'id="tg' in moving]
            self.assertTrue(sparkles, theme["name"])
            self.assertEqual(all(sparkles), bool(theme["dark"]), "the still night keeps its sparkles")
        day = SET.header("H1", HEADER, DAY, True, True)
        self.assertTrue(24 <= A.DRIFT <= 48)
        self.assertIn(f'dur="{A.DRIFT:g}s"', day, "the clouds' drift")
        self.assertRegex(day, r'type="translate" values="[^"]*" dur="8s" repeatCount="indefinite" '
                              r'calcMode="discrete"/></g>', "the hawk's circle")
        for code in ("H1", "H2"):
            night = SET.header(code, HEADER, DARK, True, True)
            loops = [float(d) for d in re.findall(r'<g clip-path="url\(#gl\d+\)"><g>.*?type="translate" values="[^"]*" '
                                                 r'dur="([\d.]+)s"', night)]
            self.assertTrue(loops and all(4 <= d <= 8 for d in loops), (code, loops))

    def test_the_months_mark_hangs_at_the_top_centre_only_as_its_months_design(self):
        held = SET.on(JULY)
        for name in ("kit", "least"):
            h, _ = contents(KEY)[name]
            for night in (False, True):
                for draw in ("h1", "h2", "h3"):
                    wide = getattr(held, draw)(h, night, True), getattr(SET, draw)(h, night, True)
                    phone = getattr(held, draw + "_narrow")(h, night), getattr(SET, draw + "_narrow")(h, night)
                    for month, kept in (wide, phone):
                        self.assertTrue(any(L.startswith("mark") for L in month.layers), (name, draw, night))
                        self.assertFalse(any(L.startswith("mark") for L in kept.layers), (name, draw, night))

    def test_the_months_marks_box_is_kept_clear_of_every_scene(self):
        """The box the month's mark takes, and two units round it, holds nothing of a header's scene, wide or on a
        phone, by day or by night, for every shared content, whether or not the mark is drawn: the pennants' rope
        runs on behind it, but the pennants pause there, and the stars and everything else keep out."""
        drawers = {"H1": (SET.h1, SET.h1_narrow), "H2": (SET.h2, SET.h2_narrow), "H3": (SET.h3, SET.h3_narrow)}
        hooks = ("scene", "scene_narrow", "scene_under", "garland", "section_mark", "strip_mark", "rule_decor", "stars")
        for name, (h, _) in contents(KEY).items():
            for code, (wide, phone) in drawers.items():
                for night in (False, True):
                    for draw in (lambda: wide(h, night, True), lambda: phone(h, night)):
                        p, pixels = sprites(draw, *hooks)
                        x0, y0, x1, y1 = A.mark_box(p)
                        rope = {(x, y) for (x, y), c in p.layers["base"].items() if c in RAMP["wood"] and y < 8}
                        hits = sorted(xy for xy in pixels - rope if x0 <= xy[0] < x1 and y0 <= xy[1] < y1)
                        self.assertEqual(hits[:6], [], (name, code, p.w, night))

    def test_an_h3_has_its_great_keep_rising_the_strips_full_height(self):
        """At the right of every wide H3 stands the great keep, its banner's head two rows under the pennants and its
        moat on the rule, so it rises the strip's full height, sixty rows and more over the water where the strip
        allows; its curtain wall and its gate stand with it."""
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "great_keep", wraps=A.great_keep) as keep:
                    p, pixels = sprites(lambda: SET.h3(h, night, True), "scene")
                (call,) = keep.call_args_list
                g, room = call.args[3], call.kwargs["room"]
                self.assertGreaterEqual(call.kwargs["left"], 40, (name, night, "the wall and its gate"))
                top = min(y for _, y in pixels)
                self.assertTrue(15 <= top <= 18, (name, night, top))
                self.assertGreaterEqual(g - top, 54, (name, night))
                self.assertEqual(g - top + 1, room, (name, night))
                self.assertGreaterEqual(min(x for x, _ in pixels), 352, (name, night))

    def test_as_its_months_design_its_files_keep_their_room_and_their_motion(self):
        """Drawn as its month's design, with the mark, every header of the kit's own lines, the samples and the least
        a page can say is drawn at full weight with its motion at least 1,500 bytes under the budget, and the most a
        page can say, drawn lighter where it must be, still comes within the budget with all its motion."""
        held, cap = SET.on(JULY), BUDGET["header"]
        for name in ("kit", "repository", "profile", "least"):
            h, _ = contents(KEY)[name]
            for code in ("H1", "H2", "H3"):
                for theme in (DAY, DARK):
                    for wide, motion in ((True, True), (False, False)):
                        with mock.patch.dict(BUDGET, {"header": 10**9}):
                            svg = held.header(code, h, theme, wide, motion)
                        what = (name, code, theme["name"], wide)
                        self.assertLessEqual(len(svg.encode("utf-8")), cap - 1500, what)
                        self.assertEqual("<animate" in svg, motion, what)
        most, _ = contents(KEY)["most"]
        for code in ("H1", "H2", "H3"):
            for theme in (DAY, DARK):
                svg = held.header(code, most, theme, True, True)
                with mock.patch.dict(BUDGET, {"header": 10**9}):
                    full = held.header(code, most, theme, True, True)
                self.assertLessEqual(len(svg.encode("utf-8")), cap, (code, theme["name"]))
                self.assertEqual(svg.count("<animate"), full.count("<animate"), (code, theme["name"]))

    def test_a_phones_h1_has_the_whole_stronghold_under_its_words(self):
        """A phone's H1 stands the whole stronghold across its width under the words, at least 48 rows tall, the
        watchtower, the castle and the knight riding to the guard's tower, for every shared content."""
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "phone_castle", wraps=A.phone_castle) as castle:
                    p, pixels = sprites(lambda: SET.h1_narrow(h, night), "scene_narrow")
                self.assertTrue([c for c in castle.call_args_list if c.args[0] is p], (name, night))
                xs, ys = [x for x, _ in pixels], [y for _, y in pixels]
                self.assertLessEqual(min(xs), 6, (name, night))
                self.assertGreaterEqual(max(xs), 173, (name, night))
                self.assertGreaterEqual(max(ys) - min(ys) + 1, 48, (name, night))
                self.assertEqual(off_words(p, pixels), [], (name, night))

    def test_every_footer_stands_on_the_walls_footing_with_the_banner_after_its_last_cell(self):
        """Every footer stands on the wall's footing, a lit ledge over a course of blocks along its foot, rising where
        its cells leave it room; the stronghold's banner hangs on the wall after the way back up on a title block
        whose cells leave it the room, and on a scale bar's sheet wherever they do; its torches burn by night; and
        nothing of it comes within two units of a word."""
        h, f = contents(KEY)["repository"]
        for code, draw in (("F1", SET.f1), ("F2", SET.f2)):
            for night in (False, True):
                with mock.patch.object(A, "gonfalon", wraps=A.gonfalon) as banner:
                    p = draw(f, night)
                (call,) = banner.call_args_list
                ledge = [p.layers["base"].get((x, p.h - 5)) for x in range(8, p.w - 8)]
                self.assertGreater(ledge.count(A.stone_ramp(night)[6]), p.w // 2, (code, night, "the ledge"))
                if code == "F1":
                    self.assertGreater(call.args[1], max(b[2] for b in p.words), "after the way back up")
                    self.assertEqual(call.args[4], "lion", "the great banner of the lion")
                    self.assertEqual(bool(flickering(p)), night, "its torches burn by night")
        for name, (_, f) in contents(KEY).items():
            for draw in (SET.f1, SET.f2, SET.f1_narrow, SET.f2_narrow):
                for night in (False, True):
                    p, pixels = sprites(lambda: draw(f, night), "_footed")
                    self.assertEqual(off_words(p, pixels, margin=1)[:6], [], (name, draw.__name__, night))


class SharedBanners(unittest.TestCase):
    """The checks every registered set passes, over this set."""

    def test_every_file_is_the_sets_well_formed_linted_and_deterministic(self):
        drawn = {(n, c, fn): svg for n, c, fn, svg in every_banner()}
        for (name, code, fn), svg in drawn.items():
            minidom.parseString(svg)
            self.assertIn(f"<!--{KIT} v{KIT_VERSION} {KEY} ", svg, (name, fn))
            self.assertNotIn("<text", svg)
            for ch in DASHES:
                self.assertNotIn(ch, svg)
            cap = BUDGET["link"] if fn.startswith("link-") else BUDGET[DESIGNS[code].kind]
            self.assertEqual(lint(svg, budget=cap, tokens=SET.tokens), [], (name, code, fn))
        for name, code, fn, svg in draw_banners():
            self.assertEqual(svg, drawn[(name, code, fn)], (name, fn))

    def test_files_are_the_kits_sizes(self):
        for name, code, fn, svg in every_banner():
            w = int(re.search(r'width="(\d+)"', svg).group(1))
            if fn.startswith("link-"):
                self.assertLess(w, 300, fn)
            else:
                self.assertEqual(w, 360 if "narrow" in fn else 830, (name, fn))

    def test_only_a_wide_moving_header_moves(self):
        for name, code, fn, svg in every_banner():
            if "still" in fn or "narrow" in fn or fn.startswith(("footer", "link")):
                self.assertNotIn("<animate", svg, (name, fn))
        h, _ = contents(KEY)["repository"]
        self.assertIn("<animate", SET.header("H2", h, DAY, True, True))

    def test_text_colours_hold_4_5_on_the_paper_and_every_row_of_the_night(self):
        for night in (False, True):
            k = SET.ink(night)
            p = Pix(415, 200)
            grounds = {SET.bg_at(p, night, y) for y in range(p.h)}
            for role in ("title", "body", "muted", "accent"):
                for ground in grounds:
                    self.assertGreaterEqual(contrast(k[role], ground), 4.5, (night, role, ground))
            self.assertGreaterEqual(contrast(k["tag_ink"], k["tag"]), 4.5, (night, "tag"))

    def test_a_file_too_heavy_is_drawn_lighter_then_still_and_stays_the_sets(self):
        h, _ = contents(KEY)["repository"]
        full = SET.header("H2", h, DARK, True, True)
        self.assertIn("<animate", full)
        with mock.patch.dict(BUDGET, {"header": len(full.encode("utf-8")) - 1}):
            lighter = SET.header("H2", h, DARK, True, True)
        self.assertLess(len(lighter), len(full))
        self.assertIn("<animate", lighter, "a lighter drawing keeps its motion while it fits")
        self.assertIn(f"{KEY} H2 dark-->", lighter)
        with mock.patch.dict(BUDGET, {"header": 1000}):
            last = SET.header("H2", h, DARK, True, True)
        self.assertNotIn("<animate", last, "motion is the last thing to go")
        self.assertFalse(SET._lite, "the set is left drawing lighter")
        most, _ = contents(KEY)["most"]
        for code in ("H1", "H2", "H3"):
            for theme in (DAY, DARK):
                svg = SET.header(code, most, theme, True, True)
                self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"], (code, theme["name"]))

    def test_a_character_the_sets_letters_lack_hands_a_badge_back(self):
        self.assertFalse(SET.can_letter("flat", "中文"))


class SharedElements(unittest.TestCase):
    def test_every_element_is_the_sets_linted_deterministic_and_the_kits_size(self):
        files = draw_elements()
        again = draw_elements()
        for (eid, kind, variant, theme), svg in files.items():
            minidom.parseString(svg)
            self.assertEqual(svg, again[(eid, kind, variant, theme)], (eid, variant, theme))
            self.assertIn(f"<!--{KIT} v{KIT_VERSION} {KEY} elements {kind} ", svg, (eid, variant, theme))
            self.assertEqual(lint(svg, budget=BUDGET[E.KINDS[kind][2]], tokens=SET.tokens), [],
                             (eid, variant, theme))
            w = int(re.search(r'width="(\d+)"', svg).group(1))
            half = kind == "placard" or variant == "half" or (variant == "narrow" and kind in ("roster", "certificate"))
            self.assertEqual(w, 404 if half else 360 if variant == "narrow" else 830, (eid, variant, theme))

    def test_the_half_page_pair_is_drawn_level(self):
        pair = {eid: (d["kind"], E.describe(d["kind"], d)) for eid, d in ELEMENTS.items()
                if d["kind"] in ("roster", "certificate")}
        level = max(SET.element_height(kind, spec) for kind, spec in pair.values())
        heights = {re.search(r'height="(\d+)"', SET.element(kind, spec, DAY, "half", level)).group(1)
                   for kind, spec in pair.values()}
        self.assertEqual(len(heights), 1)

    def test_odd_data_is_drawn_whole(self):
        bare = {"kind": "roster", "subject": "x/y", "people": [
            {"name": "A PERSON WITH A NAME FAR LONGER THAN A COLUMN", "handle": "@" + "h" * 30, "initials": "AP",
             "n": 3, "first": "1 JAN 2020", "last": "31 DEC 2026"}]}
        svg = SET.element("roster", E.describe("roster", bare), DAY, "wide")
        self.assertEqual(lint(svg, budget=BUDGET["sheet"], tokens=SET.tokens), [])
        cert = dict(ELEMENTS["conformance"], name="an-extraordinarily-long-name",
                    ring_bottom="V12 · VERIFIED 31 DECEMBER 2026 AT LENGTH")
        for variant in ("wide", "half"):
            svg = SET.element("certificate", E.describe("certificate", cert), DARK, variant)
            self.assertEqual(lint(svg, budget=BUDGET["sheet"], tokens=SET.tokens), [], variant)


class SharedBadges(unittest.TestCase):
    def badge(self, style, **kw):
        args = dict(style=style, label="Build", message="Passing", icon="pulse", label_hex=PALETTE["black"],
                    message_hex=PALETTE["blue"], live=False, state=None, reserve=(), rels=["static/b.svg"], stamp=STAMP)
        args.update(kw)
        return SET.badge(**args)

    def check_file(self, svg, px_height, what):
        self.assertEqual(BD.lint(svg), [], what)
        self.assertEqual(colours(svg, SET.tokens), [], what)
        minidom.parseString(svg)
        self.assertEqual(int(re.search(r'height="(\d+)"', svg).group(1)), px_height, what)

    def test_every_style_classic_plate_and_live_is_the_kits_height_and_files(self):
        for style in BADGE_STYLES:
            one = self.badge(style)
            self.assertEqual(list(one), ["static/b.svg"])
            self.check_file(one["static/b.svg"], HEIGHTS[style], style)
            two = self.badge(PLATE + style, rels=["static/b.svg", "static/b-dark.svg"])
            self.assertEqual(list(two), ["static/b.svg", "static/b-dark.svg"])
            self.assertNotEqual(*two.values())
            for rel, svg in two.items():
                self.check_file(svg, HEIGHTS[style], (style, rel))
            for state in STATES:
                for form in (style, PLATE + style):
                    live = self.badge(form, live=True, state=state, label_hex=PALETTE["gold"],
                                      message_hex=PALETTE[state], rels=["dynamic/b.svg"])
                    self.assertEqual(list(live), ["dynamic/b.svg"])
                    self.check_file(live["dynamic/b.svg"], HEIGHTS[style], (form, state))

    def test_a_live_plate_keeps_its_width_whatever_it_says(self):
        widths = set()
        for state, message in (("green", "Passing"), ("red", "Failing"), ("slate", "No Data")):
            svg = self.badge(PLATE + "flat", live=True, state=state, message=message,
                             reserve=("Passing", "Failing", "No Data"), rels=["dynamic/b.svg"])["dynamic/b.svg"]
            widths.add(re.search(r'width="(\d+)"', svg).group(1))
        self.assertEqual(len(widths), 1)

    def test_every_letter_holds_4_5_on_its_block(self):
        pairs = [("label", *SET.badge_label()), ("gold", *SET.badge_gold())]
        pairs += [(f"state {s}", *SET.badge_states()[s]) for s in STATES]
        pairs += [(f"swatch {n}", bg, ink) for n, (bg, ink, _) in SET.badge_swatches().items()]
        for mode in ("day", "night"):
            k = SET.plate_colours(mode)
            pairs += [(f"{mode} block", k["block"], k["letters"]), (f"{mode} paper", k["paper"], k["ink"]),
                      (f"{mode} dot", k["dot"], k["ink"])]
        k = SET.plate_colours("live")
        pairs += [("live paper", k["paper"], k["ink"]), ("live dot", k["dot"], k["ink"])]
        for what, ground, ink in pairs:
            self.assertGreaterEqual(contrast(ink, ground), 4.5, what)

    def test_the_swatches_cover_every_family_a_written_colour_comes_in(self):
        swatches = SET.badge_swatches()
        self.assertGreaterEqual(len(swatches), 10)
        for name, (block, _, _) in swatches.items():
            self.assertIn(block, self.badge("flat", message_hex=block)["static/b.svg"], name)

    def test_what_the_sets_letters_cannot_draw_is_left_to_the_kit(self):
        self.assertIsNone(self.badge("flat", message="中文"))


if __name__ == "__main__":
    unittest.main()
