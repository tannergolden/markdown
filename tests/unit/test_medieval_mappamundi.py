# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Mappa Mundi set's own rules, which the checks every set shares cannot know: what the night alone shows (the
lantern's flame and its pool of light, the chart falling dark at its edges, the gilt letters) stays out of the
day's files, and the day's verdigris sea out of the night's; a title is engraved on a banderole, ink cut with an
engraver's shadow of fine lines by day and gilt by night; the wave lines drift, the needle swings and the ships
and the serpent ride the swell only in a wide moving header; every sprite, every shape a scene fills and every
rhumb line keeps clear of the words, and the sea is calm round them, its wave lines, water lines, rhumb lines and
grain masked away within two units of every word; an island is drawn as land on a chart, its coast inked and
hatched and the map's marks on it; a phone's H1 builds its map in the rows its words leave, and a phone's section
and strip stand their heroes under their words, the great compass rose and the great serpent, with islands in the
open sea over them, so that every phone header carries a chart; the longest page, drawn lighter to fit its budget,
keeps its whole chart and its motion; every sheet has the ruled border, a header the wind heads at its top corners
and a footer the scale bar to stand on, the sea along its foot and the open chart wherever its cells leave room,
and at its closing corner the compass rose in its medallion with the dividers laid before it and, by night, the
lantern, all of it two units clear of every word; a schematic's cards are cartouches with curled corners and their
icons in roundels, and a contributor is a wind head blowing away from its name; a link is a small file; every badge
is ruled round in ink along its top; and a counter's numerals and every text colour hold 4.5:1 on what they sit on,
the lantern's pool among it. It is drawn in the medieval collection's hand: it keeps to the hand as June's design
and kept all year, its words are set in the hand's inks, its lanterns burn the hand's flame and its wind heads are
on the hand's skin, its idles and sweeps keep the hand's time, the band of stars ends either side of the month's
mark and nothing of the chart enters the top centre, with the mark or without it, and its composition stands to the
hand's measure: the strip's great serpent rears the strip's whole height at its right, and a phone's heroes stand
forty-four rows and more under its words. The set is a theme, not a holiday on the calendar, so the checks every
registered set shares run here over the set directly, with the same contents and the same entry points."""
from __future__ import annotations

import contextlib
import datetime as dt
import re
import unittest
import xml.dom.minidom as minidom
from unittest import mock

from tests import support
from tests.unit.test_holiday_sets import DASHES, ELEMENTS, HEIGHTS, STAMP, contents

from domain import KIT, KIT_VERSION
from domain.badges import data as BD
from domain.banners.content import Header
from domain.banners.designs import DESIGNS, variants
from domain.canvas import BUDGET, DARK, DAY, colours, lint
from domain.elements import draw as E
from domain.holidays.designs.badges import PLATE, STATES, STYLES as BADGE_STYLES, TOP, inside
from domain.collections import zodiac
from domain.collections.hand import MEDIEVAL, check
from domain.collections.medieval_mappamundi import SET
from domain.collections.medieval_mappamundi import art as A
from domain.collections.medieval_mappamundi.art import POOL_WORDS
from domain.collections.medieval_mappamundi.palette import C, NIGHT_SKY, RAMP, X
from domain.holidays.pixel import BLINKS, Pix, contrast
from domain.palette import PALETTE

support.install()
KEY = SET.key
HEADER = Header(tone="standard", holiday=KEY)
# The set drawn as the collection's design for June, its month, with the month's mark at the top centre.
HELD = SET.on(dt.date(2026, 6, 1))
# A title that fills four full lines on a phone, its words running far down the sheet.
TALL = HEADER.with_(title="w" * 48)
INK, GOLD, FLAME, SEA = RAMP["ink"], RAMP["gold"], RAMP["flame"], RAMP["sea"]


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


def sprites(draw, *hooks, held=SET) -> tuple:
    """`draw()`'s drawing, and every pixel of the sprites the set's `hooks` (names of its drawing hooks) put on
    it, gathered as they draw: their pixels on every layer, the cells of the symbols they place, and the cells
    of the shapes they fill (which the set keeps in the drawing's `filled`). `held` is the set that draws, the
    one kept all year or the one drawn as June's design."""
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
            filled = set(getattr(p, "filled", ()))
            out = hook(*args, **kw)
            for L, c in p.layers.items():
                pixels.update(set(c) - before.get(L, set()))
            for L, uses in p.uses.items():
                for (_, sid, x, y, s) in uses[placed.get(L, 0):]:
                    pixels.update((x + dx * s, y + dy * s) for dx, dy in cells.get(sid, ()))
            pixels.update(set(getattr(p, "filled", ())) - filled)
            return out
        return drawn

    with mock.patch.object(Pix, "symbol", kept), \
            mock.patch.multiple(held, **{name: watched(getattr(held, name)) for name in hooks}):
        p = draw()
    return p, pixels


def drawn_by(name: str, draw) -> tuple:
    """`draw()`'s drawing, and the pixels the set's art function `name` lays on it as it draws: on every layer and
    in the cells it keeps as filled."""
    pixels, real = set(), getattr(A, name)

    def watched(p, *args, **kw):
        before = {L: set(c) for L, c in p.layers.items()}
        filled = set(getattr(p, "filled", ()))
        out = real(p, *args, **kw)
        for L, c in p.layers.items():
            pixels.update(set(c) - before.get(L, set()))
        pixels.update(set(getattr(p, "filled", ())) - filled)
        return out
    with mock.patch.object(A, name, watched):
        p = draw()
    return p, pixels


def served(draw, names) -> tuple:
    """`draw()`'s file, and which of the set's art functions `names` drew on the drawing it was written from: the
    last the kit made for it, drawn lighter where the full drawing came out over its budget."""
    calls, made = [], {}
    write = Pix.svg

    def written(self, *args, **kw):
        out = write(self, *args, **kw)
        made[out] = self
        return out
    with contextlib.ExitStack() as stack:
        stack.enter_context(mock.patch.object(Pix, "svg", written))
        for name in names:
            def watched(p, *args, _real=getattr(A, name), _name=name, **kw):
                calls.append((p, _name))
                return _real(p, *args, **kw)
            stack.enter_context(mock.patch.object(A, name, watched))
        svg = draw()
    return svg, {name for p, name in calls if p is made[svg]}


FOOTERS = {("F1", True): SET.f1, ("F2", True): SET.f2, ("F1", False): SET.f1_narrow, ("F2", False): SET.f2_narrow}


def off_words(p: Pix, pixels, margin=2) -> list:
    """The pixels among `pixels` that lie within `margin` units of a word's box."""
    return sorted(xy for xy in pixels if not p.clear_of_words(xy[0] - margin, xy[1] - margin, xy[0] + margin + 1,
                                                             xy[1] + margin + 1))


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
    def test_what_the_night_alone_shows_stays_out_of_the_day_and_the_days_sea_out_of_the_night(self):
        for code in ("H1", "H2", "H3"):
            day = SET.header(code, HEADER, DAY, True, True)
            night = SET.header(code, HEADER, DARK, True, True)
            fall = f'fill="{X["shade_ink"]}" fill-opacity=".34"'
            self.assertFalse(FLAME[6] in day, (code, "a flame by day"))
            self.assertFalse("pagilt" in day, (code, "the gilt letters by day"))
            self.assertFalse(fall in day, (code, "the chart falling dark by day"))
            self.assertTrue(FLAME[6] in night, (code, "the lantern burns"))
            self.assertTrue("pagilt" in night, (code, "the letters gilt"))
            self.assertTrue(fall in night, (code, "the chart falls dark at its edges"))
            self.assertTrue(f'fill="{C["sea"]}"' in day, (code, "the verdigris sea"))
            self.assertFalse(f'fill="{C["sea"]}"' in night, (code, "the sea is dark by night"))
            self.assertTrue(f'fill="{C["sea_night"]}"' in night, code)

    def test_the_lantern_pools_its_light_over_the_chart_and_stands_in_front_of_it(self):
        """By night the lantern's light lies in rings over the chart and everything on it, kept above the chart's
        rule, and the lantern stands in front of its own light; by day there is neither."""
        for code in ("H1", "H2", "H3"):
            night = SET.header(code, HEADER, DARK, True, True)
            pool = re.search(r'<clipPath id="pk0"><rect width="415" height="(\d+)"/></clipPath>', night)
            self.assertTrue(pool, (code, "the light is kept to the chart"))
            rings = re.search(r'<g clip-path="url\(#pk0\)" fill="(#[0-9A-F]{6})">(.*?)</g>', night)
            self.assertTrue(rings, code)
            self.assertEqual(rings.group(1), FLAME[3], code)
            self.assertGreaterEqual(rings.group(2).count("<ellipse"), 4, (code, "the light in rings"))
            self.assertLess(night.index('clip-path="url(#pk0)"'), night.rindex(FLAME[6]),
                            (code, "the lantern stands in front of its light"))
            self.assertNotIn("pk0", SET.header(code, HEADER, DAY, True, True), code)

    def test_where_the_light_reaches_a_word_it_is_held_to_what_the_inks_are_checked_against(self):
        """The rings strongest near the flame stop short of the words: the light over any word's box on the chart
        is no stronger than the pool the contrast check lays over the text and its ground."""
        drawers = {"H1": SET.h1, "H2": SET.h2, "H3": SET.h3}
        narrow = {"H1": SET.h1_narrow, "H2": SET.h2_narrow, "H3": SET.h3_narrow}
        cases = [(d, (h, True, True)) for d in drawers.values() for h, _ in contents(KEY).values()]
        cases += [(d, (h, True)) for d in narrow.values() for h, _ in contents(KEY).values()]
        pattern = r'<ellipse cx="([\d.]+)" cy="([\d.]+)" rx="([\d.]+)" ry="([\d.]+)" fill-opacity="([\d.]+)"'
        seen = 0
        for drawer, args in cases:
            p, _ = sprites(lambda: drawer(*args), "scene", "scene_narrow")
            rings = [tuple(map(float, m)) for raw in p.raws for m in re.findall(pattern, raw[2])
                     if "clip-path" in raw[2]]
            seen += bool(rings)
            rule = p.chart[1]
            for (x0, y0, x1, y1) in p.words:
                if y0 >= rule:
                    continue            # under the chart's rule, where the light is not let fall
                y1 = min(y1, rule)
                light = 1.0
                for (cx, cy, rx, ry, o) in rings:
                    nx, ny = min(max(cx, x0), x1), min(max(cy, y0), y1)
                    if ((nx - cx) / rx) ** 2 + ((ny - cy) / ry) ** 2 < 1:
                        light *= 1 - o
                self.assertLessEqual(1 - light, POOL_WORDS + 0.01, (x0, y0, x1, y1))
        self.assertGreater(seen, 10, "the lantern burns on most of them")

    def test_a_phones_section_stands_its_rose_under_its_words_whatever_its_title(self):
        """A phone's section stands its great compass rose under its words at its full size, by day and by night,
        whether its title is the kit's own or fills four lines; nothing of the map stands beside the title."""
        for h in (HEADER, TALL):
            for night in (False, True):
                with mock.patch.object(A, "rose", wraps=A.rose) as rose:
                    p = SET.h2_narrow(h, night)
                (_, cx, cy, R, _), _ = rose.call_args
                self.assertEqual((rose.call_count, R), (1, A.ROSE_R), (h.title, night))
                last = max(b[3] for b in p.words if b[1] < cy)
                self.assertGreaterEqual(cy - R - 5, last + 2, (h.title, night, "under the words"))
                _, beside = sprites(lambda: SET.h2_narrow(h, night), "scene_narrow")
                self.assertEqual(beside, set(), (h.title, night))

    def test_the_night_lights_the_footer(self):
        f = contents(KEY)["kit"][1]
        self.assertTrue(FLAME[6] in SET.footer("F1", f, DARK, True, False), "the lantern burns at the notes' corner")
        self.assertFalse(FLAME[6] in SET.footer("F1", f, DAY, True, False), "and is not there by day")
        self.assertTrue(FLAME[6] in SET.footer("F1", f, DARK, False, False), "on a phone too")


class Phones(unittest.TestCase):
    HOOKS = ("scene", "scene_narrow", "scene_under", "garland", "section_mark", "strip_mark", "rule_decor", "finish")

    def test_every_sprite_keeps_two_units_clear_of_every_word_on_a_phone(self):
        """On a phone the city, the serpent, the lantern, the rose, the wind heads and the marks are built to the
        rows the words leave free: no pixel of theirs lies within two units of a word's box, for any of the shared
        contents, by day or by night."""
        drawers = {"H1": SET.h1_narrow, "H2": SET.h2_narrow, "H3": SET.h3_narrow}
        for name, (h, _) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    p, pixels = sprites(lambda: drawer(h, night), *self.HOOKS)
                    hits = off_words(p, pixels)
                    self.assertEqual(hits[:6], [], (name, code, night, len(hits)))

    def test_every_sprite_keeps_two_units_clear_of_every_word_on_a_wide_header_too(self):
        """The map's drawings, the rhumb lines, the wind heads, the compass stars, the marks beside a title and
        the graduation along the rules keep the same two units from every word across a wide header."""
        drawers = {"H1": SET.h1, "H2": SET.h2, "H3": SET.h3}
        for name, (h, _) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    p, pixels = sprites(lambda: drawer(h, night, True), *self.HOOKS)
                    hits = off_words(p, pixels)
                    self.assertEqual(hits[:6], [], (name, code, night, len(hits)))

    def test_the_map_stands_where_the_words_leave_it_room(self):
        """The kit's own lines leave each phone its map; the least a page can say leaves the city its spire; and
        what cannot fit beside the most a page can say is left out rather than drawn over a word."""
        h, _ = contents(KEY)["kit"]
        for code in ("H1", "H2", "H3"):
            _, pixels = sprites(lambda: {"H1": SET.h1_narrow, "H2": SET.h2_narrow,
                                         "H3": SET.h3_narrow}[code](h, False), "scene_narrow", "scene_under")
            self.assertTrue(pixels, code)
        least, _ = contents(KEY)["least"]
        p, pixels = sprites(lambda: SET.h1_narrow(least, False), "scene_narrow")
        self.assertIn(SEA[4], {p.get(*xy) for xy in pixels}, "the spire's verdigris copper")
        most, _ = contents(KEY)["most"]
        p, pixels = sprites(lambda: SET.h1_narrow(most, False), "scene_narrow")
        self.assertEqual(off_words(p, pixels), [])

    def test_every_phone_header_carries_a_chart_of_its_own(self):
        """Every phone header of every shared content, by day and by night, as the kit draws it, carries a chart of
        the set's own and not a token of one. An H1 builds its map in the rows its words leave: four of its pieces
        at least (the city, the cog, the whale, the serpent, the dragon, an island, the rose), a ship or a beast
        among them. An H2 stands under its words the great compass rose with the cog, the whale and the cape's
        watch tower, and an H3 the great serpent with the walled city on its coast and the cog. By night the
        lantern burns on every one, and on an H2 it stands on the cape in the tower's place."""
        pieces = ("city", "cog", "whale", "serpent", "great_serpent", "dragon", "isle", "rose", "lantern", "tower")
        for name, (h, _) in contents(KEY).items():
            for code in ("H1", "H2", "H3"):
                for theme in (DAY, DARK):
                    with contextlib.ExitStack() as stack:
                        watched = {n: stack.enter_context(mock.patch.object(A, n, wraps=getattr(A, n))) for n in pieces}
                        svg = SET.header(code, h, theme, False, False)
                    drawn = {n for n, m in watched.items() if m.called}
                    case = (name, code, theme["name"])
                    night = bool(theme["dark"])
                    self.assertEqual("lantern" in drawn and FLAME[6] in svg, night, case)
                    if code == "H1":
                        self.assertGreaterEqual(len(drawn - {"lantern", "tower"}), 4, (case, drawn))
                        self.assertTrue(drawn & {"cog", "whale", "serpent", "dragon"}, case)
                    elif code == "H2":
                        self.assertTrue({"rose", "cog", "whale"} <= drawn, (case, drawn))
                        self.assertEqual("tower" in drawn, not night, (case, "the watch tower by day"))
                    else:
                        self.assertTrue({"great_serpent", "city", "cog"} <= drawn, (case, drawn))


class Maps(unittest.TestCase):
    def test_a_phones_open_sea_takes_islands_over_its_hero(self):
        """The least a page can say leaves a phone's H2 and H3 open sea beside the title, over the hero that stands
        under its words, and islands drawn as land take it there, by day and by night."""
        least, _ = contents(KEY)["least"]
        for draw in (SET.h2_narrow, SET.h3_narrow):
            for night in (False, True):
                with mock.patch.object(A, "isle", wraps=A.isle) as isle:
                    p = draw(least, night)
                self.assertTrue(isle.called, (draw.__name__, night))
                for call in isle.call_args_list:
                    self.assertLess(call.args[2], p.strip[0], (draw.__name__, night, "over the hero"))

    def test_an_island_is_drawn_as_land_on_a_chart(self):
        """An island's coast is inked, its shore hatched with short strokes out into the sea, its wash kept inside
        the ink, and on it the map's marks as it has room: a town on the biggest, a tower on the next, hills and
        trees on the rest."""
        for night in (False, True):
            for (rx, ry), mark in (((16, 8), "town"), ((12, 6), "tower"), ((9, 4), "hill"), ((8, 4), "tree")):
                p = Pix(80, 40)
                got = A.isle(p, 40, 20, rx, ry, night, seed=5)
                land = {(40 + x, 20 + y) for (x, y) in A.isle_cells(rx, ry, 5)}
                base = p.layers["base"]
                coast = A.K if not night else GOLD[3]
                rim = [q for q in got - land if base.get(q) == coast]
                self.assertGreater(len(rim), 2 * rx, (rx, night, "the coast inked"))
                hatch = INK[4] if not night else GOLD[1]
                self.assertGreater(sum(base.get(q) == hatch for q in got - land), rx, (rx, night, "the shore hatched"))
                colours = {base.get(q) for q in land}
                k = -1 if night else 0
                want = {"town": RAMP["verm"][5 + k], "tower": RAMP["verm"][5 + k], "hill": A.isle_pal(night)["h"],
                        "tree": RAMP["green"][4 + k]}[mark]
                self.assertIn(want, colours, (rx, night, mark))


class Titles(unittest.TestCase):
    def test_a_title_is_engraved_on_a_banderole_by_day_and_gilt_by_night(self):
        day = SET.header("H1", HEADER, DAY, True, True)
        self.assertIn('id="pahatchd4d"', day, "the engraver's shadow in fine lines")
        self.assertIn(f'<g stroke="{INK[1]}">', day, "the letters, solid ink")
        self.assertIn(f'fill="{RAMP["parch"][6]}"', day, "the banderole's face")
        night = SET.header("H1", HEADER, DARK, True, True)
        self.assertIn('id="pagilt4n"', night, "gilt letters, a band of gold a row of the face")
        self.assertIn('id="pahatchn4n"', night, "their shadow cut in gilt lines")
        self.assertIn(f'fill="{GOLD[3]}"', night, "the banderole's gilt edge")

    def test_only_a_wide_moving_header_moves_its_waves_its_needle_and_its_beasts(self):
        moving = SET.header("H1", HEADER, DAY, True, True)
        self.assertIn('attributeName="transform" type="translate" values="0;1;2;3', moving, "the waves drift")
        self.assertIn('values="0 0;0 0;0 -1;0 -1;0 -1;0 0;0 0;0 1;0 1;0 1"', moving, "the cog bobs")
        self.assertIn('<g opacity="0">', moving, "the needle swings in steps")
        still = SET.header("H1", HEADER, DAY, True, False)
        self.assertNotIn("<animate", still)
        for theme in (DAY, DARK):
            self.assertNotIn("<animate", SET.header("H1", HEADER, theme, False, False))

    def test_the_rose_rakes_its_rhumb_lines_across_the_sea(self):
        svg = SET.header("H2", HEADER, DAY, True, True)
        self.assertIn('stroke-width=".5"', svg, "the rhumb lines")
        self.assertIn(GOLD[5], svg, "the rose's gilt points")

    def test_every_sheet_has_the_ruled_border_and_a_header_its_wind_heads(self):
        for code in ("H1", "H2", "H3"):
            for wide in (True, False):
                svg = SET.header(code, HEADER, DAY, wide, False)
                self.assertIn('<pattern id="frh"', svg, (code, wide))
                self.assertIn('<pattern id="tb"', svg, (code, wide, "the band of scales and gilt stars"))
                self.assertEqual(svg.count('transform="matrix(-1 0 0 1 22 0)"'), 1, (code, wide, "the right head"))
        f = contents(KEY)["kit"][1]
        self.assertNotIn("matrix(-1", SET.footer("F1", f, DAY, True, False), "a footer has corner pieces instead")
        svg = SET.element("roster", E.describe("roster", ELEMENTS["contributors"]), DAY, "wide")
        self.assertIn('<pattern id="frh"', svg)


class Calm(unittest.TestCase):
    @staticmethod
    def hidden(p: Pix) -> set:
        """The cells the sheet's calm hides wholly: the rectangles of its mask laid in full ink."""
        d = re.search(rf'<path fill="{INK[0]}" d="([^"]+)"/>', p.defs[p.calm_at])
        cells = set()
        for x, y, w, h in re.findall(r"M(\d+) (\d+)h(\d+)v(\d+)h-\d+z", d.group(1) if d else ""):
            x, y, w, h = int(x), int(y), int(w), int(h)
            cells |= {(xx, yy) for xx in range(x, x + w) for yy in range(y, y + h)}
        return cells

    def test_nothing_of_the_seas_marks_shows_within_two_units_of_a_word(self):
        """On every header, wide and on a phone, by day and by night, on every footer and on every element, the calm
        hides the wave lines, the water lines, the rhumb lines and the parchment's grain, foxing and fold wholly
        within two units of every word on the chart."""
        sheets = []
        for h, f in contents(KEY).values():
            for night in (False, True):
                sheets += [SET.h1(h, night, True), SET.h2(h, night, True), SET.h3(h, night, True),
                           SET.h1_narrow(h, night), SET.h2_narrow(h, night), SET.h3_narrow(h, night)]
                sheets += [draw(f, night) for draw in FOOTERS.values()]
        for d in ELEMENTS.values():
            if d["kind"] != "placard":
                for night in (False, True):
                    sheets.append(SET.draw_element(d["kind"], E.describe(d["kind"], d), night, "wide", None))
        for p in sheets:
            hidden = self.hidden(p)
            top = getattr(p, "chart", (None, p.h))[1]
            for (x0, y0, x1, y1) in p.words:
                missed = [(xx, yy) for yy in range(max(0, y0 - 2), min(top, y1 + 2))
                          for xx in range(max(0, x0 - 2), min(p.w, x1 + 2)) if (xx, yy) not in hidden]
                self.assertEqual(missed[:4], [], (p.w, p.h, (x0, y0, x1, y1)))

    def test_the_seas_marks_lie_under_the_calm_and_a_placard_is_plain(self):
        """The wave lines, the water lines along the coasts, the grain and the rhumb lines are drawn whole under the
        calm, so the open sea keeps them from edge to edge; a footer's parchment is grained and foxed under the same
        calm, laid once its words are all set, and a placard's, which its words cover from end to end, is left
        plain."""
        for code in ("H1", "H2", "H3"):
            for theme in (DAY, DARK):
                svg = SET.header(code, HEADER, theme, True, True)
                self.assertIn(f'<g mask="url(#calm)"><g><rect x="-{A.WAVE_W}"', svg, (code, "the wave lines drift"))
                self.assertRegex(svg, r'<g mask="url\(#calm\)">(<path stroke="#[0-9A-F]{6}" d="[^"]+"/>)?<rect '
                                      r'width="415" height="\d+" fill="url\(#pg\)"/>', (code, "the grain"))
                self.assertTrue(re.search(r'<g mask="url\(#calm\)"><path stroke="#[0-9A-F]{6}" stroke-width=".5"', svg)
                                or code == "H3", (code, "the rhumb lines"))
        f = contents(KEY)["kit"][1]
        for theme in (DAY, DARK):
            for code in ("F1", "F2"):
                for wide in (True, False):
                    svg = SET.footer(code, f, theme, wide, False)
                    self.assertRegex(svg, r'<g mask="url\(#calm\)"><rect width="\d+" height="\d+" fill="url\(#fgg\)"/>',
                                     (code, wide, "the footer's grain, calmed"))
                    self.assertIn(f'<path fill="{INK[0]}"', re.search(r'<mask id="calm".*?</mask>', svg).group(0))
            card = SET.element("placard", E.describe("placard", ELEMENTS["action"]), theme, "wide")
            self.assertNotIn('fill="url(#plg)"', card)

    def test_the_water_lines_follow_the_coasts_out_into_the_sea_and_never_onto_the_land(self):
        laid = []
        real = A._put

        def kept(cols, c, x, y):
            laid.append((x, y))
            return real(cols, c, x, y)
        for kind in ("H1", "H2", "H3"):
            p = Pix(415, 120)
            lands = A.chart_lands(kind, 415, 110)
            laid.clear()
            with mock.patch.object(A, "_put", kept):
                A._water_lines(p, lands, 110, False)
            self.assertTrue(laid or kind == "H3", kind)
            for (x, y) in laid:
                for side, _, reach in lands:
                    r = reach[y]
                    self.assertFalse(r is not None and (x <= r if side < 0 else x >= r), (kind, x, y))


class Footers(unittest.TestCase):
    def test_a_footer_stands_on_the_scale_bar_with_the_dividers_at_its_corner(self):
        f = contents(KEY)["kit"][1]
        for code in ("F1", "F2"):
            for wide in (True, False):
                svg = SET.footer(code, f, DAY, wide, False)
                self.assertIn('<pattern id="frs"', svg, (code, wide))
        for wide in (True, False):
            self.assertIn(RAMP["slate"][6], SET.footer("F1", f, DAY, wide, False), "the dividers' steel points")
        self.assertNotIn('<pattern id="frs"', SET.header("H1", HEADER, DAY, True, True))

    def test_the_footers_last_pass_keeps_two_units_clear_of_every_word(self):
        """The closing piece, the lantern, the sea along the foot and the open chart with what sails it are built
        to the room the footer's words leave: no pixel of theirs and no cell of their sea lies within two units of a
        word's box, for any of the shared contents, wide and on a phone, by day and by night."""
        for name, (_, f) in contents(KEY).items():
            for (code, wide), draw in FOOTERS.items():
                for night in (False, True):
                    p, pixels = drawn_by("footer_finish", lambda: draw(f, night))
                    self.assertEqual(off_words(p, pixels)[:6], [], (name, code, wide, night))
                    sea = C["sea_night"] if night else C["sea"]
                    for group in re.findall(rf'<g fill="{sea}">(.*?)</g>', "".join(p.under)):
                        for box in re.findall(r'<rect x="(\d+)" y="(\d+)" width="(\d+)" height="(\d+)"/>', group):
                            x, y, w, h = map(int, box)
                            self.assertTrue(p.clear_of_words(x - 2, y - 2, x + w + 2, y + h + 2),
                                            (name, code, wide, night, x, y, w, h))

    def test_the_closing_corner_holds_the_compass_rose_in_its_medallion(self):
        """At the corner of the closing notes the compass rose stands in its medallion, a roundel of the sea in a
        ring of brass, with the dividers laid before it; by night the lantern burns beside it, and its light where
        it reaches a word is held to what the inks are checked against."""
        f = contents(KEY)["kit"][1]
        for draw in (SET.f1, SET.f1_narrow):
            for night in (False, True):
                p, pixels = drawn_by("closing_piece", lambda: draw(f, night))
                self.assertTrue(pixels, (draw.__name__, night))
                cx, _ = p.corner
                xs = [x for (x, _) in pixels]
                self.assertTrue(cx - 30 < min(xs) and max(xs) < cx + 24, (draw.__name__, night, min(xs), max(xs)))
                colours = {p.get(*q) for q in pixels}
                self.assertIn(C["sea_night"] if night else C["sea"], colours, "the medallion's sea")
                self.assertIn(GOLD[5 + (-1 if night else 0)], colours, "its ring of brass")
                self.assertIn(RAMP["slate"][6 if not night else 5], colours, "the dividers' steel")
                self.assertEqual(FLAME[6] in {p.get(*q, L="lamp") for q in pixels}, night, "the lantern by night")
                ring = r'<ellipse cx="([\d.]+)" cy="([\d.]+)" rx="([\d.]+)" ry="([\d.]+)" fill-opacity="([\d.]+)"'
                rings = [tuple(map(float, m)) for raw in p.raws for m in re.findall(ring, raw[2])]
                self.assertEqual(bool(rings), night)
                for (x0, y0, x1, y1) in p.words:
                    light = 1.0
                    for (lx, ly, rx, ry, o) in rings:
                        nx, ny = min(max(lx, x0), x1), min(max(ly, y0), y1)
                        if ((nx - lx) / rx) ** 2 + ((ny - ly) / ry) ** 2 < 1:
                            light *= 1 - o
                    self.assertLessEqual(1 - light, POOL_WORDS + 0.01, (x0, y0, x1, y1))

    def test_a_phones_footer_without_closing_notes_holds_the_closing_piece_too(self):
        """A phone's F1 with no closing notes, the repository's and the profile's, leaves room only for a small
        medallion between its cells' words: the closing piece stands there all the same, the rose in its ring of
        brass with the dividers before it and by night the lantern, two units clear of every word."""
        for name in ("repository", "profile"):
            f = contents(KEY)[name][1]
            self.assertFalse(f.on("closing"), name)
            for night in (False, True):
                p, pixels = drawn_by("closing_piece", lambda: SET.f1_narrow(f, night))
                self.assertTrue(pixels, (name, night))
                self.assertEqual(off_words(p, pixels), [], (name, night))
                colours = {p.get(*q) for q in pixels}
                self.assertIn(GOLD[5 + (-1 if night else 0)], colours, (name, night, "the ring of brass"))
                self.assertIn(RAMP["slate"][6 if not night else 5], colours, (name, night, "the dividers' steel"))
                self.assertEqual(FLAME[6] in {p.get(*q, L="lamp") for q in pixels}, night, (name, night))

    def test_where_a_footers_cells_leave_room_it_opens_onto_the_chart(self):
        """A footer whose cells leave a stretch with no word in it opens onto the chart there, the sea from rule to
        foot with what sails it; one whose cells all leave rows under their words has the sea along its foot."""
        for name in ("repository", "least"):
            f = contents(KEY)[name][1]
            p = SET.f1(f, False)
            self.assertIn(C["sea"], "".join(p.under), name)
            _, sailing = drawn_by("_furnish", lambda: SET.f1(f, False))
            self.assertTrue(sailing, (name, "something sails the open chart"))
        laid = []
        real = A.sea_band

        def kept(p, night, **kw):
            out = real(p, night, **kw)
            laid.extend(out)
            return out
        with mock.patch.object(A, "sea_band", kept):
            SET.f2(contents(KEY)["kit"][1], False)
        self.assertTrue(laid and all(coasts is None for *_, coasts in laid), "the sea along the foot")
        self.assertGreater(sum(x1 - x0 for x0, x1, *_ in laid), 0.7 * (415 - 2 * A.BAND))

    def test_a_link_is_a_small_cartouche_with_a_bold_icon(self):
        for i, label in enumerate(("Issues", "Pull Requests", "Releases", "Actions")):
            for theme in (DAY, DARK):
                svg = SET.link(label, theme, i)
                self.assertLess(len(svg.encode("utf-8")), 2500, (label, theme["name"]))


class Badges(unittest.TestCase):
    def test_every_badge_is_ruled_round_in_ink_with_its_letters_under_the_rule(self):
        for style in BADGE_STYLES:
            drawn = [SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                       SET.badge_states()["green"])]
            drawn += [SET.plate_badge(style, "License", "MIT", "scale", mode) for mode in ("day", "night")]
            for p in drawn:
                corner = BADGE_STYLES[style]["corner"]
                top = [x for x in range(p.w) if inside(x, 0, p.w, p.h, corner) and x % 4 != 2]
                self.assertTrue(all(p.get(x, 0) == INK[1] for x in top), (style, "the rule along its top"))
                self.assertTrue(all(y >= TOP for _, _, _, y, _ in p.uses["base"]), "the letters sit under the rule")

    def test_a_counters_numerals_hold_4_5_on_their_scale(self):
        for night in (False, True):
            q = Pix(20, 20)
            SET.counter_cell(q, 2, 2, night)
            face = q.layers["base"][(7, 8)]
            self.assertGreaterEqual(contrast(SET.counter_ink(night, False), face), 4.5, night)
            self.assertGreaterEqual(contrast(SET.counter_ink(night, True), face), 2.0, night)


