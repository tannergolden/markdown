# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The hand a collection is drawn in: every collection has one, and its inks hold 4.5:1 against both ends of its
bands; the medieval hand's mark draws the twelve signs, each its own and within its box; a design drawn as its
month's design carries the mark at the top centre of every header, clear of every word, while a design kept all
year and a holiday's set carry none; and `check` names how a design breaks its hand."""
from __future__ import annotations

import datetime as dt
import unittest

from tests.unit.test_holiday_sets import contents

from domain import collections as C
from domain import holidays as H
from domain.canvas import DARK, DAY
from domain.collections import zodiac
from domain.collections.hand import HANDS, MEDIEVAL, CollectionSet, check, lab, signs
from domain.holidays.designs.banners import MARK_Y
from domain.holidays.pixel import Pix
from domain.holidays.pixel.shade import luminance

# The design the stand-ins are made around, and a day that makes it its month's design.
KEY = "medieval-forge"
ITS_DAY = dt.date(2026, 11, 3)
CODES = ("H1", "H2", "H3")


def stand_in(key: str = KEY, **body):
    """A design of the medieval collection made again as a class of its own, so a test can change what it draws
    without touching the design itself. `body` adds to the class."""
    design = type(C.drawn_by(key))
    return type(design.__name__, (design,), dict(body))()


def headers(held, h, night: bool):
    """Every header a design draws for `h`, as (what, drawing): H1, H2 and H3, wide and on a phone."""
    for code in CODES:
        yield f"{code} wide", {"H1": held.h1, "H2": held.h2, "H3": held.h3}[code](h, night, True)
        yield f"{code} phone", {"H1": held.h1_narrow, "H2": held.h2_narrow, "H3": held.h3_narrow}[code](h, night)


