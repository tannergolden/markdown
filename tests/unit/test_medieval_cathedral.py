# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Cathedral set's own rules, which the checks every set shares cannot know: what the night alone shows (the
candles' flames and their light on the stone and the glass, the gargoyles' eyes, the owl) stays out of the day's
files, and what the day alone shows (the sunbeam and its motes, the colour the windows lay on the sill) out of the
night's; every letter of a title is a pane of coloured glass in a came of lead, glowing by night; the frieze is
tracery, quatrefoils of stone glazed in two glasses whose glints twinkle only in a wide moving header, never a
string of coloured lights, and a gargoyle crouches on each top corner; every rule is a string course of stone; every
scene, the frieze, the gargoyles and the string courses keep two units from every word; every phone header stands a
scene of the set's, H2 and H3 their heroes under their words; the longest page's wide headers keep their whole scene
and their motion within the budget, a drawing made lighter thinning only texture, and every other page keeps 1.5 KB
to spare at full weight; every sprite the set lays on grounds and patterns to save bytes shows its own colours; a
schematic's wires are cames of lead and its cards leaded panels; a footer stands on its sill and ends in the
design's mark; a release keeps under what it brought; a came of lead lies along every badge's top row; a counter's
numerals hold 4.5:1 on their panes; and the roster's avatars are saints' heads, never initials. The design keeps to
its collection's hand (see `Hand`) and its composition (see `Composition`). The set is a theme, not a holiday on the
calendar, so the checks every registered set shares run here over the set directly, with the same contents and the
same entry points."""
from __future__ import annotations

import contextlib
import datetime as dt
import math
import random
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
from domain.collections.hand import MEDIEVAL as HAND, check, lab
from domain.holidays.designs import NARROW, WIDE
from domain.holidays.designs.badges import PLATE, STATES, STYLES as BADGE_STYLES, TOP, nearest
from domain.holidays.designs.banners import MARK_Y
from domain.collections.medieval_cathedral import SET
from domain.collections.medieval_cathedral import art as A
from domain.collections.medieval_cathedral.palette import C, GLAZES, NIGHT_SKY, RAMP, X
from domain.holidays.pixel import BLINKS, Pix, contrast, num
from domain.palette import PALETTE

support.install()
KEY = SET.key
HELD = SET.on(dt.date(2026, 4, 1))      # the design drawn as April's, the month's mark at the top of its headers
FLAME = frozenset(HAND.ramp("flame"))
HEADER = Header(tone="standard", holiday=KEY)
# The longest title the kit allows: two lines at the smallest size, centred, which still leave the sides free.
LONG = HEADER.with_(title="w" * 40)
LEAD = set(RAMP["lead"])


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


# A symbol drawn as another one turned to face the other way (the gargoyle's twin), a block laid in a pattern (a
# string course, the frieze), and a ground laid as one path of runs under a sprite (see `art.paint`): what
# `sprites` reads to know which cells they cover.
MIRROR = re.compile(r'<use href="#(q\d+)" transform="matrix\(-1 0 0 1 (\d+) 0\)"/>')
RECT = re.compile(r'<rect(?: x="(\d+)")?(?: y="(\d+)")? width="(\d+)" height="(\d+)" fill="([^"]+)"')
GROUND = re.compile(r'<path stroke="([^"]+)" d="([^"]+)"')
STEP = re.compile(r"([Mmhv])(-?(?:\d+\.?\d*|\.\d+))(?:\s*(-?(?:\d+\.?\d*|\.\d+)))?")
PATTERN = re.compile(r'<pattern id="([^"]+)"(?: x="(\d+)")?(?: y="(\d+)")? width="(\d+)" height="(\d+)" '
                     r'patternUnits="userSpaceOnUse">(.*?)</pattern>')
# The window the owl crosses through, clipped to the sky over the rose (see `art.glide`).
OWL = re.compile(r'<clipPath id="gl\d+">')


def runs(d: str) -> set:
    """The pixels a path of runs strokes a pixel wide, along rows (`h`) and down columns (`v`), as the canvas and
    the set write them."""
    out, x, y = set(), 0.0, 0.0
    for cmd, a, b in STEP.findall(d):
        if cmd in "Mm":
            x, y = (float(a), float(b)) if cmd == "M" else (x + float(a), y + float(b))
        elif cmd == "h":
            out.update((math.floor(x) + i, math.floor(y)) for i in range(int(a)))
            x += int(a)
        else:
            out.update((math.floor(x), math.floor(y) + i) for i in range(int(a)))
            y += int(a)
    return out


def laid(markup: str) -> list:
    """The blocks and grounds in `markup`, in the order they are drawn: (paint, cells)."""
    out = []
    for m in re.finditer(f"{RECT.pattern}|{GROUND.pattern}", markup):
        x, y, w, h, fill, stroke, d = m.groups()
        if fill:
            x0, y0 = int(x or 0), int(y or 0)
            out.append((fill, {(xx, yy) for xx in range(x0, x0 + int(w)) for yy in range(y0, y0 + int(h))}))
        else:
            out.append((stroke, runs(d)))
    return out


def covered(markup: str) -> set:
    """The cells the blocks and the grounds in `markup` cover."""
    return set().union(*(cells for _, cells in laid(markup)))


def shown(p: Pix, L="base") -> dict:
    """The colour each cell of layer `L` shows: its grounds and blocks in the order they were laid, a pattern's
    tile read where it lies, and the layer's solid pixels over them."""
    tiles = {}
    for pid, x, y, w, h, body in PATTERN.findall("".join(p.defs)):
        tile = {}
        for paint, cells in laid(body):
            if ":" not in paint:
                tile.update(dict.fromkeys(cells, paint))
        tiles[pid] = (int(x or 0), int(y or 0), int(w), int(h), tile)
    out = {}
    for paint, cells in laid("".join(p.shapes.get(L, ()))):
        if paint.startswith("url(#"):
            x0, y0, w, h, tile = tiles[paint[5:-1]]
            out.update({(x, y): tile.get(((x - x0) % w, (y - y0) % h)) for x, y in cells})
        else:
            out.update(dict.fromkeys(cells, paint))
    out.update({xy: c for xy, c in p.layers.get(L, {}).items() if ":" not in c})
    return out


def colours_at(p: Pix, cells) -> set:
    """Every colour laid at `cells`, on any layer, as a pixel or a ground."""
    out = {c for layer in p.layers.values() for xy, c in layer.items() if xy in cells}
    return out | {c for xy, c in getattr(p, "grounds", {}).items() if xy in cells}


