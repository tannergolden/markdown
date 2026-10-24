# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The trophy case in every look: the page's theme decides it, a print draws it on its drafting paper and a pixel
set in its pixels; every file within its lint, its palette, its budget and the standard look's size, its words the
same in every look; motion in CSS that holds still for reduced motion; and a case a set cannot letter drawn in the
page's own look, with a note."""
from __future__ import annotations

import json
import re
import unittest
import xml.dom.minidom as minidom
from unittest import mock

from tests import support

from domain import collections, holidays, pixelsets, pixelthemes, prints
from domain.canvas import BUDGET, DARK, DAY, colours
from domain.holidays.designs import trophies as T
from domain.holidays.pixel import Pix
from domain.palette import contrast, hexof, letters_on
from domain.trophies import catalogue as C
from domain.trophies import looks as L
from domain.trophies import plan as P
from domain.trophies import sample as S
from domain.trophies import settings as TS

CATALOGUE = support.install()
STYLES = ("trophy", "crest", "medallion", "crystal", "plaque")
CASES = ("day", "night")
CORE = C.RCORE[0]
SIZES = {"card": (164, 222), "plaque": (264, 88), "pin": (104, 124), "level": (420, 152), "next-up": (328, 152)}
SETS = ([k for k in holidays.KEYS if k in holidays.SETS]
        + [k for c in collections.COLLECTIONS.values() for k in c.keys] + pixelthemes.themes())
HALLOWEEN = "halloween:2026-10-31"