class Contrast(unittest.TestCase):
    def test_every_text_colour_holds_4_5_on_every_ground_the_chart_has(self):
        """The parchment, the sea and the land by day; by night every band of the parchment, the sea, the land and
        the unknown land, bare and under the lantern's light as strong as it falls where a word lies, which lies
        over the letters as over their ground."""
        day = [C["paper"], C["sea"], C["land"]]
        night = list(NIGHT_SKY) + [C["sea_night"], C["land_night"], RAMP["night"][2]]

        def lit(colour, alpha):
            g = [int(colour[i:i + 2], 16) for i in (1, 3, 5)]
            f = [int(FLAME[3][i:i + 2], 16) for i in (1, 3, 5)]
            return "#%02X%02X%02X" % tuple(round(a + (b - a) * alpha) for a, b in zip(g, f))
        for is_night, grounds in ((False, day), (True, night)):
            k = SET.ink(is_night)
            for role in ("title", "body", "muted", "accent"):
                for ground in grounds:
                    for alpha in ((0, POOL_WORDS) if is_night else (0,)):
                        self.assertGreaterEqual(contrast(lit(k[role], alpha), lit(ground, alpha)), 4.5,
                                                (is_night, role, ground, alpha))


# The drawers of every header, wide and on a phone, by their code.
HEADERS = {("H1", True): lambda held: held.h1, ("H2", True): lambda held: held.h2, ("H3", True): lambda held: held.h3,
           ("H1", False): lambda held: held.h1_narrow, ("H2", False): lambda held: held.h2_narrow,
           ("H3", False): lambda held: held.h3_narrow}