def sprites(draw, *hooks) -> tuple:
    """`draw()`'s drawing, and every pixel of the sprites the set's `hooks` (names of its drawing hooks) put on
    it, gathered as they draw: their pixels on every layer, the cells of the symbols they place (a symbol that is
    another turned to face the other way covers that one's cells mirrored), and the cells of the blocks they lay
    in a pattern and of the grounds they lay under their sprites."""
    pixels, cells = set(), {}
    symbol = Pix.symbol

    def kept(self, key, cells_=None, shapes="", mono=False):
        sid = symbol(self, key, cells_, shapes, mono)
        if sid not in cells:
            own = set(cells_ or ()) | covered(shapes)
            for ref, w in MIRROR.findall(shapes):
                own |= {(int(w) - 1 - x, y) for x, y in cells.get(ref, ())}
            cells[sid] = own
        return sid

    def watched(hook):
        def drawn(*args, **kw):
            p = next(a for a in args if isinstance(a, Pix))
            before = {L: set(c) for L, c in p.layers.items()}
            placed = {L: len(u) for L, u in p.uses.items()}
            before_shapes = {L: len(s) for L, s in p.shapes.items()}
            out = hook(*args, **kw)
            for L, c in p.layers.items():
                pixels.update(set(c) - before.get(L, set()))
            for L, uses in p.uses.items():
                for (_, sid, x, y, s) in uses[placed.get(L, 0):]:
                    pixels.update((x + dx * s, y + dy * s) for dx, dy in cells.get(sid, ()))
            for L, shapes in p.shapes.items():
                pixels.update(covered("".join(shapes[before_shapes.get(L, 0):])))
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
    def test_what_the_night_alone_shows_stays_out_of_the_day_and_the_days_sun_out_of_the_night(self):
        for code in ("H1", "H2", "H3"):
            day = SET.header(code, HEADER, DAY, True, True)
            night = SET.header(code, HEADER, DARK, True, True)
            self.assertNotIn(RAMP["candle"][6], day, (code, "a candle's flame"))
            self.assertNotIn("flicker", str(SET.h1(HEADER, False, True).meta) if code == "H1" else "", code)
            self.assertNotRegex(day, OWL, (code, "the owl"))
            self.assertIn(RAMP["candle"][6], night, (code, "the candles burn"))
            self.assertIn(f'<path stroke="{RAMP["candle"][4]}" stroke-opacity=', night,
                          (code, "their light on the stone"))
            self.assertNotIn(X["sun"], night, (code, "the sunbeam"))
            self.assertNotIn('<g clip-path="url(#bmc)">', night, (code, "the motes"))
            self.assertNotIn('<path stroke="#C42634" stroke-opacity=', night, (code, "coloured light on the sill"))
        day, night = (SET.header("H1", HEADER, theme, True, True) for theme in (DAY, DARK))
        self.assertIn(X["sun"], day, "the sunbeam slants through the glass")
        self.assertIn('clip-path="url(#bmc)"', day, "motes drift in it")
        self.assertRegex(night, OWL, "the owl crosses")
        self.assertIn("painted", "painted")

    def test_by_night_the_candles_light_reaches_the_glass_of_the_rose_and_the_lancets(self):
        """The altar's candles lay a glow over the lower half of the rose, votive candles burn on the east window's
        sill between the saints and light their glass, and the candles beside a section's or a strip's lancet
        light its glass: a warm glow in front of the glass that flickers with the flames. By day none of it."""
        F = RAMP["candle"]
        for code, drawer in (("H1", SET.h1), ("H2", SET.h2), ("H3", SET.h3)):
            night = drawer(HEADER, True, True)
            glows = [s for L, shapes in night.shapes.items() if L.startswith("fl") for s in shapes
                     if f'fill="{F[4]}"' in s]
            self.assertTrue(glows, (code, "a glow over the glass, flickering"))
            day = drawer(HEADER, False, True)
            self.assertFalse([L for L in day.layers if L.startswith(("fl", "fb"))], (code, "no flame by day"))
        p = Pix(415, 120)
        A.east_window(p, 358, 100, True, room=78)
        flames = {xy for L, cells in p.layers.items() if L.startswith("fl") for xy, c in cells.items() if c == F[6]}
        self.assertEqual(len({x for x, _ in flames}), 3, "a votive between each pair of lancets")

    def test_the_owl_crosses_where_the_words_leave_the_rose_room_for_it(self):
        """By night the owl comes to perch on the rose wherever the words leave the rose fifty rows over the altar,
        the most a page can say among them, whose drawing made lighter to fit its budget keeps it; never by day,
        and never over a rose with less room."""
        most, _ = contents(KEY)["most"]
        for h in (most, LONG, HEADER):
            self.assertRegex(SET.header("H1", h, DARK, True, True), OWL, h.title)
            self.assertNotRegex(SET.header("H1", h, DAY, True, True), OWL, h.title)
        for room, owl in ((49, False), (50, True)):
            p = Pix(415, 140)
            A.east_end(p, 5, 130, True, room=room)
            self.assertEqual(any('<clipPath id="gl' in d for d in p.defs), owl, room)


class Day(unittest.TestCase):
    def test_the_sun_comes_down_from_the_upper_left_through_the_rose_onto_the_altar(self):
        p = SET.h1(HEADER, False, True)
        beam = p.shapes["beam"][0]
        xs = [float(v) for v in re.search(r'points="([^"]+)"', beam).group(1).split()[0::2]]
        ys = [float(v) for v in re.search(r'points="([^"]+)"', beam).group(1).split()[1::2]]
        top, foot = min(ys), max(ys)
        self.assertLess(max(x for x, y in zip(xs, ys) if y == top), max(x for x, y in zip(xs, ys) if y == foot),
                        "it slants down to the right, from the upper left")
        self.assertLess(min(xs), 31, "from the left of the rose")
        self.assertTrue(any(c == C["white"] for c in p.layers["motes"].values()), "motes caught in it")

    def test_the_lancets_lay_their_four_colours_on_the_sill(self):
        """By day the east window lays ruby, cobalt, emerald and amber side by side on its sill, a patch under
        each lancet, strong enough to read; by night it lays none."""
        p = SET.h1(HEADER, False, True)
        laid = {c.split(":")[0] for c in p.layers["pool"].values() if float(c.split(":")[1]) >= 0.6}
        for glaze in ("ruby", "cobalt", "emerald", "amber"):
            self.assertIn(A.glaze_tones(glaze, False)[1], laid, glaze)
        self.assertNotIn("pool", SET.h1(HEADER, True, True).layers)