def values(core) -> list[int]:
    """A value in every tier: unranked, bronze to platinum, and diamond with a star."""
    st = core.steps
    return [st[0] // 3, st[0], st[1] + 1, st[2] + 2, st[3] + 3, st[4] * 2 + 5]


def size(svg: str) -> tuple[int, int]:
    m = re.search(r'<svg\b[^>]*?\swidth="(\d+)" height="(\d+)"', svg)
    return int(m[1]), int(m[2])


def sample(mode: str = "repository") -> dict:
    s = json.loads(json.dumps(S.SAMPLES[mode]))
    s["owners"] = {a.only: s["subject"].split("/")[0] for a in C.MODES[mode]["ach"] if a.only}
    return s


def planned(theme: str = "standard", holiday: str = "", section: dict | None = None, mode: str = "repository",
            subject: str | None = None) -> dict:
    s = sample(mode)
    if subject:
        s["subject"] = subject
    return P.plan(s, TS.check(section or {}), folder="assets/trophies", base="assets/trophies", theme=theme,
                  holiday=holiday)


def stamps(plan: dict) -> set[str]:
    return {re.search(r"<!--markdown-kit v1 trophy ([^>]*?)-->", svg)[1].rsplit(" ", 1)[0]
            if re.search(r"trophy \S+ (?:day|night)-->", svg) else "standard" for svg in plan["files"].values()}


class TheLookFollowsThePage(unittest.TestCase):
    def test_a_page_in_standard_keeps_the_standard_look(self):
        self.assertEqual([type(look) for look in L.looks(TS.check({}))], [L.Standard])
        self.assertEqual(stamps(planned()), {"standard"})

    def test_a_print_draws_the_case_and_hands_it_to_standard_if_it_cannot(self):
        self.assertEqual([type(look) for look in L.looks(TS.check({}), "blueprint")], [L.Drafted, L.Standard])
        self.assertEqual(stamps(planned("blueprint")), {"blueprint"})

    def test_rainbowprint_draws_the_case_in_the_print_it_is_on(self):
        # The page hands the case its resolved print, as it hands every part.
        self.assertEqual(stamps(planned("tealprint")), {"tealprint"})

    def test_a_holidays_set_and_a_collections_design_draw_the_case_in_their_pixels(self):
        tried = L.looks(TS.check({}), "blueprint", HALLOWEEN)
        self.assertEqual([type(look) for look in tried], [L.Pixels, L.Drafted, L.Standard])
        self.assertEqual(tried[0].held.key, "halloween")
        self.assertEqual(stamps(planned("blueprint", HALLOWEEN)), {"halloween"})
        design = L.looks(TS.check({}), "standard", "medieval-forge:2026-11-01")
        self.assertEqual([type(look) for look in design], [L.Pixels, L.Standard])
        self.assertEqual(stamps(planned("standard", "medieval-forge:2026-11-01")), {"medieval-forge"})

    def test_look_standard_keeps_the_trophies_kits_case_in_every_theme(self):
        section = {"look": "standard"}
        standard = planned(section=section)["files"]
        self.assertEqual(planned("blueprint", HALLOWEEN, section)["files"], standard)
        self.assertEqual(planned("standard")["files"], standard)

    def test_the_case_says_the_same_words_in_every_look(self):
        block = planned()["block"]
        for theme, holiday in (("blueprint", ""), ("blackprint", ""), ("standard", HALLOWEEN),
                               ("standard", "medieval-hoard:2026-12-01")):
            p = planned(theme, holiday)
            self.assertEqual(p["block"], block, (theme, holiday))
            self.assertEqual(p["notes"], [])

    def test_a_case_a_set_cannot_letter_is_drawn_in_the_pages_own_look_with_a_note(self):
        p = planned("blueprint", HALLOWEEN, subject="octo-dev/日本")
        self.assertEqual(stamps(p), {"blueprint"})
        self.assertEqual(p["look"], "blueprint")
        self.assertTrue(p["notes"] and "the Halloween set cannot letter" in p["notes"][0], p["notes"])

    def test_a_repository_with_its_own_print_draws_the_case_in_those_colours(self):
        try:
            prints.use(CATALOGUE, {"goldprint": {"line": "#B8860B", "ink": "#5C4400", "sheet": "#7A5B00"}})
            p = planned("goldprint")
            self.assertEqual(stamps(p), {"goldprint"})
            joined = "".join(p["files"].values())
            self.assertIn("#B8860B", joined)
            for rel, svg in p["files"].items():
                self.assertEqual(colours(svg), [], rel)
        finally:
            support.install()


class APrintsCase(unittest.TestCase):
    def standard_size(self, style: str) -> tuple[int, int]:
        return SIZES["plaque" if style == "plaque" else "card"]

    def test_every_card_in_every_print_lints_keeps_the_palette_and_the_standard_size(self):
        for tone in prints.PRINTS:
            for style in STYLES:
                look = L.Drafted(style, tone)
                for case in CASES:
                    for i, v in enumerate(values(CORE)):
                        o = {"rank": True, "delta": 3 * i, "new": i % 2 == 1}
                        svg = look.card(case, CORE, v, o)
                        where = (tone, style, case, v)
                        self.assertEqual(P.lint(svg), [], where)
                        self.assertEqual(colours(svg), [], where)
                        self.assertEqual(size(svg), self.standard_size(style), where)
                        self.assertEqual(svg, look.card(case, CORE, v, o), where)
                        minidom.parseString(svg)

    def test_its_pins_level_and_next_up_lint_and_keep_the_standard_sizes(self):
        s = sample()
        m = C.MODES["repository"]
        foot = P.foot_of(s, TS.check({}))
        for tone in ("blueprint", "yellowprint", "blackprint"):
            look = L.Drafted("trophy", tone)
            for case in CASES:
                drawn = {"level": look.level(case, m["core"], s["values"], m["ach"], s["curs"], s["subject"], foot),
                         "next-up": look.next_up(case, m["core"], s["values"], m["ach"], s["curs"])}
                for name, svg in drawn.items():
                    self.assertEqual((P.lint(svg), colours(svg), size(svg)), ([], [], SIZES[name]), (tone, case, name))
                for a in m["ach"]:
                    for cur in (None, 0, a.tiers[0], a.tiers[-1]):
                        svg = look.pin(case, a, cur)
                        self.assertEqual((P.lint(svg), colours(svg), size(svg)), ([], [], SIZES["pin"]),
                                         (tone, case, a.slug, cur))

    def test_every_colour_is_the_prints_own(self):
        for tone in prints.PRINTS:
            for case, th in (("day", DAY), ("night", DARK)):
                col = prints.colours(tone, th)
                own = {hexof(col[k]) for k in ("line", "ink", "paper", "edge")} | {hexof("white"), hexof("black")}
                for style in STYLES:
                    for v in values(CORE):
                        svg = L.Drafted(style, tone).card(case, CORE, v, {"rank": True, "new": True})
                        found = {h.upper() for h in re.findall(r"#[0-9A-Fa-f]{6}\b", svg)}
                        self.assertLessEqual(found, own, (tone, case, style, v))

    def test_every_word_holds_four_and_a_half_to_one_on_its_paper(self):
        for tone in prints.PRINTS:
            for th in (DAY, DARK):
                col = prints.colours(tone, th)
                self.assertGreaterEqual(contrast(col["ink"], col["paper"]), 4.5, (tone, th["name"]))
                block = col["paper"] if contrast(col["paper"], col["line"]) >= 4.5 else letters_on(col["line"])
                self.assertGreaterEqual(contrast(block, col["line"]), 4.5, (tone, th["name"]))

    def test_its_motion_is_css_and_holds_still_for_reduced_motion(self):
        for style in STYLES:
            for v in values(CORE):
                svg = L.Drafted(style, "blueprint").card("night", CORE, v, {"new": True})
                self.assertNotIn("<animate", svg)
                self.assertIn("prefers-reduced-motion:reduce", svg)

    def test_the_drawing_grows_with_its_tier(self):
        v = values(CORE)
        look = L.Drafted("trophy", "blueprint")
        unranked, gold, platinum = (look.card("day", CORE, v[i], {}) for i in (0, 3, 4))
        self.assertIn('stroke-dasharray="7 2 1.5 2 1.5 2"', unranked, "an unranked trophy is a phantom")
        self.assertNotIn('class="sh"', unranked)
        self.assertIn('class="sh"', gold, "gold glints")
        self.assertNotIn('class="sp"', gold)
        self.assertIn('class="sp"', platinum, "platinum sparkles")

    def test_its_shaded_side_darkens_tier_by_tier(self):
        # A print's tiers read as a metal's do: the shaded side lined at gold, the lining crossed at platinum, and
        # at diamond inked solid with its lining cut back through it in the paper.
        v = values(CORE)
        for style in STYLES:
            look = L.Drafted(style, "blueprint")
            gold, platinum, diamond = (look.card("day", CORE, v[i], {}) for i in (3, 4, 5))
            self.assertNotIn('patternTransform="rotate(-45)"', gold if style != "crystal" else "", style)
            self.assertIn('patternTransform="rotate(-45)"', platinum, f"a platinum {style}'s lining is crossed")
            self.assertNotIn('fill-opacity=".9"', gold + platinum, style)
            self.assertIn('fill-opacity=".9"', diamond, f"a diamond {style}'s shaded side is inked solid")


class APixelSetsCase(unittest.TestCase):
    def test_every_card_lints_keeps_the_sets_palette_and_the_standard_size(self):
        for key in SETS:
            held = pixelsets.drawn_by(key)
            for style in STYLES:
                look = L.Pixels(style, held)
                for case in CASES:
                    for i, v in enumerate(values(CORE)):
                        o = {"rank": True, "delta": 4 * i, "new": i % 2 == 1}
                        svg = look.card(case, CORE, v, o)
                        where = (key, style, case, v)
                        self.assertEqual(P.lint(svg), [], where)
                        self.assertEqual(colours(svg, held.trophy_tokens), [], where)
                        self.assertEqual(size(svg), SIZES["plaque" if style == "plaque" else "card"], where)
                        self.assertNotIn("<animate", svg, where)
                        self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["trophy"], where)

    def test_its_pins_level_and_next_up_lint_and_keep_the_standard_sizes(self):
        s = sample()
        m = C.MODES["repository"]
        foot = P.foot_of(s, TS.check({}))
        pins = [a for a in m["ach"] if a.secret][:1] + [a for a in m["ach"] if a.goals][:2] + m["ach"][:4]
        pins += [a for a in m["ach"] if a.slug in ("constellation", "containerized", "well-formed")]
        for key in SETS:
            held = pixelsets.drawn_by(key)
            look = L.Pixels("trophy", held)
            for case in CASES:
                drawn = {"level": look.level(case, m["core"], s["values"], m["ach"], s["curs"], s["subject"], foot),
                         "next-up": look.next_up(case, m["core"], s["values"], m["ach"], s["curs"])}
                for name, svg in drawn.items():
                    self.assertEqual((P.lint(svg), colours(svg, held.trophy_tokens), size(svg)), ([], [], SIZES[name]),
                                     (key, case, name))
                for a in pins:
                    for cur in (None, 0, a.tiers[0], a.tiers[-1]):
                        svg = look.pin(case, a, cur)
                        self.assertEqual((P.lint(svg), colours(svg, held.trophy_tokens), size(svg)),
                                         ([], [], SIZES["pin"]), (key, case, a.slug, cur))

    def test_every_word_is_lettered_in_the_sets_own_inks(self):
        s = sample()
        m = C.MODES["repository"]
        seen: list = []
        real = Pix.text

        def text(self, x, y, s_, c, *args, **kw):
            seen.append(c)
            return real(self, x, y, s_, c, *args, **kw)

        with mock.patch.object(Pix, "text", text):
            for key in SETS:
                held = pixelsets.drawn_by(key)
                for night in (False, True):
                    case = "night" if night else "day"
                    k = held.ink(night)
                    inks = {k[role] for role in ("title", "body", "muted", "accent", "tag_ink")}
                    seen.clear()
                    for style in STYLES:
                        for v in values(CORE):
                            L.Pixels(style, held).card(case, CORE, v, {"rank": True, "delta": 2, "new": True})
                    look = L.Pixels("trophy", held)
                    look.level(case, m["core"], s["values"], m["ach"], s["curs"], s["subject"],
                               P.foot_of(s, TS.check({})))
                    look.next_up(case, m["core"], s["values"], m["ach"], s["curs"])
                    for a in m["ach"][:6]:
                        look.pin(case, a, s["curs"].get(a.slug))
                    self.assertLessEqual(set(seen), inks, (key, case))

    def test_every_file_keeps_clear_of_the_sets_frame(self):
        # Nothing a file draws lies on the set's frame, within a unit of it or in the squares its corner pieces take,
        # and no word comes within two units of it: a word's box, a unit all round it, keeps inside the room.
        m = C.MODES["repository"]
        pins = [a for a in m["ach"] if a.secret][:1] + [a for a in m["ach"] if a.goals][:1]
        pins += [a for a in m["ach"] if a.slug in ("constellation", "well-formed", "used-by")]
        for key in SETS:
            held = pixelsets.drawn_by(key)
            for night in (False, True):
                jobs = [(T.PLAQUE if style == "plaque" else T.CARD,
                         lambda st=style, v=v, i=i: held.trophy_card(st, CORE, v, {"rank": True, "delta": 14,
                                                                                   "new": i in (1, 4)}, night))
                        for style in STYLES for i, v in enumerate(values(CORE)) if i in (0, 1, 4, 5)]
                jobs += [(T.PIN, lambda a=a, cur=cur: held.trophy_pin(a, cur, night))
                         for a in pins for cur in (None, a.tiers[0], a.tiers[-1])]
                for mode in ("repository", "profile"):
                    sm, mm = sample(mode), C.MODES[mode]
                    fm = P.foot_of(sm, TS.check({}))
                    jobs += [(T.LEVEL, lambda sm=sm, mm=mm, fm=fm: held.trophy_level(
                                 mm["core"], sm["values"], mm["ach"], sm["curs"], sm["subject"], fm, night)),
                             (T.NEXT, lambda sm=sm, mm=mm: held.trophy_next_up(mm["core"], sm["values"], mm["ach"],
                                                                               sm["curs"], night))]
                for dims, draw in jobs:
                    got = []
                    real = type(held)._finish
                    with mock.patch.object(type(held), "_finish", lambda self, p, n: (got.append(p), real(self, p, n))):
                        draw()
                    p = got[0]
                    ground = held._card_canvas(dims, night)
                    room = held._trophy_room(p)

                    def inside(x, y, room=room, p=p):
                        corner = (x < room.corner or x >= p.w - room.corner) and (y < room.corner or
                                                                                  y >= p.h - room.corner)
                        return room.x0 <= x < room.x1 and room.y0 <= y < room.y1 and not corner

                    drawn = {xy for L, px in p.layers.items() for xy, c in px.items()
                             if ground.layers.get(L, {}).get(xy) != c}
                    self.assertEqual({xy for xy in drawn if not inside(*xy)}, set(), (key, night, dims))
                    for x0, y0, x1, y1 in p.words:
                        self.assertTrue(all(inside(x, y) for x in (x0, x1 - 1) for y in (y0, y1 - 1)),
                                        (key, night, dims, (x0, y0, x1, y1)))

    def test_a_collections_design_letters_its_trophies_in_its_hands_two_inks(self):
        for key in (k for c in collections.COLLECTIONS.values() for k in c.keys):
            held = pixelsets.drawn_by(key)
            for night in (False, True):
                k = held.ink(night)
                self.assertEqual((k["body"], k["muted"]), (held.hand.body[night], held.hand.muted[night]), key)

    def test_its_motion_is_css_and_holds_still_for_reduced_motion(self):
        held = pixelsets.drawn_by("christmas")
        v = values(CORE)
        bronze, gold, platinum = (L.Pixels("trophy", held).card("night", CORE, v[i], {}) for i in (1, 3, 4))
        self.assertNotIn("<style>", bronze, "a bronze trophy holds still")
        self.assertIn('class="gl"', gold, "gold glints")
        self.assertIn('class="tw"', platinum, "platinum twinkles")
        for svg in (gold, platinum):
            self.assertIn("prefers-reduced-motion:reduce", svg)
            self.assertNotIn("<animate", svg)

    def test_a_collections_design_glints_on_its_hands_period(self):
        held = pixelsets.drawn_by("medieval-forge")
        gold = L.Pixels("trophy", held).card("day", CORE, values(CORE)[3], {})
        self.assertIn(f"animation:gl {held.hand.glint:g}s", gold)


if __name__ == "__main__":
    unittest.main()
