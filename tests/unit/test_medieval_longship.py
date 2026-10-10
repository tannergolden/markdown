# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Longship set's own rules, which the checks every set shares cannot know: it keeps to the medieval hand, as
January's design and kept all year, its words in the hand's inks, its ground in the hand's bands, its fires on the
hand's flame, its moon the hand's, its people on the hand's skins and canon and its motion on the hand's time; the
shields along the gunwale pause for the month's mark at the top centre, ending whole on either side of it, and no
scene reaches into its columns; its heroes stand to the collection's measure, a phone's H1 on a fjord across the
rows under its words and a phone's H2 and H3 on their heroes under theirs, and a footer stands on the fjord's
water with the longship sailing at its right end where the words leave her room. What the night alone shows (the
fires, the lantern, the lit window, the moon, the aurora and its green on the water and the snow, and the bronze
inlay) stays out of the day's files, and what the day alone shows (the sun and the gulls) out of the night's; a
title is chip-carved into the oak by day, its strokes cut to a lit face and a dark one, and inlaid with bronze by
night; the ship rides the swell and the aurora drifts and shimmers only in a wide moving header, stepping a pixel
at a time without writing out every step; every sprite and every shape a scene fills keeps clear of the words; the
longest page's wide headers keep their whole scene and their motion within the budget, a drawing made lighter
thinning only texture, while ordinary pages keep their headroom at full weight with the month's mark; the border is
a carved plait with a prow beast at each top corner of a header; the H2's dragon ship hangs a lantern that burns by
night; the histogram's bars are stacked shields, the busiest bossed in bronze; a placard is a runestone with a
serpent painted round it; a header stands on the strake; a plank's lit edge and nails lie along every badge's top;
a link is a small file; and a counter's numerals hold 4.5:1 on their planks. The set is a theme, not a holiday on
the calendar, so the checks every registered set shares run here over the set directly, with the same contents
and the same entry points."""
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
from domain.collections.hand import MEDIEVAL, check, lab
from domain.elements import draw as E
from domain.holidays.designs.badges import PLATE, STATES, STYLES as BADGE_STYLES, TOP, inside
from domain.collections.medieval_longship import SET
from domain.collections.medieval_longship import art as A
from domain.collections.medieval_longship.palette import C, NIGHT_SKY, RAMP, X
from domain.holidays.pixel import Pix, contrast
from domain.palette import PALETTE

support.install()
KEY = SET.key
HEADER = Header(tone="standard", holiday=KEY)
OAK, TAR, IRON, BRONZE, FLAME = RAMP["oak"], RAMP["tar"], RAMP["iron"], RAMP["bronze"], RAMP["flame"]
MOON = MEDIEVAL.ramp("moon")
BOB = 'values="0 0;0 0;0 -1;0 -1;0 -2;0 -2;0 -1;0 -1;0 0;0 0;0 1;0 1"'
HEADROOM = 1500     # what an ordinary page's every file keeps under its budget at full weight
HELD = SET.on(dt.date(2026, 1, 1))     # the Longship drawn as January's design, with the month's mark
# A run of the gunwale's shields, laid in their pattern: its x, its width, and how far it is shifted along.
GUNWALE = re.compile(r'<rect x="(-?\d+)" y="5" width="(\d+)" height="9" fill="url\(#gw\)"'
                     r'(?: transform="translate\((\d+)\)")?/>')


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
    on it, gathered as they draw: their pixels on every layer, the cells of the symbols they place, and the
    cells of the regions they fill (which the set keeps in the drawing's `filled`)."""
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
            mock.patch.multiple(SET, **{name: watched(getattr(SET, name)) for name in hooks}):
        p = draw()
    return p, pixels


# Every piece of the set's art a hook draws with, by name: the functions of its `art` module.
ART = sorted(n for n, f in vars(A).items()
             if callable(f) and n[0].islower() and getattr(f, "__module__", "") == A.__name__)


def served(draw) -> tuple:
    """`draw()`'s file, the drawing it was written from (the last one, when the kit drew it again lighter), and
    how many times each piece of the set's art (see ART) was drawn on that drawing. A wall of the fjord too low
    to stand draws nothing and is not counted."""
    made, write = [], Pix.svg

    def written(self, *args, **kw):
        out = write(self, *args, **kw)
        made.append((self, out))
        return out

    def watched(name, piece):
        def drawn(*args, **kw):
            out = piece(*args, **kw)
            p = next((a for a in args if isinstance(a, Pix)), None)
            if p is not None and (out or name != "fjord_wall"):
                p.__dict__.setdefault("pieces", Counter())[name] += 1
            return out
        return drawn
    with mock.patch.object(Pix, "svg", written), \
            mock.patch.multiple(A, **{name: watched(name, getattr(A, name)) for name in ART}):
        svg = draw()
    p = next(q for q, out in made if out == svg)
    return svg, p, getattr(p, "pieces", Counter())