class Phones(unittest.TestCase):
    def test_every_sprite_keeps_two_units_clear_of_every_word_on_a_phone(self):
        """On a phone the altar and its rose, the lancets, the candle, the frieze and its gargoyles, the section
        mark and the string course on the rule are built to the rows the words leave free: no pixel of theirs lies
        within two units of a word's box, for any of the shared contents, by day or by night."""
        drawers = {"H1": SET.h1_narrow, "H2": SET.h2_narrow, "H3": SET.h3_narrow}
        for name, (h, _) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    p, pixels = sprites(lambda: drawer(h, night), "scene_narrow", "scene_under", "garland",
                                        "section_mark", "rule_decor")
                    hits = off_words(p, pixels)
                    self.assertEqual(hits[:6], [], (name, code, night, len(hits)))

    def test_every_sprite_keeps_two_units_clear_of_every_word_on_a_wide_header_too(self):
        """The scenes, the frieze and its gargoyles, the marks beside a title and the string course on the rule
        keep the same two units from every word across a wide header."""
        drawers = {"H1": SET.h1, "H2": SET.h2, "H3": SET.h3}
        for name, (h, _) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    p, pixels = sprites(lambda: drawer(h, night, True), "scene", "garland", "section_mark",
                                        "strip_mark", "rule_decor")
                    hits = off_words(p, pixels)
                    self.assertEqual(hits[:6], [], (name, code, night, len(hits)))

    def test_every_phone_header_stands_a_scene_of_the_sets_by_day_and_by_night(self):
        """Every phone header, H1, H2 and H3, of every shared content stands a scene of the set's own, beside its
        words or under them, by day and by night, at a size that reads at 1x: twenty rows of it or more, of stone
        and coloured glass and a candle in brass, and by night its candles burn."""
        drawers = {"H1": SET.h1_narrow, "H2": SET.h2_narrow, "H3": SET.h3_narrow}
        stone = set(RAMP["stone"]) | set(RAMP["dusk"])
        glass = {t for g in GLAZES for night in (False, True) for t in A.glaze_tones(g, night)}
        for name, (h, _) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    what = (name, code, "night" if night else "day")
                    p, cells = sprites(lambda: drawer(h, night), "scene_narrow", "scene_under")
                    self.assertTrue(cells, (*what, "a scene"))
                    self.assertGreaterEqual(max(y for _, y in cells) - min(y for _, y in cells) + 1, 20, what)
                    painted = colours_at(p, cells)
                    self.assertTrue(painted & stone, (*what, "a sill of stone"))
                    self.assertTrue(painted & glass, (*what, "coloured glass"))
                    self.assertTrue(painted & set(RAMP["gold"]), (*what, "a candlestick of brass"))
                    self.assertEqual(RAMP["candle"][6] in painted, night, (*what, "its candles burn by night"))

    def test_a_phones_hero_stands_under_its_words_whatever_its_title(self):
        """A phone's H2 and H3 ask for rows under their words whatever their title (`phone_rows`), and their
        heroes stand in them, clear of every word and on the rule: on H2 the great window, the angel, the knight
        and the king in its three lights under its rose, and on H3 the bishop in his lancet. Nothing of either
        stands beside the words but the fleur-de-lis by a strip's title."""
        for name, (h, _) in contents(KEY).items():
            for code, drawer, who in (("H2", SET.h2_narrow, ["angel", "knight", "king"]),
                                      ("H3", SET.h3_narrow, ["bishop"])):
                for night in (False, True):
                    what = (name, code, night)
                    with mock.patch.object(type(SET), "phone_rows", lambda self, design, title_w: 0):
                        plain = drawer(h, night)
                    saints = []
                    with mock.patch.object(A, "saint", lambda p, x, y, figure, *a, **k: saints.append(figure)):
                        drawn, under = sprites(lambda: drawer(h, night), "scene_under")
                    self.assertEqual(drawn.h - plain.h, SET.UNDER[code], (*what, "the rows it asked for"))
                    self.assertTrue(under, (*what, "a hero under the words"))
                    self.assertEqual(saints, who, what)
                    self.assertEqual(off_words(drawn, under), [], what)
                    rule = max(y for _, y in under) + 2
                    self.assertEqual(drawn.get(20, rule), SET.ink(night)["rule"], (*what, "it stands on the rule"))
                    _, beside = sprites(lambda: drawer(h, night), "scene_narrow")
                    self.assertLessEqual(len(beside), 0 if code == "H2" else 15 * 15, what)

    def test_the_scenes_stand_where_the_words_leave_them_room(self):
        """The kit's own lines leave each phone its scene; the least a page can say leaves the altar its rose; and
        the altar, which cannot fit beside the most a page can say, is left out rather than built over a word."""
        h, _ = contents(KEY)["kit"]
        for code in ("H1", "H2", "H3"):
            svg = SET.header(code, h, DAY, False, False)
            self.assertIn(RAMP["gold"][3], svg, (code, "a brass candlestick"))
        least, _ = contents(KEY)["least"]
        p, pixels = sprites(lambda: SET.h1_narrow(least, False), "scene_narrow")
        self.assertIn(RAMP["ruby"][3], {p.get(*xy) for xy in pixels}, "the rose's ruby petals")
        most, _ = contents(KEY)["most"]
        p, pixels = sprites(lambda: SET.h1_narrow(most, False), "scene_narrow")
        self.assertEqual(off_words(p, pixels), [])