def mark(width: int, height: int, month: int, night: bool = False, motion: bool = False) -> Pix:
    """The medieval hand's mark alone, at the top centre of a header `width` units wide."""
    p = Pix(width, height)
    MEDIEVAL.mark(p, width // 2, MARK_Y, month, night, motion)
    return p


def cells(p: Pix) -> dict:
    """Every pixel a drawing holds, by (layer, x, y)."""
    return {(name, x, y): c for name, layer in p.layers.items() for (x, y), c in layer.items()}


def markup(width: int, month: int) -> list[str]:
    """The paths the mark's layers are written as in a header `width` units wide: each is in the file as it is."""
    p = mark(width, 40, month)
    return [p._paths(layer) for layer in p.layers.values() if layer]


def box(width: int) -> tuple:
    """The box the mark is drawn in at the top centre of a header `width` units wide: (x0, y0, x1, y1)."""
    n = MEDIEVAL.mark_size
    x0, y0 = width // 2 - n // 2, MARK_Y - n // 2
    return x0, y0, x0 + n, y0 + n


def contrast_at(ink: str, lightness: float) -> float:
    """The contrast of an ink against a ground of CIELAB lightness `lightness`, whatever the ground's colour."""
    y = ((lightness + 16) / 116) ** 3 if lightness > 8 else lightness / 903.3
    a, b = luminance(ink), y
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


class Hands(unittest.TestCase):
    def test_every_collection_has_a_hand(self):
        self.assertTrue(C.COLLECTIONS)
        for key in C.COLLECTIONS:
            self.assertIn(key, HANDS, key)

    def test_a_hands_inks_hold_4_5_against_both_ends_of_its_bands(self):
        for key, hand in HANDS.items():
            for night, band in ((False, hand.day_ground), (True, hand.night_ground)):
                for edge in band[:2]:
                    for role in ("body", "muted"):
                        self.assertGreaterEqual(contrast_at(getattr(hand, role)[night], edge), 4.5,
                                                (key, role, night, edge))
        self.assertAlmostEqual(contrast_at(MEDIEVAL.muted[0], 72), 4.81, places=2)

    def test_its_tokens_are_its_inks_its_ramps_and_its_marks_colours(self):
        for hand in HANDS.values():
            ramps = hand.ramps
            self.assertEqual(set(ramps), {"flame", "moon", "skin0", "skin1", "skin2"})
            for name, ramp in ramps.items():
                self.assertEqual(hand.ramp(name), ramp)
                self.assertEqual(len(ramp), 7)
                self.assertLessEqual(set(ramp), hand.tokens, name)
            self.assertLessEqual({*hand.body, *hand.muted, *hand.mark.tokens}, hand.tokens)

    def test_a_page_names_one_of_its_hands_twelve_signs_whatever_its_case(self):
        for hand in HANDS.values():
            self.assertEqual(len(hand.signs), 12)
        self.assertEqual(MEDIEVAL.signs, zodiac.SIGNS)
        self.assertEqual([MEDIEVAL.month_of(s) for s in ("aquarius", "Leo", "CAPRICORN", "ophiuchus", "")],
                         [1, 7, 12, 0, 0])
        self.assertEqual(signs("medieval"), [s.lower() for s in zodiac.SIGNS])
        self.assertEqual(signs("medieval-forge"), signs("medieval"))
        self.assertEqual(signs("standard"), signs("medieval"), "every hand's, for a theme that is no collection's")

    def test_lab_measures_as_cielab_does(self):
        light, chroma, hue = lab("#FF0000")
        self.assertAlmostEqual(light, 53.24, places=1)
        self.assertAlmostEqual(chroma, 104.55, places=1)
        self.assertAlmostEqual(hue, 40.0, places=0)
        self.assertAlmostEqual(lab("#FFFFFF")[0], 100, places=2)
        self.assertLess(lab("#808080")[1], 0.01)


class TheMark(unittest.TestCase):
    def test_each_of_the_twelve_signs_is_drawn_each_its_own_and_within_the_box(self):
        self.assertEqual(len(zodiac.SIGNS), 12)
        n, drawn = MEDIEVAL.mark_size, set()
        self.assertTrue(15 <= n <= 19)
        for month in range(1, 13):
            p = Pix(60, 60)
            MEDIEVAL.mark(p, 30, 30, month, False, False)
            got = cells(p)
            self.assertTrue(got, month)
            for _, x, y in got:
                self.assertTrue(30 - n // 2 <= x < 30 - n // 2 + n and 30 - n // 2 <= y < 30 - n // 2 + n,
                                (month, x, y))
            drawn.add(frozenset(got.items()))
        self.assertEqual(len(drawn), 12, "every month's sign is its own")

    def test_every_sign_lies_on_the_lapis_field(self):
        for name, art in zodiac.GLYPHS.items():
            self.assertLessEqual(max(len(row) for row in art), 9, name)
            self.assertLessEqual(len(art), 9, name)
        for month in range(1, 13):
            field = zodiac.layers(month)[2]
            self.assertLessEqual(zodiac._glyph(month), set(field), zodiac.sign(month))

    def test_it_is_the_same_by_day_and_by_night_and_only_a_moving_header_glints(self):
        for month in range(1, 13):
            self.assertEqual(cells(mark(415, 40, month)), cells(mark(415, 40, month, night=True)))
            still, moving = cells(mark(415, 40, month)), cells(mark(415, 40, month, motion=True))
            glint = {k: c for k, c in moving.items() if k not in still}
            self.assertTrue(glint, month)
            self.assertTrue(all(":" in c for c in glint.values()), "the glint is faint, laid over the gold")
            p = mark(415, 40, month, motion=True)
            self.assertTrue(all(p.meta[name][2] == ("twinkle", 0) for name, _, _ in glint), "on the twinkle cadence")

    def test_every_colour_it_paints_is_its_own(self):
        for month in range(1, 13):
            for motion in (False, True):
                for c in cells(mark(415, 40, month, motion=motion)).values():
                    self.assertIn(c.split(":")[0], zodiac.TOKENS, (month, c))

    def test_it_is_compact(self):
        blank = len(Pix(415, 40).svg("t", "d", still=True))
        for month in range(1, 13):
            self.assertLessEqual(len(mark(415, 40, month).svg("t", "d", still=True)) - blank, 950, zodiac.sign(month))


class InTheHeaders(unittest.TestCase):
    """A stand-in, an existing design with `CollectionSet` mixed in, drawn as its month's design and kept all
    year, for every content the holiday sets are held to."""

    def test_a_design_drawn_as_its_months_carries_the_mark_at_the_top_centre_of_every_header(self):
        held = stand_in().on(ITS_DAY)
        month = held.month
        self.assertEqual(month, 11)
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                for what, p in headers(held, h, night):
                    with self.subTest(name, what=what, night=night):
                        want = cells(mark(p.w, p.h, month, night))
                        got = cells(p)
                        self.assertEqual({k: got.get(k) for k in want}, want, "the mark, whole, at the top centre")
                        x0, y0, x1, y1 = box(p.w)
                        self.assertTrue(all(x0 <= x < x1 and y0 <= y < y1 for _, x, y in want), "within its box")
                        self.assertTrue(p.clear_of_words(x0 - 2, y0 - 2, x1 + 2, y1 + 2), "two units clear of words")
                        gx, gy = p.w // 2 + zodiac.GLINT[0], MARK_Y + zodiac.GLINT[1]
                        glints = [layer for (layer, x, y), c in got.items() if (x, y) == (gx, gy)
                                  and c.startswith(zodiac.GOLD[6]) and p.meta[layer][2]
                                  and p.meta[layer][2][0] == "twinkle"]
                        self.assertEqual(len(glints), 1 if what.endswith("wide") else 0, "a glint only if it moves")

    def test_the_mark_is_in_the_file_as_drawn(self):
        held = stand_in().on(ITS_DAY)
        h, _ = contents(KEY)["repository"]
        for code in CODES:
            for theme in (DAY, DARK):
                for wide, motion in ((True, True), (True, False), (False, False)):
                    svg = held.header(code, h, theme, wide, motion)
                    for part in markup(415 if wide else 180, 11):
                        self.assertIn(part, svg, (code, theme, wide, motion))

    def test_a_design_kept_all_year_carries_none(self):
        kept = stand_in()
        self.assertIsNone(kept.day)
        for name in ("kit", "profile", "most"):
            h, _ = contents(KEY)[name]
            for night in (False, True):
                for what, p in headers(kept, h, night):
                    self.assertFalse(any(layer.startswith("mark") for layer in p.layers), (name, what, night))

    def test_a_sign_the_page_chose_is_carried_kept_all_year_and_in_place_of_the_months(self):
        h, _ = contents(KEY)["kit"]
        for held in (stand_in().signed("leo"), stand_in().on(ITS_DAY).signed("Leo")):
            self.assertEqual((held.mark_month, held.marked), (7, True))
            for night in (False, True):
                for what, p in headers(held, h, night):
                    with self.subTest(what=what, night=night, months=held.day is not None):
                        got = cells(p)
                        leo, november = cells(mark(p.w, p.h, 7, night)), cells(mark(p.w, p.h, 11, night))
                        self.assertEqual({k: got.get(k) for k in leo}, leo, "Leo, whole, at the top centre")
                        self.assertNotEqual({k: got.get(k) for k in november}, november, "and not November's")
        self.assertEqual(check(stand_in().signed("leo"), shared()), [])

    def test_a_holidays_set_carries_none(self):
        for key in H.SETS:
            held = H.drawn_by(f"{key}:{H.window(key, 2026).day.isoformat()}")
            self.assertIsNotNone(held.day)
            self.assertEqual(held.mark_size, 0)
            h, _ = contents(key)["repository"]
            for night in (False, True):
                for what, p in headers(held, h, night):
                    self.assertFalse(any(layer.startswith("mark") for layer in p.layers), (key, what, night))

    def test_every_design_knows_the_box_its_mark_takes(self):
        held = stand_in()
        for p in (held.h1(contents(KEY)["kit"][0], False, False), held.h1_narrow(contents(KEY)["kit"][0], False)):
            x0, y0, x1, y1 = box(p.w)
            self.assertEqual(held.mark_box(p), (x0 - 2, y0 - 2, x1 + 2, y1 + 2))
            self.assertEqual(held.mark_box(p, 0), (x0, y0, x1, y1))

    def test_the_hands_colours_join_the_designs_palette(self):
        own = frozenset({"#123456"})
        made = type("Made", (CollectionSet,), {"collection": "medieval", "tokens": own})
        self.assertEqual(made.tokens, own | MEDIEVAL.tokens)
        self.assertLessEqual(MEDIEVAL.tokens | type(C.drawn_by(KEY)).tokens, type(stand_in()).tokens)


def shared(key: str = KEY) -> list:
    """Every content the holiday sets are held to, as `check` takes headers: (what, header)."""
    return [(name, h) for name, (h, _) in contents(key).items()]


def inked(day: str, night: str, **body):
    """A stand-in that sets its words in the hand's inks on a ground of `day` by day and `night` by night. `body`
    adds to its class."""
    design = C.drawn_by(KEY)

    def ink(self, at_night):
        return dict(design.ink(at_night), body=self.hand.body[at_night], muted=self.hand.muted[at_night])

    def bg_at(self, p, at_night, y):
        return night if at_night else day

    return stand_in(**{"ink": ink, "bg_at": bg_at, **body})


class Check(unittest.TestCase):
    """`check` names what breaks the hand, and nothing a design keeps to."""

    def test_a_stand_in_that_keeps_to_its_hand_passes(self):
        self.assertEqual(check(inked("#E6D8B8", "#1E1812"), shared()), [])
        self.assertEqual(check(inked("#E6D8B8", "#1E1812")), [], "with the kit's own lines and samples")

    def test_it_names_a_stand_ins_broken_ink_and_ground_beyond_the_band(self):
        def ink(self, night):
            return dict(C.drawn_by(KEY).ink(night), body="#0C0F14" if not night else self.hand.body[night],
                        muted=self.hand.muted[night])

        self.assertEqual(check(inked("#8F9AA8", "#1E1812", ink=ink), shared()),
                         ["its body ink by day is #0C0F14, not the hand's #22180F",
                          "the ground behind its words by day, #8F9AA8, is L* 63.2, outside 72 to 90"])

    def test_it_names_a_ground_too_light_or_too_cold_and_a_mark_missing_or_moved(self):
        found = " ".join(check(inked("#F4F6FA", "#0D1117")))
        self.assertIn("by day, #F4F6FA, is L* ", found)
        self.assertIn("almost no colour", found)       # a cold white by day
        self.assertNotIn("by night", found)            # a cool near-black night is a night sky
        quiet = inked("#E6D8B8", "#1E1812", month_mark=lambda self, p, cx, cy, night, motion: None)
        type(quiet).tokens = frozenset()      # a palette made without the hand's colours
        found = " ".join(check(quiet))
        self.assertIn("no month's mark", found)
        self.assertIn("not in its palette", found)

        def month_mark(self, p, cx, cy, night, motion):
            CollectionSet.month_mark(self, p, cx - 30, cy, night, motion)

        self.assertIn("away from the top centre", " ".join(check(inked("#E6D8B8", "#1E1812",
                                                                        month_mark=month_mark))))


class EveryDesign(unittest.TestCase):
    """Every drawn design of every collection is drawn in its collection's hand: it subclasses `CollectionSet`, names
    its collection, and `check` finds nothing that breaks the hand, drawn as its month's design, kept all year, and
    with a sign the page chose. A new collection's designs are held to their hand from the first one drawn. Each
    design's own tests run `check` over every shared content; this holds every design to it with the kit's own
    lines."""

    def drawn(self):
        for c in C.COLLECTIONS.values():
            for key in c.keys:
                if C.is_drawn(key):
                    yield c, key

    def test_there_are_designs_to_hold(self):
        self.assertTrue(list(self.drawn()))

    def test_every_design_subclasses_collection_set_and_names_its_collection(self):
        for c, key in self.drawn():
            with self.subTest(key):
                held = C.drawn_by(key)
                self.assertIsInstance(held, CollectionSet)
                self.assertEqual(held.collection, c.key)
                self.assertIs(held.hand, HANDS[c.key])
                self.assertEqual(held.month, c.month_of(key))

    def test_every_design_kept_all_year_with_no_sign_carries_no_mark(self):
        for c, key in self.drawn():
            h, _ = contents(key)["kit"]
            for night in (False, True):
                for what, p in headers(C.drawn_by(key), h, night):
                    self.assertFalse(any(layer.startswith("mark") for layer in p.layers), (key, what, night))

    def test_every_design_keeps_to_its_hand_as_its_months_design_kept_all_year_and_with_a_sign(self):
        for c, key in self.drawn():
            day = dt.date(2026, c.month_of(key), 1).isoformat()
            sign = HANDS[c.key].signs[(c.month_of(key) + 5) % 12]       # another month's sign
            kit = [("the kit's own lines", contents(key)["kit"][0])]
            for held in (C.drawn_by(f"{key}:{day}"), C.drawn_by(key), C.drawn_by(f"{key}:{sign.lower()}")):
                with self.subTest(key=key, day=held.day, sign=held.sign):
                    self.assertEqual(check(held, kit), [])


if __name__ == "__main__":
    unittest.main()