def full_weight(draw) -> tuple:
    """`draw()`'s file, and whether the kit served it at full weight: no drawing of it was made lighter."""
    lite, canvas = [], type(SET).canvas
    with mock.patch.object(type(SET), "canvas", lambda self, w, h: lite.append(self._lite) or canvas(self, w, h)):
        svg = draw()
    return svg, not any(lite)


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


class Hand(unittest.TestCase):
    """The Longship in the medieval collection's hand (see `collections.hand`)."""

    def test_it_keeps_to_its_hand_as_januarys_design_and_kept_all_year(self):
        self.assertEqual(check(HELD), [])
        self.assertEqual(check(SET), [])

    def test_its_words_are_in_the_hands_inks(self):
        for night in (False, True):
            k = SET.ink(night)
            self.assertEqual((k["body"], k["muted"]), (MEDIEVAL.body[night], MEDIEVAL.muted[night]), night)

    def test_its_ground_falls_in_the_hands_bands(self):
        """By day the weathered oak behind the words falls in the hand's day band; by night every band of the tarred
        planks falls in its night band."""
        lo, hi, most = MEDIEVAL.day_ground
        light, chroma, hue = lab(C["paper"])
        self.assertTrue(lo <= light <= hi and chroma <= most, (light, chroma))
        self.assertTrue(chroma >= 6 or 40 <= hue <= 110, (chroma, hue))
        lo, hi, most = MEDIEVAL.night_ground
        for c in NIGHT_SKY:
            light, chroma, _ = lab(c)
            self.assertTrue(lo <= light <= hi and chroma <= most, (c, light, chroma))

    def test_its_fires_burn_on_the_hands_flame_and_its_moon_is_the_hands(self):
        """Every fire (the brazier, the lit window, the lantern on the stem and the beacon) burns on the hand's flame,
        every colour a flickering light lays by night a tone of that ramp; and the moon and its path are drawn on the
        hand's moon ramp."""
        self.assertEqual(FLAME, MEDIEVAL.ramp("flame"))
        flame = set(FLAME)
        for name in ("kit", "most"):
            h, _ = contents(KEY)[name]
            for draw in (SET.h1, SET.h2, SET.h3):
                p = draw(h, True, True)
                lit = [n for n in p.layers if n.startswith(("fl", "fb"))]
                fire = {c.split(":")[0] for n in lit for c in p.layers[n].values()}
                fire |= set(re.findall(r'fill="(#[0-9A-F]{6})"', "".join(shape for n in lit for shape in p.shapes[n])))
                self.assertTrue(fire, (name, draw.__name__))
                self.assertLessEqual(fire, flame, (name, draw.__name__))
        q = Pix(40, 40)
        A.moon(q, 20, 20, 5)
        A.moonpath(q, 20, 34, False)
        self.assertLessEqual({c.split(":")[0] for c in q.layers["base"].values()}, set(MOON))

    def test_its_people_wear_the_hands_skins_and_stand_to_its_canon(self):
        """The lookout stands 24 units from the crown of his helm to his boots, his head about a fifth of that, a
        single dark unit for his eye and his face and hands on one of the hand's skins; the steersman and the
        warriors of the roster have the hand's skins too; and no outline anywhere is black."""
        skins = {c for k in ("skin0", "skin1", "skin2") for c in MEDIEVAL.ramp(k)}
        rows = [j for j, row in enumerate(A.WATCHMAN) if "H" in row or "g" in row]
        self.assertTrue(24 <= max(rows) - min(rows) + 1 <= 28, (min(rows), max(rows)))
        head = [j for j, row in enumerate(A.WATCHMAN) if set(row) & set("Hhbnef")]
        self.assertTrue(4 <= len(head) <= 6, head)
        self.assertEqual(sum(row.count("e") for row in A.WATCHMAN), 1, "a single dark unit for an eye")
        for night in (False, True):
            q = Pix(30, 40)
            A.lookout(q, 2, 36, night)
            face = {q.get(2 + i, 36 - len(A.WATCHMAN) + j) for j, row in enumerate(A.WATCHMAN)
                    for i, ch in enumerate(row) if ch in "fFa"}
            self.assertLessEqual(face, skins, night)
            q = Pix(20, 20)
            A.steersman(q, 2, 15, night)
            self.assertTrue({c for c in q.layers["base"].values()} & skins, night)
            for i in range(3):
                q = Pix(20, 20)
                A.warrior(q, 10, 10, i, night)
                self.assertTrue({c for c in q.layers["base"].values()} & set(MEDIEVAL.ramp(f"skin{i}")), (night, i))
        for name, code, fn, svg in every_banner():
            self.assertNotIn("#000000", svg.upper(), (name, fn))

    def test_it_moves_in_the_hands_time(self):
        """The fires flicker and the stars, the bosses and the inlay twinkle on the engine's cadences; the ships ride
        the swell and the smoke rises in loops of four to eight seconds, the gulls wheel in eight; and the aurora
        drifts across the sheet in a slow sweep of 24 to 48 seconds."""
        night = HELD.header("H1", HEADER, DARK, True, True)
        self.assertIn('dur="1.8s"', night, "the fires flicker")
        self.assertIn('dur="1.5s"', night, "the stars and the inlay twinkle")
        self.assertTrue(4 <= A.SMOKE_LOOP <= 8)
        self.assertIn(f'dur="{A.SMOKE_LOOP:g}s"', night, "the smoke rises")
        self.assertIn('dur="4.2s"', night, "the longship rides the swell")
        self.assertIn('dur="4.6s"', HELD.header("H2", HEADER, DARK, True, True), "the dragon ship rides the swell")
        self.assertIn('dur="8s"', HELD.header("H1", HEADER, DAY, True, True), "the gulls wheel")
        drift = re.findall(r'type="translate" values="0 0;[^"]*" dur="([\d.]+)s"', night)
        self.assertTrue(drift)
        self.assertTrue(24 <= max(float(d) for d in drift) <= 48, drift)

    def test_its_top_centre_is_kept_for_the_months_mark(self):
        """As January's design, on every header, wide and on a phone, the shields along the gunwale pause for the
        month's mark: a run of them ends with a whole shield on either side of the mark's box and the two units round
        it, as far from its middle on the one side as on the other, and the rail runs on behind the mark; and so for
        a sign the page chose. Kept all year, with no mark, the shields run unbroken. No scene reaches into those
        columns over the mark's foot."""
        n = MEDIEVAL.mark_size
        for name in ("kit", "least", "most"):
            h, _ = contents(KEY)[name]
            for code in ("H1", "H2", "H3"):
                for wide in (True, False):
                    for held in (HELD, SET, SET.signed("leo")):
                        draw = getattr(held, code.lower() if wide else f"{code.lower()}_narrow")
                        args = (h, False, True) if wide else (h, False)
                        p, pixels = sprites(lambda: draw(*args), "scene", "scene_narrow", "scene_under")
                        what = (name, code, wide, held.day, held.sign)
                        lo, hi = SET.top_centre(p)
                        self.assertEqual((lo, hi), (p.w // 2 - n // 2 - 2, p.w // 2 - n // 2 + n + 2))
                        runs = [(int(x) + int(d or 0), int(x) + int(d or 0) + int(w))
                                for x, w, d in GUNWALE.findall("".join(p.shapes["base"]))]
                        foot = 10 + n // 2 + 3
                        self.assertFalse([(x, y) for x, y in pixels if lo <= x < hi and y < foot], what)
                        if held is SET:
                            self.assertEqual(len(runs), 1, what)
                            continue
                        (a0, a1), (b0, b1) = runs
                        self.assertTrue(a1 <= lo and b0 >= hi, (what, runs))
                        self.assertEqual((a1 - 3 - 31) % 7, 0, (what, "the left run ends on a shield's last column"))
                        self.assertEqual(p.w // 2 - a1, b0 - p.w // 2, (what, "as far from the middle each side"))
                        self.assertIsNotNone(p.get(a1, 10), (what, "its last column drawn whole"))
                        box = (p.w // 2 - n // 2, p.w // 2 - n // 2 + n)
                        self.assertTrue(all(p.get(x, 5) for x in [*range(a1, box[0]), *range(box[1], b0)]),
                                        (what, "the rail runs on behind the mark"))

    def test_its_scenes_are_drawn_to_the_collections_measure(self):
        """A wide H2's dragon ship rises the band's height over a third of the sheet at its right, and a wide H3's
        lookout the strip's; a phone's H1 stands its fjord across the rows under its words at least 48 rows tall,
        and a phone's H2 and H3 their heroes under their words at least 40 rows tall, none beside them."""
        for name in ("kit", "repository", "least"):
            h, _ = contents(KEY)[name]
            p, px = sprites(lambda: SET.h2(h, False, True), "scene")
            hero = [(x, y) for x, y in px if x > p.w // 2]
            rule = max(y for _, y in hero) + 1
            self.assertGreaterEqual(rule - min(y for _, y in hero), 0.8 * (rule - 14), name)
            span = (max(x for x, _ in hero) - min(x for x, _ in hero) + 1) / p.w
            self.assertTrue(0.35 <= span <= 0.48, (name, span))
            p, px = sprites(lambda: SET.h3(h, False, True), "scene")
            rule = max(y for _, y in px) + 1
            self.assertLessEqual(min(y for _, y in px), 17, name)
            self.assertGreaterEqual(rule - min(y for _, y in px), 0.9 * (rule - 14), name)
        self.assertGreaterEqual(SET.phone_scene_rows, 48)
        for name in ("kit", "profile", "least", "most"):
            h, _ = contents(KEY)[name]
            p, px = sprites(lambda: SET.h1_narrow(h, False), "scene_narrow")
            walls = [y for x, y in px if x < 40 or x > 140]
            self.assertGreaterEqual(max(walls) - min(walls) + 1, 48, name)
            self.assertGreaterEqual(max(x for x, _ in px) - min(x for x, _ in px), 165, name)
            for code, draw in (("H2", SET.h2_narrow), ("H3", SET.h3_narrow)):
                _, beside = sprites(lambda: draw(h, False), "scene_narrow")
                p, under = sprites(lambda: draw(h, False), "scene_under")
                ys = [y for _, y in under]
                self.assertEqual(beside, set(), (name, code))
                self.assertGreaterEqual(max(ys) - min(ys) + 1, 40, (name, code))

    def test_its_footer_stands_on_the_water_with_the_ship_at_its_right_end(self):
        """Every footer stands on the fjord's water, along its whole foot; where it has no closing notes, the
        longship, its mark, sails at its right end after the way back up."""
        for name in ("kit", "profile", "repository", "least", "most"):
            _, f = contents(KEY)[name]
            for night in (False, True):
                surface = RAMP["deep" if night else "sea"]
                for draw in (SET.f1, SET.f2, SET.f1_narrow, SET.f2_narrow):
                    p = draw(f, night)
                    self.assertLessEqual({p.get(x, p.h - 1) for x in range(p.w)}, set(surface), (name, draw.__name__))
                    self.assertNotIn("frs", "".join(p.defs), (name, draw.__name__, "no strake"))
                if name in ("profile", "repository", "least"):
                    p = SET.f1(f, night)
                    kind, x0 = p.marked_at
                    self.assertEqual(kind, "ship", (name, night))
                    self.assertGreater(x0, max(b[2] for b in p.words), (name, night))


class Night(unittest.TestCase):
    def test_what_the_night_alone_shows_stays_out_of_the_day_and_the_days_sun_and_gulls_out_of_the_night(self):
        for code in ("H1", "H2", "H3"):
            day = SET.header(code, HEADER, DAY, True, True)
            night = SET.header(code, HEADER, DARK, True, True)
            self.assertNotIn(FLAME[6], day, (code, "a flame"))
            self.assertNotIn(MOON[0], day, (code, "the moon"))
            self.assertNotIn('id="auc"', day, (code, "the aurora"))
            self.assertNotIn("painlay", day, (code, "the bronze inlay"))
            self.assertNotIn(X["snow_night"], day, (code, "the aurora's green on the snow"))
            self.assertIn(FLAME[6], night, (code, "the brazier, the lantern or the beacon burns"))
            self.assertIn('id="auc"', night, (code, "the aurora"))
            self.assertIn("painlay", night, code)
            self.assertNotIn(X["sun"], night, (code, "the sun"))
            self.assertNotIn('dur="1.1s"', night, (code, "a gull's wingbeat"))
        day, night = (SET.header("H1", HEADER, theme, True, True) for theme in (DAY, DARK))
        self.assertIn(X["sun"], day, "the sun")
        self.assertIn('dur="1.1s"', day, "the gulls wheel")
        self.assertIn(MOON[0], night, "the moon")
        self.assertIn(MOON[4], night, "and its path on the water")

    def test_a_phones_scene_under_its_words_keeps_the_nights_lights_out_of_the_day(self):
        h, _ = contents(KEY)["profile"]
        for code in ("H2", "H3"):
            day, night = (SET.header(code, h, theme, False, False) for theme in (DAY, DARK))
            self.assertNotIn(FLAME[6], day, (code, "the lantern and the beacon are cold by day"))
            self.assertNotIn(MOON[0], day, (code, "the moon"))
            self.assertNotIn(X["snow_night"], day, (code, "the aurora's green on the snow"))
            self.assertIn(FLAME[6], night, (code, "and burn by night"))
            self.assertIn(X["snow_night"], night, code)
        self.assertIn(MOON[0], SET.header("H2", h, DARK, False, False), "the moon over her hull")

    def test_the_night_lights_the_footer_and_the_window(self):
        f = contents(KEY)["kit"][1]
        self.assertIn(FLAME[6], SET.footer("F1", f, DARK, True, False), "the brazier burns at the notes' corner")
        self.assertNotIn(FLAME[6], SET.footer("F1", f, DAY, True, False))
        self.assertIn(FLAME[6], SET.footer("F1", f, DARK, False, False))
        self.assertIn(FLAME[3], SET.header("H1", HEADER, DARK, True, True), "the longhouse window is lit")


class Phones(unittest.TestCase):
    def test_every_sprite_keeps_two_units_clear_of_every_word_on_a_phone(self):
        """On a phone the ship, the shore, the bow, the raven, the shields and the section mark are built to
        the rows the words leave free: no pixel of theirs lies within two units of a word's box, for any of the
        shared contents, by day or by night."""
        drawers = {"H1": SET.h1_narrow, "H2": SET.h2_narrow, "H3": SET.h3_narrow}
        for name, (h, _) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    p, pixels = sprites(lambda: drawer(h, night), "scene_narrow", "scene_under", "garland",
                                        "section_mark")
                    hits = off_words(p, pixels)
                    self.assertEqual(hits[:6], [], (name, code, night, len(hits)))

    def test_every_phone_header_of_every_content_carries_a_scene_by_day_and_by_night(self):
        """Every phone header the set draws for the shared contents, H1, H2 and H3, by day and by night, carries a
        scene of its own: the fjord's water, and on it a ship, a shore or a raven, some hundreds of pixels at the
        least, beside the words or under them."""
        drawers = {"H1": SET.h1_narrow, "H2": SET.h2_narrow, "H3": SET.h3_narrow}
        for name, (h, _) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    p, pixels = sprites(lambda: drawer(h, night), "scene_narrow", "scene_under")
                    self.assertGreater(len(pixels), 150, (name, code, night))
                    surface = RAMP["deep" if night else "sea"][4]
                    self.assertIn(surface, {p.layers["base"].get(xy) for xy in pixels}, (name, code, night, "water"))

    def test_a_phones_h2_and_h3_ask_for_their_heroes_rows_under_their_words(self):
        """A phone's H2 and H3 are laid out with PHONE_ROWS under their words, more than the kit's own layout, and
        stand their scene there; a phone's H1 leaves at least 48 rows under its last words for its fjord."""
        for name, (h, _) in contents(KEY).items():
            for code, drawer in (("H2", SET.h2_narrow), ("H3", SET.h3_narrow)):
                with mock.patch.object(type(SET), "phone_rows", lambda self, design, title_w: 0):
                    kit = drawer(h, False).h
                p, under = sprites(lambda: drawer(h, False), "scene_under")
                self.assertEqual(p.h - kit, SET.PHONE_ROWS[code], (name, code))
                self.assertTrue(under, (name, code))
            p, px = sprites(lambda: SET.h1_narrow(h, False), "scene_narrow")
            foot = max(y for _, y in px)
            self.assertGreaterEqual(foot - max(b[3] for b in p.words if b[3] <= foot), 48, name)

    def test_every_sprite_keeps_two_units_clear_of_every_word_on_a_wide_header_too(self):
        """The scenes, the shields, the marks beside a title and the rivets on the rules keep the same two
        units from every word across a wide header."""
        drawers = {"H1": SET.h1, "H2": SET.h2, "H3": SET.h3}
        for name, (h, _) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    p, pixels = sprites(lambda: drawer(h, night, True), "scene", "garland", "section_mark",
                                        "strip_mark", "rule_decor")
                    hits = off_words(p, pixels)
                    self.assertEqual(hits[:6], [], (name, code, night, len(hits)))

    def test_a_phones_fjord_holds_the_ship_under_sail_and_the_shore_with_its_longhouse(self):
        """The kit's own lines leave each phone its scene on the water; a phone's H1 holds the longship under her
        striped sail and the shore with its longhouse, whatever the page says, built clear of every word."""
        h, _ = contents(KEY)["kit"]
        for code in ("H1", "H2", "H3"):
            self.assertIn(RAMP["sea"][4], SET.header(code, h, DAY, False, False), (code, "the water"))
        for name in ("least", "most"):
            page, _ = contents(KEY)[name]
            svg = SET.header("H1", page, DAY, False, False)
            self.assertIn('<pattern id="sl"', svg, (name, "the sail flies, red and cream"))
            self.assertIn('<pattern id="lht"', svg, (name, "the longhouse's turf"))
            p, pixels = sprites(lambda: SET.h1_narrow(page, False), "scene_narrow")
            self.assertEqual(off_words(p, pixels), [], name)


class Titles(unittest.TestCase):
    def test_a_title_is_carved_and_painted_red_ochre_by_day_and_inlaid_with_bronze_by_night(self):
        day = SET.header("H1", HEADER, DAY, True, True)
        self.assertIn(f'<g stroke="{OAK[6]}">', day, "the cut's edge catching the light along the upper edges")
        self.assertIn(f'<g stroke="{OAK[1]}">', day, "the cut's dark lower face")
        self.assertIn(f'<g stroke="{X["shade_ink"]}" stroke-opacity=".35">', day, "the shadow the letters throw")
        self.assertIn(f'<g stroke="{RAMP["red"][2]}">', day, "the letters, painted red ochre")
        self.assertIn(f'<g stroke="{RAMP["red"][4]}">', day, "each stroke's face turned to the light")
        self.assertNotIn('fill="#FFB13A"', day, "no firelight by day")
        night = SET.header("H1", HEADER, DARK, True, True)
        self.assertIn('id="painlay4n"', night, "bronze inlay, a band a row of the face")
        self.assertIn(f'<g stroke="{TAR[5]}">', night, "the cut's face by night")
        self.assertIn(f'fill="{FLAME[4]}"', night, "the firelight's glow behind the title")
        self.assertNotIn(f'<g stroke="{RAMP["red"][4]}">', night, "the inlay is not faceted")

    def test_the_ship_rides_the_swell_and_the_aurora_drifts_only_in_a_wide_moving_header(self):
        moving = SET.header("H1", HEADER, DARK, True, True)
        self.assertIn(BOB, moving, "the ship bobs")
        self.assertIn('<g clip-path="url(#auc)"><g><g><g id="aug">', moving, "the aurora drifts")
        self.assertIn('<use href="#aug" x="-408"/>', moving, "shown again a window to the left, so it loops")
        steps = re.findall(r'type="translate" values="([^"]*)"', moving)
        self.assertTrue(all(len(v.split(";")) <= 40 for v in steps), "a step a pixel, never every step written")
        self.assertIn("0 0;1 0;2 0", moving, "a pixel at a time")
        self.assertIn('values="1;.7;1;.55;.9"', moving, "the rays shimmer")
        still = SET.header("H1", HEADER, DARK, True, False)
        self.assertNotIn("<animate", still)
        self.assertIn(f'stroke="{RAMP["aurora"][4]}" stroke-opacity=', still, "the aurora still lies across the sky")
        for narrow in (SET.header("H1", HEADER, DARK, False, False), SET.header("H1", HEADER, DAY, False, False)):
            self.assertNotIn("<animate", narrow)
        self.assertIn(RAMP["red"][3], SET.header("H1", HEADER, DAY, False, False), "the sail still flies")

    def test_the_aurora_hangs_three_curtains_and_greens_the_water_and_the_snow(self):
        night = SET.header("H1", HEADER, DARK, True, True)
        for b in range(3):
            self.assertIn(f'<path id="au{b}"', night, ("a band", b))
        self.assertGreaterEqual(night.count('<pattern id="aur'), 6, "the rays, many short and a few long")
        self.assertIn(RAMP["violet"][4], night, "a violet fringe")
        self.assertIn(f'stroke="{RAMP["aurora"][4]}" stroke-opacity=".24"', night, "its green on the water")
        self.assertIn(X["snow_night"], night, "and on the snow of the fells")

    def test_the_border_is_a_carved_plait_with_a_prow_beast_at_each_top_corner(self):
        for code in ("H1", "H2", "H3"):
            for wide in (True, False):
                svg = SET.header(code, HEADER, DAY, wide, False)
                self.assertIn('<pattern id="frh"', svg, "one tile of the plait, along the top")
                self.assertIn('fill="url(#frh)" transform="matrix(0 1 1 0 0 0)"', svg, "and turned down the sides")
                self.assertEqual(svg.count('transform="matrix(-1 0 0 1'), 1, (code, wide, "the right beast faces left"))
        f = contents(KEY)["kit"][1]
        self.assertNotIn("matrix(-1", SET.footer("F1", f, DAY, True, False), "a footer has iron bosses instead")

    def test_the_hero_ship_sails_under_her_striped_sail_with_oars_wake_and_spray(self):
        moving = SET.header("H1", HEADER, DAY, True, True)
        self.assertIn('<pattern id="sl"', moving, "the striped sail")
        self.assertIn(RAMP["sea"][6], moving, "foam at her bow and in her wake")
        self.assertIn('<pattern id="lht"', moving, "the longhouse's turf")
        self.assertIn('<pattern id="gw"', moving, "the shields along the gunwale, one tile")

    def test_the_section_ship_hangs_a_lantern_that_burns_by_night(self):
        """The H2's hero, the dragon ship's bow, hangs a lantern from her stem: horn panes by day, burning by night."""
        h, _ = contents(KEY)["kit"]
        night, day = SET.header("H2", h, DARK, True, False), SET.header("H2", h, DAY, True, False)
        self.assertIn(FLAME[6], night, "the lantern burns")
        self.assertNotIn(FLAME[6], day, "and is cold by day")
        self.assertIn(RAMP["ochre"][1], day, "its horn panes")


class Footers(unittest.TestCase):
    def test_a_header_and_an_element_stand_on_the_strake_and_a_footer_on_the_water(self):
        f = contents(KEY)["kit"][1]
        for code in ("F1", "F2"):
            for wide in (True, False):
                svg = SET.footer(code, f, DAY, wide, False)
                self.assertNotIn('<pattern id="frs"', svg, (code, wide))
                self.assertIn(RAMP["sea"][4], svg, (code, wide, "the water's surface"))
        self.assertIn('<pattern id="frs" width="8" height="4"', SET.header("H1", HEADER, DAY, True, True))
        self.assertIn('<pattern id="frs" width="8" height="4"',
                      SET.element("roster", E.describe("roster", ELEMENTS["contributors"]), DAY, "wide"))

    def test_a_brazier_stands_at_the_corner_of_the_notes(self):
        f = contents(KEY)["kit"][1]
        for wide in (True, False):
            self.assertIn(IRON[5], SET.footer("F1", f, DAY, wide, False), "the brazier's iron by day")

    def test_a_link_is_a_small_file_with_a_bold_icon(self):
        for i, label in enumerate(("Issues", "Pull Requests", "Releases", "Actions")):
            for theme in (DAY, DARK):
                svg = SET.link(label, theme, i)
                self.assertLess(len(svg.encode("utf-8")), 2500, (label, theme["name"]))
                self.assertIn(IRON[6 if theme is DAY else 5], svg, "the rivets")


class Badges(unittest.TestCase):
    def test_a_planks_lit_edge_and_its_nails_lie_along_every_badges_top_with_the_letters_under(self):
        for style in BADGE_STYLES:
            drawn = [SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                       SET.badge_states()["green"])]
            drawn += [SET.plate_badge(style, "License", "MIT", "scale", mode) for mode in ("day", "night")]
            for p in drawn:
                ends = [x for x in range(p.w) if inside(x, 0, p.w, p.h, BADGE_STYLES[style]["corner"])
                        and inside(x, 1, p.w, p.h, BADGE_STYLES[style]["corner"])]
                self.assertEqual(p.get(ends[0], 0), IRON[6], (style, "a nail at the left end"))
                self.assertEqual(p.get(ends[-1], 0), IRON[6], (style, "and at the right"))
                self.assertTrue(all(y >= TOP for _, _, _, y, _ in p.uses["base"]), "the letters sit under the edge")

    def test_a_counters_numerals_hold_4_5_on_their_planks(self):
        for night in (False, True):
            q = Pix(20, 20)
            SET.counter_cell(q, 2, 2, night)
            face = q.layers["base"][(7, 8)]
            self.assertGreaterEqual(contrast(SET.counter_ink(night, False), face), 4.5, night)
            self.assertGreaterEqual(contrast(SET.counter_ink(night, True), face), 2.0, night)


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

    def test_ordinary_content_is_drawn_at_full_weight_with_room_to_spare(self):
        """The kit's own lines, the samples (the profile also with a motto and a note, the heaviest of its
        kind), and the least a page can say are served at full weight as January's design, with the month's mark,
        a wide moving header with its motion, and every file keeps HEADROOM under its budget; only the stress
        contents are ever served lighter."""
        ordinary = {name: contents(KEY)[name] for name in ("kit", "repository", "profile", "least")}
        h, f = ordinary["profile"]
        ordinary["noted"] = (h.with_(motto="Built to be rebuilt.", notes=("All times in EST.",)), f)
        for name, (h, f) in ordinary.items():
            for theme in (DAY, DARK):
                for code in ("H1", "H2", "H3"):
                    for wide, motion in ((True, True), (True, False), (False, False)):
                        what = (name, code, theme["name"], wide, motion)
                        svg, full = full_weight(lambda: HELD.header(code, h, theme, wide, motion))
                        self.assertTrue(full, what)
                        self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"] - HEADROOM, what)
                        self.assertEqual("<animate" in svg, wide and motion, what)
                for code in ("F1", "F2"):
                    for wide in (True, False):
                        svg, full = full_weight(lambda: HELD.footer(code, f, theme, wide, False))
                        self.assertTrue(full, (name, code, theme["name"], wide))
                        self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["footer"] - HEADROOM, (name, code))

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

    def test_a_character_the_sets_letters_lack_hands_a_badge_back(self):
        self.assertFalse(SET.can_letter("flat", "中文"))


class Lighter(unittest.TestCase):
    """The longest page a header can say, every field at its longest, keeps its whole scene and its motion
    within the budget: a drawing made lighter to fit thins only texture (the planks' grain, faint stars, the
    outer rings of a light, small repeated ornament), never a figure, a building, a beast, a prop, a light or
    the title's treatment, and never the motion."""
    # What each wide header holds that a reader can name, and how many of each: the scene, by day and night...
    SCENE = {"H1": {"hero_ship": 1, "steersman": 1, "hang": 6, "sea": 2, "fjord_wall": 2, "strand": 1, "longhouse": 1,
                    "raven": 1, "brazier": 1},
             "H2": {"prow_hero": 1, "stem": 1, "sea": 1, "fjord_wall": 1, "section_mark": 1},
             "H3": {"crag": 1, "beacon": 1, "lookout": 1, "figure": 1, "sea": 1, "fjord_wall": 1}}
    # ...the sheet round it and the title's two lines, carved and lettered...
    SHEET = {"frame": 1, "prow_head": 2, "gunwale": 1, "carve": 2, "letters": 2}
    # ...and what only the night shows, or only the day.
    NIGHT = {"H1": ("aurora", "stars", "moon", "moonpath", "lamp", "glimmer", "firelight", "northlight", "glints",
                    "glow"),
             "H2": ("aurora", "stars", "moon", "lamp", "glimmer", "firelight", "northlight", "glints", "glow"),
             "H3": ("aurora", "stars", "lamp", "glimmer", "firelight", "northlight", "glints", "glow")}
    DAY = {"H1": ("sun", "birds"), "H2": ("birds",), "H3": ("birds",)}

    def test_the_longest_pages_wide_headers_keep_their_whole_scene_and_their_motion_within_the_budget(self):
        """As January's design, with the month's mark."""
        h, _ = contents(KEY)["most"]
        for code in ("H1", "H2", "H3"):
            for theme in (DAY, DARK):
                for motion in (True, False):
                    what = (code, theme["name"], "moving" if motion else "still")
                    with mock.patch.dict(BUDGET, {"header": 10 ** 9}):
                        _, _, whole = served(lambda: HELD.header(code, h, theme, True, motion))
                    svg, p, kept = served(lambda: HELD.header(code, h, theme, True, motion))
                    self.assertEqual(lint(svg, budget=BUDGET["header"], tokens=SET.tokens), [], what)
                    self.assertEqual(set(kept), set(whole), (what, "every piece the full drawing holds"))
                    for piece, n in {**self.SCENE[code], **self.SHEET}.items():
                        self.assertEqual((kept[piece], whole[piece]), (n, n), (what, piece))
                    for piece in (self.NIGHT if theme is DARK else self.DAY)[code]:
                        self.assertTrue(kept[piece], (what, piece))
                    if not motion:
                        self.assertNotIn("<animate", svg, what)
                        continue
                    if code != "H3":
                        self.assertIn(BOB, svg, (what, "the ship rides the swell"))
                    self.assertIn('values="1;.28;1"', svg, (what, "glints twinkle"))
                    if code == "H1":
                        self.assertIn('keyTimes="0;.33;.67"', svg, (what, "the smoke rises"))
                    if theme is DARK:
                        self.assertIn('<g clip-path="url(#auc)"><g><g><g id="aug">', svg, (what, "the aurora drifts"))
                        self.assertIn('values="1;.7;1;.55;.9"', svg, (what, "and shimmers"))
                        self.assertIn('values="1;.62;.94;.5;1;.8"', svg, (what, "the fires flicker"))
                    else:
                        self.assertIn('dur="1.1s"', svg, (what, "the gulls wheel"))

    def test_a_drawing_made_lighter_thins_the_texture_and_keeps_the_rest(self):
        """Made lighter, the night's longest H1 lets the planks' grain, most faint stars, the outer rings of each
        light and some of the rivets and glints go, and keeps every layer that moves."""
        h, _ = contents(KEY)["most"]
        with mock.patch.dict(BUDGET, {"header": 10 ** 9}):
            _, whole, _ = served(lambda: HELD.header("H1", h, DARK, True, True))
        svg, lighter, _ = served(lambda: HELD.header("H1", h, DARK, True, True))
        self.assertTrue(lighter.lite, "the longest night's H1 is served lighter")
        self.assertNotIn(X["grain_night"], svg, "the planks' grain")
        self.assertLess(len(lighter.layers["haze"]) + sum(len(lighter.layers.get(f"tb{i}", ())) for i in range(3)),
                        len(whole.layers["haze"]) + sum(len(whole.layers.get(f"tb{i}", ())) for i in range(3)),
                        "fewer faint stars")
        moving = {a[0] for a in (m[2] for m in whole.meta.values()) if a}
        self.assertEqual({a[0] for a in (m[2] for m in lighter.meta.values()) if a}, moving, "every kind of motion")
        self.assertEqual(len(whole.raws), len(lighter.raws), "the aurora's drift")


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

    def test_a_placard_is_a_runestone_with_a_serpent_painted_round_it(self):
        for theme, paint in ((DAY, RAMP["red"][3]), (DARK, RAMP["red"][2])):
            svg = SET.element("placard", E.describe("placard", ELEMENTS["action"]), theme, "wide")
            self.assertIn(BRONZE[5], svg, "the serpent's eye and the hammer pendant")
            self.assertIn(paint, svg, "the serpent painted red ochre")
            self.assertNotIn(C["paper"], svg, "no planks: the words are cut into granite")
            self.assertNotIn('<rect x="0" y="0" width="202"', svg, "the stone is not a plain rectangle")
            self.assertIn('<pattern id="rsa"', svg, "lichen and grain on its face")

    def test_the_histogram_stacks_shields_and_bosses_the_busiest_in_bronze(self):
        spec = E.describe("instruments", next(d for d in ELEMENTS.values() if d["kind"] == "instruments"))
        for theme in (DAY, DARK):
            svg = SET.element("instruments", spec, theme, "wide")
            for paint in ("red", "ochre", "cream"):
                self.assertTrue(any(c in svg for c in RAMP[paint]), (theme["name"], paint))
            self.assertIn(BRONZE[6 if theme is DAY else 5], svg, "the busiest week's bronze boss")


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