class Titles(unittest.TestCase):
    def test_every_letter_is_a_pane_of_glass_in_a_came_of_lead(self):
        p = Pix(200, 40)
        w = A.glass_title(p, 4, 4, "ABCD", False, 4)
        self.assertEqual(w, Pix.measure("ABCD", "57", 4))
        line = "".join(p.shapes["base="])
        self.assertTrue(line.startswith('<g transform="translate(4 4) scale(4)">'), "the line set once, at its size")
        cames = re.search(f'<g stroke="{RAMP["lead"][0]}">(.*?)</g>', line).group(1)
        self.assertEqual(cames.count("<use "), 4, "a came round each of four letters, under them")
        for i, glaze in enumerate(GLAZES):
            self.assertIn(f'<g stroke="{A.glaze_tones(glaze, False)[1]}"><use ', line,
                          (i, glaze, "a letter of each glass by turns"))
        # A letter that comes again and again on its line is placed once with its came: the came in lead inside
        # one symbol, the glass taking the colour of its group.
        q = Pix(200, 40)
        A.glass_title(q, 4, 4, "WWWWWW", True, 2)
        both = q.syms[("glass", "W", RAMP["lead"][1])]
        self.assertIn(f'<g id="{both}"><use href="#{q.syms[("came", "57", "W")]}" stroke="{RAMP["lead"][1]}"/>'
                      f'<use href="#{q.syms[("glyph", "57", "W")]}"/></g>', q.defs)
        self.assertEqual("".join(q.shapes["base="]).count(f'<use href="#{both}"'), 6)
        day = SET.header("H1", HEADER, DAY, True, True)
        self.assertIn(f'<g stroke="{RAMP["lead"][0]}">', day, "the cames")
        self.assertNotIn("stroke-opacity", day.split("<defs>")[0].split("<desc")[0], "no glow by day")
        night = SET.header("H1", HEADER, DARK, True, True)
        for glaze in GLAZES:
            thin = A.glaze_tones(glaze, True)[2]
            self.assertIn(f'<g stroke="{thin}" stroke-opacity=".22">', night, (glaze, "its glow"))

    def test_the_glass_is_rimmed_and_streaked_by_its_finish(self):
        p = Pix(60, 40)
        A.glass_title(p, 4, 4, "I", False, 4)
        top = p.layers["base~"]
        dark, body, thin = A.glaze_tones("ruby", False)
        self.assertIn(dark, top.values(), "a dark rim where the glass meets the lead")
        self.assertIn(thin, top.values(), "a streak where the glass runs thin")
        q = Pix(60, 40)
        A.glass_title(q, 4, 4, "I", False, 2)
        self.assertNotIn(dark, q.layers.get("base~", {}).values(), "no rim on a stroke two pixels wide")

    def test_the_roundels_twinkle_only_in_a_wide_moving_header(self):
        moving = SET.header("H1", HEADER, DAY, True, True)
        self.assertEqual(moving.count('dur="1.5s"'), 3, "three phases of twinkling")
        for still in (SET.header("H1", HEADER, DAY, True, False), SET.header("H1", HEADER, DAY, False, False)):
            self.assertNotIn("<animate", still)
            self.assertIn(RAMP["ruby"][3], still, "the roundels still sit in the frieze")


class Frame(unittest.TestCase):
    def test_the_frieze_is_tracery_of_stone_and_two_glasses_never_a_string_of_lights(self):
        """A header's top is a band of stone hung from the coping, a quatrefoil in each bay glazed in cobalt round
        a roundel of ruby: whole bays between the gargoyles, laid out from the top centre with a bay under the
        month's mark, the same bay over and over, in the stone's tones and two glasses and lead, and a glint on
        each roundel."""
        art = {c for row in A.FRIEZE for c in row}
        self.assertLessEqual(art, set("0123456gGqLr*"), "stone, cobalt, lead and ruby only")
        for night in (False, True):
            S = A.stone_ramp(night)
            tones = set(S) | set(A.glaze_tones("cobalt", night)) | set(A.glaze_tones("ruby", night)) | set(RAMP["lead"])
            for w in (415, 180):
                p = Pix(w, 40)
                A.frieze(p, night)
                x0, n = A.bay_layout(w)
                (x, y, width, height, fill), = RECT.findall("".join(p.shapes["frieze"]))
                self.assertEqual((int(width), int(height), int(y)), (n * A.BAY, len(A.FRIEZE), A.FRIEZE_TOP),
                                 (night, w))
                self.assertEqual(int(x), x0, "whole bays from the top centre")
                self.assertGreaterEqual(x0, A.GW, "clear of the gargoyle on the left")
                self.assertLessEqual(x0 + n * A.BAY, w - A.GW, "and of the one on the right")
                self.assertEqual(x0 + n // 2 * A.BAY + A.BAY // 2, w // 2, "a bay under the month's mark")
                (pid, px, py, pw, ph, body), = [t for t in PATTERN.findall("".join(p.defs)) if f"url(#{t[0]})" == fill]
                self.assertEqual((int(px), int(py), int(pw), int(ph)), (int(x), A.FRIEZE_TOP, A.BAY, len(A.FRIEZE)),
                                 "the same bay over and over, from the band's first column")
                self.assertEqual(covered(body), {(i, j) for i in range(A.BAY) for j in range(len(A.FRIEZE))})
                self.assertLessEqual({c for c, _ in laid(body)}, tones, (night, "of stone and the two glasses"))
                glints = [xy for L, cells in p.layers.items() if L.startswith("tw") for xy in cells]
                self.assertEqual(len(glints), n, "a glint on each roundel")

    def test_a_gargoyle_crouches_on_each_top_corner_and_its_eyes_glow_by_night(self):
        for code in ("H1", "H2", "H3"):
            for wide in (True, False):
                for theme in (DAY, DARK):
                    svg = SET.header(code, HEADER, theme, wide, True)
                    w = 415 if wide else 180
                    self.assertIn(f'transform="matrix(-1 0 0 1 {A.GW} 0)"', svg, (code, wide, "the twin"))
                    self.assertIn(f'x="{w - A.GW}" y="0"', svg, (code, wide, "on the right corner"))
                    eye = RAMP["candle"][6] in svg
                    self.assertEqual(eye, theme is DARK, (code, wide, theme["name"], "eyes that glow by night"))
        p = Pix(415, 30)
        A.gargoyles(p, True)
        lit = {xy for L, cells in p.layers.items() if L.startswith("fl") for xy, c in cells.items()
               if c == RAMP["candle"][6]}
        self.assertEqual(lit, {A.EYE, (414 - A.EYE[0], A.EYE[1])})

    def test_the_gargoyles_keep_inside_the_corners_no_word_ever_reaches(self):
        """Wherever a gargoyle reaches past its twelfth column it keeps above row 14, and its corbel, feet and tail
        keep inside that column down to row 22, so no title, dimension or note any layout sets near either corner
        comes near it."""
        for j, row in enumerate(A.GARGOYLE):
            for i, ch in enumerate(row):
                if ch != ".":
                    self.assertTrue(j <= 13 or i <= 12 and j <= 22, (i, j))

    def test_every_rule_is_a_string_course_of_stone(self):
        """A header's rule and a sheet's are carved as a string course, three rows of stone standing on the rule
        with a quatrefoil cut in every six columns, and nothing of glass lies along them."""
        p = SET.h1(HEADER, False, True)
        rects = [tuple(int(v or 0) for v in r[:4]) for r in RECT.findall("".join(p.shapes["course"]))]
        feet = {y + h - 1 for _, y, _, h in rects}
        self.assertEqual(len(feet), 1, "every block of it stands on the one rule")
        rule = feet.pop()
        self.assertTrue(any(p.get(x, rule) == SET.ink(False)["rule"] for x in range(4, 411)), "on the rule's row")
        self.assertGreater(sum(w for _, _, w, h in rects if h == 3), 150, "the course runs along the rule")
        glass = {t for g in GLAZES for t in A.glaze_tones(g, False)}
        rows = range(rule - 3, rule + 3)
        self.assertFalse({c for (x, y), c in p.layers["base"].items() if y in rows and 70 < x < 340} & glass)
        sheet = SET.element("milestones", E.describe("milestones", ELEMENTS["history"]), DAY, "wide")
        self.assertIn('fill="url(#sc18)"', sheet, "the sheet's rule too")


class Badges(unittest.TestCase):
    def test_a_came_of_lead_lies_along_every_badges_top_row_with_the_letters_under_it(self):
        for style in BADGE_STYLES:
            drawn = [SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                       SET.badge_states()["green"])]
            drawn += [SET.plate_badge(style, "License", "MIT", "scale", mode) for mode in ("day", "night")]
            for p in drawn:
                rows = {c for (x, y), c in p.layers["base"].items() if y == 0}
                self.assertTrue(rows and rows <= LEAD, (style, rows - LEAD))
                self.assertTrue(all(y >= TOP for _, _, _, y, _ in p.uses["base"]), "the letters sit under the came")

    def test_a_counters_numerals_hold_4_5_on_their_panes(self):
        for night in (False, True):
            q = Pix(20, 20)
            SET.counter_cell(q, 2, 2, night)
            face = q.layers["base"][(7, 8)]
            self.assertGreaterEqual(contrast(SET.counter_ink(night, False), face), 4.5, night)
            self.assertGreaterEqual(contrast(SET.counter_ink(night, True), face), 2.0, night)