def header(held, code, wide, h, night) -> Pix:
    """One header's drawing as `held` draws it, a wide one moving."""
    draw = HEADERS[(code, wide)](held)
    return draw(h, night, True) if wide else draw(h, night)


class Hand(unittest.TestCase):
    """The set is drawn in the medieval collection's hand: it keeps to it as June's design and kept all year, its
    words are in the hand's inks, its lanterns burn the hand's flame and its wind heads' faces are on the hand's
    skin, its idles and sweeps keep the hand's time, the top centre of every header is kept clear for the month's
    mark, and its composition stands to the hand's measure."""

    def test_it_keeps_to_its_hand_as_junes_design_and_kept_all_year(self):
        self.assertEqual(check(HELD), [])
        self.assertEqual(check(SET), [])
        self.assertEqual((HELD.collection, HELD.month), ("medieval", 6))

    def test_its_words_are_in_the_hands_inks(self):
        """The words and the quieter words of its headers and footers, a link's letters and a legend box's are set
        in the hand's two inks, by day and by night; its titles keep the chart's own ink and gilt."""
        for night in (False, True):
            k = SET.ink(night)
            self.assertEqual((k["body"], k["muted"]), (MEDIEVAL.body[night], MEDIEVAL.muted[night]), night)
            self.assertEqual(SET.link_colours(night)[2], MEDIEVAL.body[night], (night, "a link's letters"))
            self.assertEqual(SET.plate_colours("night" if night else "day")["ink"], MEDIEVAL.body[night], night)
            self.assertIn(k["title"], (RAMP["ink"][1], RAMP["gold"][5]), (night, "the title's own ink and gilt"))

    def test_every_flame_burns_on_the_hands_flame(self):
        """The chart's flame is the hand's: the lantern's flame, its bright heart and the light through its horn,
        the footer's small lantern and every pool of their light are tones of the hand's flame ramp."""
        flame = MEDIEVAL.ramp("flame")
        self.assertEqual(RAMP["flame"], flame)
        self.assertLessEqual({c for ch, c in A.lantern_pal(True).items() if ch in "oGhgFW"}, set(flame))
        for big in (True, False):
            p = Pix(60, 60)
            A.lantern(p, 20, 50, True, motion=True, big=big)
            burning = {c for L in p.layers if L.startswith("lampf") for c in p.layers[L].values()}
            self.assertTrue(burning, big)
            self.assertLessEqual(burning, set(flame), (big, "the flame"))
            self.assertIn(flame[6], burning, (big, "its heart the hand's brightest"))
        p = Pix(40, 40)
        A.small_lantern(p, 10, 30, True)
        lit = {c for c in p.layers["lamp"].values() if ":" not in c} - set(RAMP["gold"]) - {A.K, RAMP["parch"][6]}
        self.assertTrue(lit)
        self.assertLessEqual(lit, set(flame), "the small lantern")
        for code in ("H1", "H2", "H3"):
            night = SET.header(code, HEADER, DARK, True, True)
            for fill in re.findall(r'<g clip-path="url\(#pk\d+\)" fill="(#[0-9A-F]{6})">', night):
                self.assertIn(fill, flame, (code, "the lantern's light pooled on the chart"))

    def test_its_wind_heads_faces_are_on_the_hands_skin(self):
        """A wind head's face and a contributor's are on the hand's lightest skin: the face its base tone and its
        nose a tone darker, by day and by night, and by day its blown cheek a tone lighter."""
        skin = MEDIEVAL.ramp("skin0")
        self.assertEqual(RAMP["skin"], skin)
        for night in (False, True):
            pal = A.wind_pal(night)
            self.assertEqual((pal["F"], pal["n"]), (skin[3], skin[2]), night)
            self.assertEqual(pal["S"], skin[3 if night else 4], night)
            p = Pix(60, 40)
            A.wind_avatar(p, 30, 20, 0, night)
            faces = {c for c in p.layers["base"].values() if c in skin}
            self.assertLessEqual({skin[3], skin[2]}, faces, (night, "a contributor's face"))

    def test_its_idles_and_sweeps_keep_the_hands_time(self):
        """In a moving header the stars twinkle and the lantern flickers on the engine's cadences; the cogs bob, the
        serpent's coils rise and sink, the whale breathes and the needle swings on idles of four to eight seconds;
        and the sea's wave lines drift on a slow sweep of twenty-four to forty-eight."""
        cadences = {v[2] for v in BLINKS.values()}
        seen = set()
        for code in ("H1", "H2", "H3"):
            for theme in (DAY, DARK):
                svg = HELD.header(code, HEADER, theme, True, True)
                for attrs in re.findall(r'<animate(?:Transform)? ([^>]*)/>', svg):
                    dur = float(re.search(r'dur="([\d.]+)s"', attrs).group(1))
                    if 'type="translate"' in attrs and re.search(r'values="0;1;2;', attrs):
                        self.assertTrue(24 <= dur <= 48, (code, theme["name"], "the waves", dur))
                        seen.add("sweep")
                    elif 'attributeName="opacity"' in attrs and any(v[0] in attrs for v in BLINKS.values()):
                        self.assertIn(dur, cadences, (code, theme["name"], attrs))
                        seen.add("cadence")
                    else:
                        self.assertTrue(4 <= dur <= 8, (code, theme["name"], "an idle", attrs))
                        seen.add("idle")
        self.assertEqual(seen, {"sweep", "cadence", "idle"})
        self.assertTrue(all(4 <= d <= 8 for d in A.BOB))
        self.assertTrue(4 <= A.BREATH <= 8)

    def test_the_band_of_stars_ends_either_side_of_the_months_mark(self):
        """The band across a header's top runs on behind the month's mark, but its gilt stars are an even number
        set evenly along it, so the run of them ends either side of the top centre and none is cut by the mark."""
        for wide in (True, False):
            for night in (False, True):
                p = header(HELD, "H1", wide, HEADER, night)
                x0, _, x1, _ = A.top_centre(p)
                star = p.syms[("giltstar", night)]
                xs = sorted(x for L in p.uses for (_, sid, x, _, _) in p.uses[L] if sid == star)
                self.assertTrue(xs and len(xs) % 2 == 0, (wide, night, xs))
                for x in xs:
                    self.assertTrue(x + 13 <= x0 or x - 2 >= x1, (wide, night, x, "a star in the top centre"))
                left = [x for x in xs if x < x0]
                self.assertEqual(len(left), len(xs) // 2, (wide, night, "as many stars on each side"))

    def test_nothing_of_the_chart_enters_the_top_centre_with_the_mark_or_without_it(self):
        """In every header, wide and on a phone, by day and by night, for every shared content, as June's design and
        kept all year, nothing the scenes, the islands, the routes and the marks beside the title lay on the chart
        lies in the box the month's mark is drawn in or the two units round it, below the band across the top."""
        hooks = ("scene", "scene_narrow", "scene_under", "section_mark", "strip_mark", "finish")
        for name, (h, _) in contents(KEY).items():
            for held in (HELD, SET):
                for (code, wide), draw in HEADERS.items():
                    for night in (False, True):
                        p, pixels = sprites(lambda: header(held, code, wide, h, night), *hooks, held=held)
                        x0, y0, x1, y1 = A.top_centre(p)
                        inside = sorted((x, y) for (x, y) in pixels if x0 <= x < x1 and A.TOP_BAND <= y < y1)
                        self.assertEqual(inside[:4], [], (name, held.day, code, wide, night))

    def test_the_least_phone_section_keeps_its_rose_whole_and_clear_of_the_mark(self):
        """The least a page can say still stands a phone's section's great compass rose under its words: whole,
        clear of the box the month's mark takes, and in the same place by day and by night whether the mark is
        drawn or not."""
        least, _ = contents(KEY)["least"]
        for night in (False, True):
            placed = []
            for held in (HELD, SET):
                with mock.patch.object(A, "rose", wraps=A.rose) as rose:
                    p = held.h2_narrow(least, night)
                self.assertEqual(rose.call_count, 1, (night, held.day, "the rose"))
                (_, cx, cy, R, _), _ = rose.call_args
                cells = {(cx + x, cy + y): c for (x, y), c in A.rose_cells(0.0, 0.0, R, night).items()}
                self.assertEqual({q: p.get(*q) for q in cells}, cells, (night, held.day, "whole"))
                x0, y0, x1, y1 = A.top_centre(p)
                self.assertFalse([q for q in cells if x0 <= q[0] < x1 and y0 <= q[1] < y1], (night, held.day))
                placed.append((cx, cy, R))
            self.assertEqual(placed[0], placed[1], (night, "the same place with the mark and without it"))

    def test_its_composition_stands_to_the_hands_measure(self):
        """A wide H1 stands a scene on each side of its words, the walled city at the left and the dragon over
        the serpent at the right, each rising from the rule at least seven tenths of the way to the band across the
        top; and a phone's H1 builds its map at least 48 rows tall under its words."""
        self.assertGreaterEqual(SET.phone_scene_rows, 48)
        for name in ("kit", "repository", "profile", "least"):
            h, _ = contents(KEY)[name]
            p, pixels = sprites(lambda: HELD.h1(h, False, False), "scene", held=HELD)
            rule = p.chart[1]
            words = [b for b in p.words if b[3] <= rule]
            left = [y for (x, y) in pixels if x < min(b[0] for b in words) - 2 and y < rule]
            right = [y for (x, y) in pixels if x > max(b[2] for b in words) + 2 and y < rule]
            for side, ys in (("left", left), ("right", right)):
                self.assertGreaterEqual((rule - min(ys)) / (rule - A.TOP_BAND), 0.7, (name, side))
            p, pixels = sprites(lambda: HELD.h1_narrow(h, False), "scene_narrow", held=HELD)
            self.assertGreaterEqual(p.chart[1] - min(y for _, y in pixels), 48, (name, "the phone's map"))

    def test_the_strips_hero_rears_the_strips_whole_height(self):
        """A wide strip's hero is the great sea serpent at its right, by day and by night, for every shared content:
        it rears from the foam at the rule to its horns under the wind's stream across the top, at least 57 rows,
        with two coils behind it by day and one by night beside the lantern."""
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "great_serpent", wraps=A.great_serpent) as serpent:
                    p, pixels = drawn_by("great_serpent", lambda: HELD.h3(h, night, True))
                (_, x, wl, top, _), kw = serpent.call_args
                case = (name, night)
                self.assertEqual((serpent.call_count, top, kw["coils"]), (1, A.SERPENT_TOP, 1 if night else 2), case)
                rule = p.chart[1]
                self.assertEqual(min(y for _, y in pixels), top, case)
                self.assertGreaterEqual(rule - top, 57, case)
                self.assertGreaterEqual(min(px for px, _ in pixels), p.w * 0.8, (case, "at the right"))

    def test_the_serpents_boxes_hold_all_it_draws(self):
        """The boxes a strip's placing keeps clear of every word (see `art.serpent_boxes`) hold every pixel the great
        serpent draws, short or tall, coiled once or twice, by day and by night."""
        for wl, top, coils in ((68, 14, 2), (66, 14, 1), (117, 14, 2), (50, 8, 1)):
            for night in (False, True):
                p = Pix(415, 140)
                A.great_serpent(p, 300, wl, top, night, coils=coils)
                cells = set(p.filled) | {q for layer in p.layers.values() for q in layer}
                boxes = A.serpent_boxes(300, wl, top, coils)
                out = sorted(q for q in cells if not any(b[0] <= q[0] < b[2] and b[1] <= q[1] < b[3] for b in boxes))
                self.assertEqual(out[:4], [], (wl, top, coils, night))

    def test_a_phones_heroes_stand_forty_four_rows_under_its_words(self):
        """For every shared content, by day and by night, a phone's section stands its great compass rose and its
        strip its great serpent under its words, two units and more below the last of them, each at least 44
        rows tall."""
        for name, (h, _) in contents(KEY).items():
            for code, piece in (("H2", "rose"), ("H3", "great_serpent")):
                for night in (False, True):
                    draw = HELD.h2_narrow if code == "H2" else HELD.h3_narrow
                    p, pixels = drawn_by(piece, lambda: draw(h, night))
                    rows = sorted({y for _, y in pixels})
                    last = max(b[3] for b in p.words if b[1] < rows[0])
                    case = (name, code, night)
                    self.assertGreaterEqual(rows[0], last + 2, (case, "under the words"))
                    self.assertGreaterEqual(rows[-1] + 1 - rows[0], 44, case)


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

    def test_ordinary_content_is_drawn_at_full_weight(self):
        """The kit's own lines, the samples and the least a page can say are served as drawn at full weight, with
        their motion and, as June's design, the month's mark, and 1.5 KB to spare under a header's budget; only the
        stress contents are served lighter."""
        for name in ("kit", "repository", "profile", "least"):
            h, f = contents(KEY)[name]
            for night in (False, True):
                for code in ("H1", "H2", "H3"):
                    theme = DARK if night else DAY
                    with mock.patch.dict(BUDGET, {"header": 10**9}):
                        full = HELD.header(code, h, theme, True, True)
                    svg = HELD.header(code, h, theme, True, True)
                    self.assertEqual(svg, full, (name, code, night, "served at full weight"))
                    self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"] - 1500, (name, code, night))
                    self.assertIn("<animate", svg)
                    self.assertIn(zodiac.LAPIS[3], svg, (name, code, night, "the month's mark"))
                for code, draw in (("H1", HELD.h1_narrow), ("H2", HELD.h2_narrow), ("H3", HELD.h3_narrow)):
                    svg = draw(h, night).svg("t", "d", still=True)
                    self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"], (name, code, night, "phone"))
                for code, draw in (("F1", SET.f1), ("F2", SET.f2)):
                    svg = draw(f, night).svg("t", "d", still=True)
                    self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["footer"], (name, code, night))

    def test_text_colours_hold_4_5_on_the_paper_and_every_row_of_the_night(self):
        for night in (False, True):
            k = SET.ink(night)
            p = Pix(415, 200)
            grounds = {SET.bg_at(p, night, y) for y in range(p.h)}
            for role in ("title", "body", "muted", "accent"):
                for ground in grounds:
                    self.assertGreaterEqual(contrast(k[role], ground), 4.5, (night, role, ground))
            self.assertGreaterEqual(contrast(k["tag_ink"], k["tag"]), 4.5, (night, "tag"))
            fill, _, ink, _ = SET.link_colours(night)
            self.assertGreaterEqual(contrast(ink, fill), 4.5, (night, "a link's letters"))

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

    def test_the_longest_page_keeps_its_whole_chart_and_its_motion_within_the_budget(self):
        """The most a page can say comes out over the budget in its wide H1 at full weight. Served as the kit serves
        it, each of its wide H1 and H2, by day and by night, moving and still, fits the budget, moves where it is
        asked to, and holds every piece of the chart its full drawing holds: the city on its coast with its hills
        and river, the rose and its needle, the cog on her route, the tower, the dragon, the serpent and the whale,
        the islands, by night the lantern with its light pooled and the dividers, the rhumb lines, the water lines,
        the engraved title and the wind heads. Drawn lighter, it leaves out only the parchment's grain, foxing and
        fold and the faintest ring of a light pool. So it is kept all year and as June's design, with the month's
        mark."""
        most, _ = contents(KEY)["most"]
        names = ("city", "map_symbol", "river", "rose", "needle", "cog", "route", "tower", "dragon", "serpent", "whale",
                 "isle", "lantern", "pool", "dividers", "rhumb_lines", "_water_lines", "engraved_title", "wind_head",
                 "_foxing", "_fold")
        texture = {"_foxing", "_fold"}
        lighter = 0
        for code in ("H1", "H2"):
            for theme in (DAY, DARK):
                for motion, held in ((True, SET), (False, SET), (True, HELD), (False, HELD)):
                    case = (code, theme["name"], motion, held.day)
                    with mock.patch.dict(BUDGET, {"header": 10**9}):
                        full, whole = served(lambda: held.header(code, most, theme, True, motion), names)
                    svg, kept = served(lambda: held.header(code, most, theme, True, motion), names)
                    self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"], case)
                    self.assertEqual("<animate" in svg, motion, case)
                    self.assertEqual(whole - kept - texture, set(), case)
                    self.assertTrue({"rose", "needle", "rhumb_lines", "_water_lines", "engraved_title"} <= kept, case)
                    self.assertIn('stroke-width=".5"', svg, (case, "the rhumb lines"))
                    if len(full.encode("utf-8")) > BUDGET["header"]:
                        lighter += 1
                        self.assertEqual(whole - kept, texture, case)
        self.assertGreaterEqual(lighter, 2, "the moving wide H1 comes out over the budget by day and by night")

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

    def test_the_elements_are_made_of_the_map(self):
        spec = E.describe("instruments", next(d for d in ELEMENTS.values() if d["kind"] == "instruments"))
        for theme in (DAY, DARK):
            svg = SET.element("instruments", spec, theme, "wide")
            for roof in (RAMP["verm"], RAMP["sea"], RAMP["blue"], RAMP["gold"]):
                self.assertTrue(any(c in svg for c in roof), (theme["name"], "the towers' roofs"))
        cert = SET.element("certificate", E.describe("certificate", ELEMENTS["conformance"]), DAY, "wide")
        self.assertIn(RAMP["verm"][5], cert, "the rose's lit points in the wax")
        card = SET.element("placard", E.describe("placard", ELEMENTS["action"]), DAY, "wide")
        self.assertIn('<pattern id="plfh"', card, "the cartouche's ruled border")

    def test_a_schematic_card_is_a_cartouche_on_the_chart(self):
        """Each card is a label on the chart: an inked rule a unit out from its edge, curling out and back at every
        corner, and its icon inked in a roundel washed in one of the map's colours."""
        spec = E.describe("schematic", next(d for d in ELEMENTS.values() if d["kind"] == "schematic"))
        cards, real = [], A.cartouche_card

        def kept(p, x, y, w, h, night, seed, ink, fill):
            cards.append((x, y, w, h))
            return real(p, x, y, w, h, night, seed, ink, fill)
        washes = {C["sea"], C["land"], RAMP["verm"][5], GOLD[5], RAMP["deep"][5], RAMP["dusk"][5], RAMP["verm"][2],
                  GOLD[2], SEA[3], RAMP["land"][3], RAMP["verm"][3], GOLD[3], RAMP["deep"][3], RAMP["dusk"][3],
                  RAMP["verm"][1], GOLD[1]}
        with mock.patch.object(A, "cartouche_card", kept):
            for variant in ("wide", "narrow"):
                for night in (False, True):
                    cards.clear()
                    p = SET.draw_element("schematic", spec, night, variant, None)
                    edge = INK[1] if not night else GOLD[2]
                    self.assertGreater(len(cards), 3, variant)
                    for (x, y, w, h) in cards:
                        for (cx, cy, sx, sy) in ((x - 1, y - 1, 1, 1), (x + w, y - 1, -1, 1), (x - 1, y + h, 1, -1),
                                                 (x + w, y + h, -1, -1)):
                            for (dx, dy) in A.CURL:
                                self.assertEqual(p.get(cx + sx * dx, cy + sy * dy), edge, (variant, night, x, y))
                        top = y + (h - 7) // 2
                        self.assertEqual(p.get(x + 3, top + 3), edge, "the roundel's rim")
                        self.assertIn(p.get(x + 4, top + 3), washes, "the roundel's wash")

    def test_a_contributor_is_a_wind_head_blowing_away_from_its_name(self):
        """A contributor is a wind head sixteen units tall, its wind blowing out to its left and its face keeping
        two units clear of its name, which the layout sets twelve right of its centre."""
        for night in (False, True):
            for i in range(5):
                p = Pix(60, 40)
                A.wind_avatar(p, 30, 20, i, night, bot=i == 4)
                xs = [x for (x, _) in p.layers["base"]]
                ys = [y for (_, y) in p.layers["base"]]
                self.assertEqual((min(xs), max(xs)), (30 - 11, 30 + 9), (night, i))
                self.assertGreaterEqual(max(ys) - min(ys) + 1, 16, (night, i))
                wind = INK[3] if not night else GOLD[3]
                self.assertEqual([p.get(x, 22) for x in range(19, 23)], [wind] * 4, (night, i, "its wind"))


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
        for family in ("red", "orange", "yellow", "green", "blue", "purple", "white", "black", "slate", "brown"):
            self.assertIsNotNone(self.badge("flat", message_hex=PALETTE[family]), family)

    def test_what_the_sets_letters_cannot_draw_is_left_to_the_kit(self):
        self.assertIsNone(self.badge("flat", message="中文"))


if __name__ == "__main__":
    unittest.main()