class Elements(unittest.TestCase):
    def test_an_avatar_is_a_saints_head_in_glass_never_initials(self):
        for night in (False, True):
            p = Pix(40, 40)
            with mock.patch.object(Pix, "text", side_effect=AssertionError("initials lettered")) as lettered:
                SET.avatar(p, 10, 20, 0, {"initials": "AB", "name": "A B"}, night)
                SET.avatar(p, 28, 20, 1, {"name": "a bot"}, night)
            self.assertEqual(lettered.call_count, 0)
            painted = set(p.layers["base"].values())
            self.assertIn(RAMP["gold"][4 + (1 if night else 0)], painted, "a gold halo")
            self.assertIn(RAMP["flesh"][4], painted, "a face in glass")

    def test_the_sill_the_window_the_candle_and_the_links_are_the_sets(self):
        """Every footer stands on the sill's string course; F1's notes end with a small lancet of ruby glass and a
        candle in its sconce, burning by night with its light on the glass; F2's scale is a rule of lead and
        glass, lit from inside by night."""
        _, f = contents(KEY)["kit"]
        for theme in (DAY, DARK):
            night = theme is DARK
            for code in ("F1", "F2"):
                for wide in (True, False):
                    svg = SET.footer(code, f, theme, wide, False)
                    self.assertRegex(svg, r'<pattern id="frs\d+"', (code, theme["name"], wide, "the sill's course"))
            for wide in (True, False):
                f1 = SET.footer("F1", f, theme, wide, False)
                self.assertIn(RAMP["grisaille"][5 if night else 6], f1, (wide, "the candle in its sconce"))
                self.assertIn(A.glaze_tones("ruby", night)[1], f1, (wide, "the window's ruby"))
                self.assertEqual(RAMP["candle"][6] in f1, night, (wide, "burning by night"))
            f2 = SET.footer("F2", f, theme, True, False)
            self.assertIn(A.glaze_tones("cobalt", night)[1], f2, "the scale's glass, lit by night")
            for i in range(4):
                svg = SET.link(f"Link {i}", theme, i)
                self.assertLess(len(svg.encode("utf-8")), 2500, (i, "a link under 2.5 KB"))
                self.assertIn(RAMP["ruby"][3], svg, "the icon's pane of ruby")

    def test_a_schematics_wires_are_cames_of_lead_and_its_cards_leaded_panels(self):
        """A wire is lead from end to end, its shaded side along it and solder where it bends, with no glass on
        it; a card is a panel in a came of lead, its icon leaded in white into a pane of coloured glass."""
        glass = {t for g in ("ruby", "cobalt", "emerald", "amber", "violet") for n in (False, True)
                 for t in A.glaze_tones(g, n)}
        spec = E.describe("schematic", ELEMENTS["how-it-runs"])
        for night in (False, True):
            wires = []
            came = SET.wire_lights

            def kept(p, cells, night_, seed):
                wires.append(list(cells))
                came(p, cells, night_, seed)
            with mock.patch.object(SET, "wire_lights", kept):
                p = SET.schematic(spec, night)
            lead = set(RAMP["lead"])
            self.assertTrue(wires)
            for cells in wires:
                for (x, y, _) in cells:
                    for q in ((x, y), (x + 1, y), (x, y + 1)):
                        self.assertNotIn(p.get(*q), glass, (night, q))
                bends = [(x, y) for x, y, d in cells if (x, y, "h" if d == "v" else "v") in cells]
                for x, y in bends:
                    self.assertIn(p.get(x - 1, y), {RAMP["lead"][6]}, (night, "solder lit at a bend"))
            panes = [c for (x, y), c in p.layers["base"].items() if c in glass]
            self.assertTrue(panes, "the cards' panes of coloured glass")
            self.assertLessEqual({p.get(x, y) for x, y in ((16, 40),)} - {None}, lead | glass | {None})

    def test_a_release_keeps_under_what_it_brought(self):
        """The roundels on the timeline's came keep clear of the notes the sheet sets over each release."""
        spec = E.describe("milestones", ELEMENTS["history"])
        for night in (False, True):
            p, pixels = sprites(lambda: SET.milestones(spec, night), "release", "today_mark")
            self.assertEqual(off_words(p, pixels, margin=1), [], night)


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
            for glaze in GLAZES:
                for ground in grounds:
                    self.assertGreaterEqual(contrast(A.glaze_tones(glaze, night)[1], ground), 3.0,
                                            (night, glaze, ground))

    def test_ordinary_content_fits_at_full_weight_with_its_motion_and_room_to_spare(self):
        """Every content but the most a page can say is served at full weight and moving, with at least 1.5 KB
        under the budget to spare."""
        for name, (h, _) in contents(KEY).items():
            if name == "most":
                continue
            for code, draw in (("H1", SET.h1), ("H2", SET.h2), ("H3", SET.h3)):
                for theme in (DAY, DARK):
                    full = draw(h, theme is DARK, True)
                    self.assertFalse(full.lite)
                    svg = full.svg(h.spoken_title(), h.spoken(), stamp=SET.stamp(f"{code} {theme['name']}"))
                    self.assertEqual(SET.header(code, h, theme, True, True), svg, (name, code, "at full weight"))
                    self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"] - 1500, (name, code, theme["name"]))

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


class Lighter(unittest.TestCase):
    """The longest pages: what a drawing made lighter keeps, and the bytes the set saves without losing a pixel."""
    PIECES = ("rose_window", "owl", "altar", "altar_light", "candlestick", "votive", "flame", "lancet", "saint",
              "knight_tall", "sill", "sunbeam", "glass_glow", "candlelight", "frieze", "gargoyles", "glass_title",
              "great_window", "arch_frame", "quatrefoil_light", "title_glint")

    def test_the_longest_pages_wide_headers_keep_their_whole_scene_and_their_motion_within_the_budget(self):
        """The most a page can say, every field at its longest, on the wide H1 and H2, by day and by night, drawn as the
        kit draws them: each comes within the budget, still moves, and holds every piece of the scene its full drawing
        holds, the rose and the east window's lancets with their saints on H1 and the great window on H2, its three
        saints under its rose, the light falling through them, the frieze and its gargoyles, the candles and their
        flames, the owl, the title's glass, its glow and the gleam that crosses it. Only texture thins: the glints on
        the rose's petals, the faintest ring of each pool of light, the window's faintest cast and half the stars."""
        most, _ = contents(KEY)["most"]
        for code, draw in (("H1", SET.h1), ("H2", SET.h2)):
            for theme in (DAY, DARK):
                night, what = theme is DARK, (code, theme["name"])
                served = SET.header(code, most, theme, True, True)
                self.assertLessEqual(len(served.encode("utf-8")), BUDGET["header"], what)
                self.assertIn("<animate", served, (*what, "it still moves"))
                drawings = {}
                for lite in (False, True):
                    calls: Counter = Counter()

                    def spy(name, real):
                        def counted(*args, **kw):
                            calls[name] += 1
                            return real(*args, **kw)
                        return counted
                    with mock.patch.object(SET, "_lite", lite), \
                            mock.patch.multiple(A, **{n: spy(n, getattr(A, n)) for n in self.PIECES}):
                        p = draw(most, night, True)
                    svg = p.svg(most.spoken_title(), most.spoken(), stamp=SET.stamp(f"{code} {theme['name']}"))
                    drawings[lite] = (p, calls, svg)
                p, calls, _ = next(d for d in drawings.values() if d[2] == served)
                self.assertEqual(calls, drawings[False][1], (*what, "every piece of the full drawing"))
                # Served at full weight or not, the lighter drawing holds every piece and only thins.
                self.assertEqual(drawings[True][1], drawings[False][1], (*what, "the lighter drawing's pieces"))
                self.assertLessEqual(len(drawings[True][2]), len(drawings[False][2]), (*what, "lighter is lighter"))
                if code == "H1":
                    self.assertEqual(calls["saint"], 4, (*what, "the king, the bishop, the knight and the angel"))
                    self.assertEqual(calls["rose_window"], 2, (*what, "the great rose and the east window's"))
                    self.assertEqual(calls["owl" if night else "sunbeam"], 1, what)
                    self.assertGreaterEqual(calls["votive"], 3, what)
                else:
                    self.assertEqual(calls["great_window"], 1, (*what, "the great window"))
                    self.assertEqual(calls["saint"], 3, (*what, "the angel, the knight and the king"))
                    self.assertEqual(calls["rose_window"], 1, (*what, "its rose"))
                self.assertGreaterEqual(calls["title_glint"], 1, (*what, "the gleam across the title"))
                self.assertGreaterEqual(calls["candlestick"], 2, what)
                self.assertEqual(calls["candlelight"], int(night), (*what, "the candles' light on the stone"))
                self.assertTrue(p.layers.get("base~"), (*what, "the glass of the title, its rims and streaks"))
                self.assertEqual(bool(p.shapes.get("haze=")), night, (*what, "the glow of its letters by night"))

    def test_every_sprite_laid_on_grounds_shows_its_own_colours(self):
        """Every sprite the set paints in few bytes (`art.paint`), its roses, its lancets and their saints, laid
        on grounds of their lead, their dark glass or their patterns of quarries and canopies, shows at every one
        of its pixels the colour it was drawn in, by day and by night, wide and on a phone."""
        checked = []
        real = A.paint

        def checking(p, colours, plans=(), L="base"):
            real(p, colours, plans, L)
            now = shown(p, L)
            checked.append((len(colours), sorted(xy for xy, c in colours.items() if now.get(xy) != c)[:4]))
        with mock.patch.object(A, "paint", checking):
            for theme in (DAY, DARK):
                for code in ("H1", "H2", "H3"):
                    for h in (HEADER, contents(KEY)["most"][0]):
                        SET.header(code, h, theme, True, True)
                        SET.header(code, h, theme, False, False)
        self.assertGreater(len(checked), 50)
        for n, wrong in checked:
            self.assertEqual(wrong, [], n)
        rnd = random.Random(5)
        for _ in range(40):
            cells = {(rnd.randrange(30), rnd.randrange(20)): rnd.choice(GLAZES) for _ in range(rnd.randrange(1, 200))}
            colours = {xy: RAMP[g][rnd.randrange(7)] for xy, g in cells.items()}
            p = Pix(40, 30)
            A.paint(p, colours, [[(c, list(colours))] for c in set(colours.values())])
            now = shown(p)
            self.assertEqual({xy: now.get(xy) for xy in colours}, colours)


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
        families = {"red": PALETTE["red"], "orange": PALETTE["orange"], "yellow": PALETTE["yellow"],
                    "green": PALETTE["green"], "blue": PALETTE["blue"], "purple": PALETTE["purple"],
                    "white": PALETTE["white"], "dark": PALETTE["black"], "grey": PALETTE["slate"],
                    "brown": PALETTE["brown"]}
        taken = {family: nearest(hexc, swatches) for family, hexc in families.items()}
        self.assertEqual(len(set(taken.values())), len(taken), ("each family its own glass", taken))

    def test_what_the_sets_letters_cannot_draw_is_left_to_the_kit(self):
        self.assertIsNone(self.badge("flat", message="中文"))



class Hand(unittest.TestCase):
    """The collection's hand, which the design keeps to drawn as April's design and kept all year."""

    def test_check_finds_nothing_as_the_months_design_or_kept_all_year(self):
        self.assertEqual(check(HELD), [])
        self.assertEqual(check(SET), [])

    def test_its_words_are_in_the_hands_inks(self):
        for night in (False, True):
            k = SET.ink(night)
            self.assertEqual((k["body"], k["muted"]), (HAND.body[night], HAND.muted[night]), night)

    def test_its_grounds_fall_in_the_hands_bands(self):
        """The grisaille quarries by day, warm as stone in the sun, with the lead between them and every cast
        from one quarry to the next; and every band of the candlelit glass by night."""
        day = [C["paper"], C["came"], X["tint_sky"], X["tint_warm"], X["tint_cool"]]
        for night, grounds in ((False, day), (True, NIGHT_SKY + [C["paper_n"]])):
            lo, hi, most = HAND.night_ground if night else HAND.day_ground
            for ground in grounds:
                light, chroma, hue = lab(ground)
                self.assertTrue(lo <= light <= hi and chroma <= most, (night, ground, light, chroma))
                self.assertTrue(night or chroma >= 6 or 40 <= hue <= 110, (ground, "warm, never a cold white"))

    def test_every_flame_burns_on_the_hands_flame_ramp(self):
        """The candles' flames, their glows, the light they lay on the stone and the glass, and the gargoyles'
        eyes, in every header and footer by night, are tones of the hand's flame; and so is the flame of a still
        candle, which lies on the drawing itself."""
        self.assertEqual(RAMP["candle"], HAND.ramp("flame"))
        burning = 0
        for name, (h, f) in contents(KEY).items():
            for p in (HELD.h1(h, True, True), HELD.h2(h, True, True), HELD.h3(h, True, True), HELD.h1_narrow(h, True),
                      HELD.h2_narrow(h, True), HELD.h3_narrow(h, True), HELD.f1(f, True), HELD.f2(f, True),
                      HELD.f1_narrow(f, True), HELD.f2_narrow(f, True)):
                lit = {c.split(":")[0] for n in p.layers if n.startswith(("fl", "fb")) for c in p.layers[n].values()}
                lit |= {c for n in p.shapes if n.startswith(("fl", "fb"))
                        for c in re.findall(r'(?:fill|stroke)="(#[0-9A-F]{6})"', "".join(p.shapes[n]))}
                burning += bool(lit)
                self.assertLessEqual(lit, FLAME, name)
        self.assertGreater(burning, 30, "the candles flicker in every moving header")
        p = Pix(20, 30)
        A.candlestick(p, 10, 28, True, flicker=False)
        own = set(RAMP["gold"] + RAMP["grisaille"] + RAMP["lead"])
        flame = {c.split(":")[0] for c in p.layers["base"].values()} - own
        self.assertTrue(flame)
        self.assertLessEqual(flame, FLAME)

    def test_it_moves_on_the_hands_times(self):
        """In a moving header the gleam crosses the title's glass every twelve seconds, the hand's period; the
        flames flicker and the roundels and stars twinkle on the engine's cadences; the motes drift across the
        shaft of sun in half a minute, as slow as the hand's ambient sweeps; and the owl's crossing comes round
        in four to eight seconds, its wings beating as it flies."""
        h, _ = contents(KEY)["repository"]
        cadences = {num(v[2]) for v in BLINKS.values()}
        for code in ("H1", "H2", "H3"):
            for theme in (DAY, DARK):
                what = (code, theme["name"])
                svg = HELD.header(code, h, theme, True, True)
                glints = re.findall(r'<animateTransform attributeName="transform" type="translate" values="0;[^"]+" '
                                    r'keyTimes="0;.4;1" dur="([.\d]+)s"', svg)
                self.assertEqual(glints, [num(HAND.glint)], what)
                for dur in re.findall(r'<animate attributeName="opacity" [^>]*?dur="([.\d]+)s"', svg):
                    self.assertTrue(dur in cadences or dur == num(2 * 0.4), (*what, dur))
                for dur in re.findall(r'<animateTransform [^>]*?dur="([.\d]+)s"', svg):
                    self.assertTrue(float(dur) == HAND.glint or 4 <= float(dur) <= 8 or 24 <= float(dur) <= 48,
                                    (*what, dur))
        day, night = (HELD.header("H1", h, theme, True, True) for theme in (DAY, DARK))
        drifts = [float(d) for d in re.findall(r'<animateTransform [^>]*?dur="([.\d]+)s"', day)]
        self.assertTrue([d for d in drifts if 24 <= d <= 48], "the motes drift slowly")
        crossing = re.findall(r'<animateTransform attributeName="transform" type="translate" values="[^"]+" '
                              r'dur="([.\d]+)s" repeatCount="indefinite" calcMode="discrete"/>', night)
        self.assertTrue(crossing and all(4 <= float(d) <= 8 for d in crossing), "the owl's crossing")

    def test_every_scene_keeps_clear_of_the_months_mark(self):
        """No scene comes within two units of the box the month's mark takes at the top centre, in any header,
        wide or on a phone, with the mark or without it."""
        T = type(SET)
        for name, (h, _) in contents(KEY).items():
            for held in (HELD, SET):
                for draw, hooks in ((lambda d: d.h1(h, False, False), ("scene",)),
                                    (lambda d: d.h2(h, False, False), ("scene",)),
                                    (lambda d: d.h3(h, False, False), ("scene",)),
                                    (lambda d: d.h1_narrow(h, False), ("scene_narrow",)),
                                    (lambda d: d.h2_narrow(h, False), ("scene_narrow", "scene_under")),
                                    (lambda d: d.h3_narrow(h, False), ("scene_narrow", "scene_under"))):
                    p = draw(held)
                    with contextlib.ExitStack() as stack:
                        for hook in hooks:
                            stack.enter_context(mock.patch.object(T, hook, lambda *a, **k: []))
                        bare = draw(held)
                    n = HAND.mark_size
                    x0, y0 = p.w // 2 - n // 2 - 2, MARK_Y - n // 2 - 2
                    for layer, cells in p.layers.items():
                        for (x, y), c in cells.items():
                            if x0 <= x < x0 + n + 4 and y0 <= y < y0 + n + 4 and not layer.startswith("mark"):
                                self.assertEqual(bare.layers.get(layer, {}).get((x, y)), c, (name, layer, x, y))

    def test_the_mark_cuts_no_quatrefoil_of_the_frieze(self):
        """The month's mark, a roundel at the top centre, covers the middle bay's quatrefoil whole and leaves every
        other bay's whole, wide and on a phone: no quatrefoil is cut at its edge."""
        glass = {(i, j) for j, row in enumerate(A.FRIEZE) for i, ch in enumerate(row) if ch in "gGqLr*"}
        for w in (WIDE, NARROW):
            x0, n = A.bay_layout(w)
            for b in range(n):
                under = {math.hypot(x0 + b * A.BAY + i + 0.5 - w / 2, A.FRIEZE_TOP + j + 0.5 - MARK_Y)
                         <= HAND.mark_size / 2 + 0.5 for i, j in glass}
                self.assertEqual(len(under), 1, (w, b, "whole, under the mark or clear of it"))
                self.assertEqual(under.pop(), b == n // 2, (w, b))


class Composition(unittest.TestCase):
    """The composition the collection's hand asks of every design: a title page's scenes rising seven tenths of
    their band on both sides, a section's hero four fifths of it, a strip's its full height, a phone's standing
    forty rows, a phone's title page a full scene under its words, and a footer ending in the design's mark.
    Measured as the design is kept all year: the month's mark moves no scene (see `Hand`)."""
    ORDINARY = ("kit", "repository", "profile")

    @staticmethod
    def rows(cells) -> int:
        ys = [y for _, y in cells]
        return max(ys) - min(ys) + 1

    def test_a_title_pages_scenes_rise_seven_tenths_of_their_band_on_both_sides(self):
        """On a wide H1 the altar under its rose on the left and the east window's lancets on the right each rise
        from the rule at least seven tenths of the way to the frieze."""
        for name in self.ORDINARY:
            h, _ = contents(KEY)[name]
            p, cells = sprites(lambda: SET.h1(h, False, False), "scene")
            rule = max(y for _, y in cells) + 2
            for side in ([xy for xy in cells if xy[0] < 60], [xy for xy in cells if xy[0] > 340]):
                self.assertGreaterEqual(rule - min(y for _, y in side), 0.7 * (rule - 16), name)

    def test_a_sections_hero_rises_four_fifths_of_its_band(self):
        """The great window, at the right of a wide section, rises from its rule at least four fifths of the way
        to the frieze, and is ninety units across with its candles."""
        for name in self.ORDINARY:
            h, _ = contents(KEY)[name]
            for night in (False, True):
                p, cells = sprites(lambda: SET.h2(h, night, False), "scene")
                rule = max(y for _, y in cells) + 2
                xs = [x for x, _ in cells]
                self.assertGreaterEqual(rule - min(y for _, y in cells), 0.8 * (rule - 16), (name, night))
                self.assertGreaterEqual(max(xs) - min(xs) + 1, 89, (name, night))
                self.assertGreaterEqual(min(xs), 300, (name, night, "on the right"))

    def test_a_strips_hero_rises_its_full_height(self):
        """The bishop's lancet at the right of a wide strip rises from its sill to the frieze, sixty rows and
        more wherever the strip allows."""
        for name in self.ORDINARY:
            h, _ = contents(KEY)[name]
            p, cells = sprites(lambda: SET.h3(h, False, False), "scene")
            rule = max(y for _, y in cells) + 2
            self.assertLessEqual(min(y for _, y in cells), 20, name)
            self.assertGreaterEqual(self.rows(cells), min(60, rule - 20), name)

    def test_a_phones_hero_stands_forty_rows_and_its_title_page_a_full_scene(self):
        """A phone's great window and its bishop's lancet, under their words, each stand forty rows or more; and a
        phone's H1 stands the east end under its words, the full width of the sheet and forty-eight rows tall."""
        for name, (h, _) in contents(KEY).items():
            for draw in (lambda: SET.h2_narrow(h, False), lambda: SET.h3_narrow(h, False)):
                p, cells = sprites(draw, "scene_under")
                self.assertGreaterEqual(self.rows(cells), 40, name)
        self.assertGreaterEqual(SET.phone_scene_rows, 48)
        for name in self.ORDINARY:
            h, _ = contents(KEY)[name]
            p, cells = sprites(lambda: SET.h1_narrow(h, False), "scene_narrow")
            xs = [x for x, _ in cells]
            self.assertGreaterEqual(self.rows(cells), 48, name)
            self.assertGreaterEqual(max(xs) - min(xs) + 1, 160, (name, "the full width"))

    def test_a_footer_ends_in_the_designs_mark_on_its_floor_of_stone(self):
        """Every footer stands on its step over the sill, the string course along its foot; a wide F1 ends in the
        design's mark at the right end after the way back up, the rose between its lancets and a candle at each
        end, wherever its cells leave the room, and keeps the small window and its sconce in the notes' corner
        where it has notes; a wide F2 stands the knight's lancet in its scale's cell, and a phone's F2 the rose
        between its scale and the way back up."""
        marks: list = []

        def spy(name, real):
            def drawn(p, *a, **k):
                span = real(p, *a, **k)
                marks.append((name, p.w, span))
                return span
            return drawn
        named = ("footer_east", "footer_knight", "footer_rose", "footer_mark")
        for name, (_, ft) in contents(KEY).items():
            for night in (False, True):
                for code, draw in (("F1", SET.f1), ("F2", SET.f2), ("F1n", SET.f1_narrow), ("F2n", SET.f2_narrow)):
                    marks.clear()
                    with mock.patch.multiple(A, **{n: spy(n, getattr(A, n)) for n in named}):
                        p = draw(ft, night)
                    what = (name, code, night)
                    ledge = p.h - A.FOOT
                    self.assertIn(f'<rect x="0" y="{ledge + 1}" width="{p.w}" height="3" fill="url(#frs{ledge + 1})"/>',
                                  "".join(p.shapes["base"]), (*what, "the string course along the foot"))
                    kinds = [m[0] for m in marks]
                    end = max(b[2] for b in p.words)
                    if code == "F1":
                        self.assertEqual("footer_mark" in kinds, bool(ft.get("closing")), (*what, "the notes' corner"))
                        if end <= SET.EAST[1]:
                            (_, _, (x0, x1)), = [m for m in marks if m[0] == "footer_east"]
                            self.assertGreaterEqual(x0, end + 4, what)
                            self.assertLessEqual(x1, WIDE - 6, what)
                            self.assertGreaterEqual(x1 - x0, 55, (*what, "large enough to read"))
                        else:
                            self.assertNotIn("footer_east", kinds, what)
                    elif code == "F2":
                        (_, _, (x0, x1)), = [m for m in marks if m[0] == "footer_knight"]
                        self.assertTrue(78 <= x0 and x1 <= 94, (*what, "in the scale's cell"))
                    elif code == "F2n":
                        (_, _, (x0, x1)), = [m for m in marks if m[0] == "footer_rose"]
                        self.assertTrue(72 <= x0 and x1 <= 108, (*what, "between the scale and the way back up"))
                    elif ft.get("closing"):
                        self.assertEqual(kinds, ["footer_mark"], what)


if __name__ == "__main__":
    unittest.main()
