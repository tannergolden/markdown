# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Every holiday set: each file it draws well formed, within its lint and budget, in the set's own closed
palette, the same every time and at the kit's sizes; letters that hold 4.5:1 on what they sit on; motion only
where the kit allows it; and the kit handing a page to the set while its window is up, file by file, falling
back to the page's own drawing for any file the set cannot draw."""
from __future__ import annotations

import re
import unittest
import xml.dom.minidom as minidom
from unittest import mock

from tests import support

from domain import KIT, KIT_VERSION
from domain import holidays as H
from domain.badges import data as BD
from domain.banners import sample as BS
from domain.banners.compose import LIMITS, compose
from domain.banners.content import Footer, Header
from domain.banners.designs import DESIGNS, check, render
from domain.banners.settings import check as banners_check
from domain.canvas import BUDGET, DARK, DAY, colours, lint
from domain.elements import data as ED
from domain.elements import draw as E
from domain.holidays.designs.badges import PLATE, STATES, STYLES as BADGE_STYLES
from domain.holidays.pixel import Pix, contrast
from domain.palette import PALETTE
from infra.yaml_reader import loads

support.install()
SETS = {key: H.drawn_by(key) for key in H.SETS}
SPECIMEN = loads((support.ROOT / "tests" / "fixtures" / "driftmark" / ".github" / "markdown.yaml").read_text(encoding="utf-8"))
ELEMENTS = ED.merged(ED.check(SPECIMEN["elements"]), {}, subject="driftmark/driftmark", today="2026-09-25")
# The banned dashes, spelled by code point so this file never carries one.
DASHES = ("–", "—", "―")
STAMP = f"{KIT} v{KIT_VERSION} badge"
# The kit's badge heights, in pixels: for-the-badge 28; flat, flat-square and pill 20; plastic 18; compact 16.
HEIGHTS = {"for-the-badge": 28, "flat": 20, "flat-square": 20, "plastic": 18, "pill": 20, "compact": 16}


def contents(key: str) -> dict:
    """Every header and footer a set is held to: the kit's own lines, each sample, the most a page can say, and
    the least."""
    out = {"kit": (Header(tone="standard", holiday=key), Footer(tone="standard", holiday=key))}
    for name, m in BS.SAMPLES.items():
        h, f, _ = compose(m, banners_check({}) | {"theme": "standard", "holiday": key})
        out[name] = (h, f)
    most = Header(title="w" * LIMITS["title"], tagline=("A tagline that says as much as a tagline may. " * 4)[:LIMITS["tagline"]],
                  motto=("A motto as long as a motto may run, " * 3)[:LIMITS["motto"]],
                  notes=(("A second note, as long as a note may run, " * 2)[:LIMITS["motto"]],
                         ("A third note, as long as a note may run, too, " * 2)[:LIMITS["motto"]]),
                  description="And a description under the tagline, which may run as long as it likes to.",
                  figures=(("PROJECT", "o" * 19 + "/" + "r" * 20), ("RELEASE", "v12.34.56"), ("STARS", "123,456"),
                           ("FORKS", "12,345"), ("OPEN ISSUES", "1,234"), ("LANGUAGE", "TypeScript"),
                           ("LICENSE", "Apache-2.0")), tone="standard", holiday=key)
    out["most"] = (most, Footer(tone="standard", holiday=key, closing="Drawn at both ends. " * 4,
                                links=(("Issues", "x"), ("Pull Requests", "x"), ("Releases", "x"), ("Actions", "x"))))
    out["least"] = (Header(title="x", tagline="", motto="", notes=(), description="", figures=(), tone="standard",
                           holiday=key),
                    Footer(tone="standard", holiday=key, closing="", links=(), license="", updated=""))
    return out


def draw_banners(key: str) -> list:
    """Every banner file the set draws for its contents: (content, code, file name, svg)."""
    out = []
    for name, (h, f) in contents(key).items():
        for code, design in DESIGNS.items():
            out += [(name, code, fn, svg) for fn, svg in render(design, h if design.kind == "header" else f).items()]
    return out


DRAWN: dict = {}


def every_banner(key: str) -> list:
    """`draw_banners`, drawn once per set for every test that only reads the files."""
    if key not in DRAWN:
        DRAWN[key] = draw_banners(key)
    return DRAWN[key]


class Registry(unittest.TestCase):
    def test_every_set_is_a_holiday_on_the_calendar_and_draws(self):
        self.assertTrue(SETS)
        for key, held in SETS.items():
            self.assertIn(key, H.KEYS)
            self.assertEqual((held.key, held.name), (key, H.NAMES[key]))
            self.assertTrue(held.tokens)

    def test_a_set_is_told_the_day_its_holiday_falls_on_and_the_shared_one_is_not(self):
        import datetime as dt
        for key, held in SETS.items():
            on = H.drawn_by(f"{key}:2026-10-31")
            self.assertEqual((on.key, on.day), (key, dt.date(2026, 10, 31)))
            self.assertIsNone(held.day)
            self.assertIsNone(H.drawn_by(key).day)

    def test_a_holiday_without_its_set_and_no_holiday_draw_nothing(self):
        for key in ("", None, "no-such-day", *[k for k in H.KEYS if k not in H.SETS]):
            self.assertIsNone(H.drawn_by(key), key)


class Banners(unittest.TestCase):
    def test_every_file_is_the_sets_well_formed_linted_and_deterministic(self):
        for key, held in SETS.items():
            drawn = {(n, c, fn): svg for n, c, fn, svg in every_banner(key)}
            for (name, code, fn), svg in drawn.items():
                minidom.parseString(svg)
                self.assertIn(f"<!--{KIT} v{KIT_VERSION} {key} ", svg, (key, name, fn))
                self.assertNotIn("<text", svg)
                for ch in DASHES:
                    self.assertNotIn(ch, svg)
            for name, code, fn, svg in draw_banners(key):
                self.assertEqual(svg, drawn[(name, code, fn)], (key, name, fn))
            for name in contents(key):
                for code, design in DESIGNS.items():
                    files = {fn: svg for (n, c, fn), svg in drawn.items() if (n, c) == (name, code)}
                    self.assertEqual(check(design, files, held.tokens), {}, (key, name, code))

    def test_files_are_the_kits_sizes_and_names(self):
        for key in SETS:
            drawn = every_banner(key)
            for name, (h, f) in contents(key).items():
                for code, design in DESIGNS.items():
                    content = h if design.kind == "header" else f
                    files = {fn: svg for n, c, fn, svg in drawn if (n, c) == (name, code)}
                    self.assertEqual(set(files), set(render(design, content.with_(holiday=""))), (key, name, code))
                    for fn, svg in files.items():
                        w = int(re.search(r'width="(\d+)"', svg).group(1))
                        if fn.startswith("link-"):
                            self.assertLess(w, 300, fn)
                        else:
                            self.assertEqual(w, 360 if "narrow" in fn else 830, (key, name, fn))

    def test_only_a_wide_moving_header_moves(self):
        for key in SETS:
            for name, code, fn, svg in every_banner(key):
                if "still" in fn or "narrow" in fn or fn.startswith(("footer", "link")):
                    self.assertNotIn("<animate", svg, (key, name, fn))
            h, _ = contents(key)["repository"]
            self.assertIn("<animate", render(DESIGNS["H2"], h)["header-day.svg"], key)

    def test_text_colours_hold_4_5_on_the_paper_and_every_row_of_the_sky(self):
        for key, held in SETS.items():
            for night in (False, True):
                k = held.ink(night)
                p = Pix(415, 200)
                grounds = {held.bg_at(p, night, y) for y in range(p.h)}
                for role in ("title", "body", "muted", "accent"):
                    for ground in grounds:
                        self.assertGreaterEqual(contrast(k[role], ground), 4.5, (key, night, role, ground))
                self.assertGreaterEqual(contrast(k["tag_ink"], k["tag"]), 4.5, (key, night, "tag"))

    def test_a_file_too_heavy_is_drawn_lighter_then_still_and_stays_the_sets(self):
        for key, held in SETS.items():
            h, _ = contents(key)["repository"]
            full = held.header("H2", h, DARK, True, True)
            self.assertIn("<animate", full)
            with mock.patch.dict(BUDGET, {"header": len(full.encode("utf-8")) - 1}):
                lighter = held.header("H2", h, DARK, True, True)
            self.assertLess(len(lighter), len(full), key)
            self.assertIn("<animate", lighter, "a lighter drawing keeps its motion while it fits")
            self.assertIn(f"{key} H2 dark-->", lighter)
            with mock.patch.dict(BUDGET, {"header": 1000}):
                last = held.header("H2", h, DARK, True, True)
            self.assertNotIn("<animate", last, "motion is the last thing to go")
            self.assertFalse(held._lite, "the set is left drawing lighter")
            most, _ = contents(key)["most"]
            for code in ("H1", "H2", "H3"):
                for theme in (DAY, DARK):
                    svg = held.header(code, most, theme, True, True)
                    self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"], (key, code, theme["name"]))


class Fallback(unittest.TestCase):
    def test_a_file_the_set_cannot_draw_is_drawn_in_the_pages_own_theme(self):
        for key, held in SETS.items():
            h, f = contents(key)["repository"]
            with mock.patch.object(type(held), "header", lambda *a, **k: "<svg/>"):
                files = render(DESIGNS["H2"], h)
            own = render(DESIGNS["H2"], h.with_(holiday=""))
            self.assertEqual(files, own, key)
            with mock.patch.object(type(held), "link", lambda *a, **k: "<svg/>"):
                links = {fn: svg for fn, svg in render(DESIGNS["F1"], f).items() if fn.startswith("link-")}
            self.assertTrue(links)
            self.assertTrue(all(f"{key} " not in svg.split("-->")[0] for svg in links.values()), key)

    def test_a_character_the_sets_letters_lack_hands_the_file_back(self):
        for key in SETS:
            h, _ = contents(key)["repository"]
            files = render(DESIGNS["H2"], h.with_(title="中文"))
            self.assertNotIn(f" {key} ", files["header-day.svg"].split("-->")[0], key)


class Elements(unittest.TestCase):
    def test_every_element_is_the_sets_linted_deterministic_and_the_kits_files(self):
        for key, held in SETS.items():
            files = ED.render(ELEMENTS, "standard", key)
            self.assertEqual(set(files), set(ED.render(ELEMENTS, "standard")), key)
            again = ED.render(ELEMENTS, "standard", key)
            for eid, d in ELEMENTS.items():
                kind = d["kind"]
                for variant in E.variants(kind, d):
                    for theme in ("day", "dark"):
                        name = ED.file_name(eid, variant, theme)
                        svg = files[name]
                        minidom.parseString(svg)
                        self.assertEqual(svg, again[name], name)
                        self.assertIn(f"<!--{KIT} v{KIT_VERSION} {key} elements {kind} ", svg, name)
                        self.assertEqual(lint(svg, budget=BUDGET[E.KINDS[kind][2]], tokens=held.tokens), [], name)
                        w = int(re.search(r'width="(\d+)"', svg).group(1))
                        wanted = (404 if kind == "placard" or variant == "half" or
                                  (variant == "narrow" and kind in ("roster", "certificate"))
                                  else 360 if variant == "narrow" else 830)
                        self.assertEqual(w, wanted, name)

    def test_the_half_page_pair_is_drawn_level(self):
        for key in SETS:
            files = ED.render(ELEMENTS, "standard", key)
            heights = {re.search(r'height="(\d+)"', files[f"{eid}-day.svg"]).group(1)
                       for eid in ("contributors", "conformance")}
            self.assertEqual(len(heights), 1, key)

    def test_odd_data_is_drawn_whole(self):
        for key, held in SETS.items():
            bare = {"kind": "roster", "subject": "x/y", "people": [
                {"name": "A PERSON WITH A NAME FAR LONGER THAN A COLUMN", "handle": "@" + "h" * 30, "initials": "AP",
                 "n": 3, "first": "1 JAN 2020", "last": "31 DEC 2026"}]}
            svg = held.element("roster", E.describe("roster", bare), DAY, "wide")
            self.assertEqual(lint(svg, budget=BUDGET["sheet"], tokens=held.tokens), [], key)
            cert = dict(ELEMENTS["conformance"], name="an-extraordinarily-long-name",
                        ring_bottom="V12 · VERIFIED 31 DECEMBER 2026 AT LENGTH")
            for variant in ("wide", "half"):
                svg = held.element("certificate", E.describe("certificate", cert), DARK, variant)
                self.assertEqual(lint(svg, budget=BUDGET["sheet"], tokens=held.tokens), [], (key, variant))


class Badges(unittest.TestCase):
    def badge(self, held, style, **kw):
        args = dict(style=style, label="Build", message="Passing", icon="pulse", label_hex=PALETTE["black"],
                    message_hex=PALETTE["blue"], live=False, state=None, reserve=(), rels=["static/b.svg"],
                    stamp=STAMP)
        args.update(kw)
        return held.badge(**args)

    def check_file(self, held, svg, px_height, what):
        self.assertEqual(BD.lint(svg), [], what)
        self.assertEqual(colours(svg, held.tokens), [], what)
        minidom.parseString(svg)
        self.assertEqual(int(re.search(r'height="(\d+)"', svg).group(1)), px_height, what)

    def test_every_style_classic_plate_and_live_is_the_kits_height_and_files(self):
        for key, held in SETS.items():
            for style in BADGE_STYLES:
                one = self.badge(held, style)
                self.assertEqual(list(one), ["static/b.svg"])
                self.check_file(held, one["static/b.svg"], HEIGHTS[style], (key, style))
                two = self.badge(held, PLATE + style, rels=["static/b.svg", "static/b-dark.svg"])
                self.assertEqual(list(two), ["static/b.svg", "static/b-dark.svg"])
                self.assertNotEqual(*two.values())
                for rel, svg in two.items():
                    self.check_file(held, svg, HEIGHTS[style], (key, style, rel))
                for state in STATES:
                    for form in (style, PLATE + style):
                        live = self.badge(held, form, live=True, state=state, label_hex=PALETTE["gold"],
                                          message_hex=PALETTE[state], rels=["dynamic/b.svg"])
                        self.assertEqual(list(live), ["dynamic/b.svg"])
                        self.check_file(held, live["dynamic/b.svg"], HEIGHTS[style], (key, form, state))

    def test_a_live_plate_keeps_its_width_whatever_it_says(self):
        for key, held in SETS.items():
            widths = set()
            for state, message in (("green", "Passing"), ("red", "Failing"), ("slate", "No Data")):
                svg = self.badge(held, PLATE + "flat", live=True, state=state, message=message,
                                 reserve=("Passing", "Failing", "No Data"), rels=["dynamic/b.svg"])["dynamic/b.svg"]
                widths.add(re.search(r'width="(\d+)"', svg).group(1))
            self.assertEqual(len(widths), 1, key)

    def test_every_letter_holds_4_5_on_its_block(self):
        for key, held in SETS.items():
            pairs = [("label", *held.badge_label()), ("gold", *held.badge_gold())]
            pairs += [(f"state {s}", *held.badge_states()[s]) for s in STATES]
            pairs += [(f"swatch {n}", bg, ink) for n, (bg, ink, _) in held.badge_swatches().items()]
            for mode in ("day", "night"):
                k = held.plate_colours(mode)
                pairs += [(f"{mode} block", k["block"], k["letters"]), (f"{mode} paper", k["paper"], k["ink"]),
                          (f"{mode} dot", k["dot"], k["ink"])]
            k = held.plate_colours("live")
            pairs += [("live paper", k["paper"], k["ink"]), ("live dot", k["dot"], k["ink"])]
            for what, ground, ink in pairs:
                self.assertGreaterEqual(contrast(ink, ground), 4.5, (key, what))

    def test_a_written_colour_takes_the_nearest_the_set_has(self):
        for key, held in SETS.items():
            swatches = held.badge_swatches()
            for name, (block, _, _) in swatches.items():
                svg = self.badge(held, "flat", message_hex=block)["static/b.svg"]
                self.assertIn(block, svg, (key, name))

    def test_what_the_sets_letters_cannot_draw_is_left_to_the_kit(self):
        for key, held in SETS.items():
            self.assertIsNone(self.badge(held, "flat", message="中文"), key)

    def test_the_kit_draws_a_badge_in_the_set_at_the_paths_it_always_uses(self):
        for key in SETS:
            static = {"name": "license", "label": "License", "message": "MIT", "icon": "scale"}
            for theme in ("standard", "blueprint"):
                own = BD.draw(static, {}, theme=theme, shade=None, seed="2026W44")
                held = BD.draw(static, {}, theme=theme, shade=None, seed="2026W44", holiday=key)
                self.assertEqual(set(own), set(held), (key, theme))
                self.assertNotEqual(own, held, (key, theme))
            measured = {"ci": {"message": "Failing", "state": "red"}}
            live = {"name": "ci", "label": "CI", "icon": "pulse", "measure": {"kind": "workflow"}}
            files = BD.draw(live, measured, theme="blueprint", shade=None, seed="2026W44", holiday=key)
            self.assertEqual(list(files), ["dynamic/ci.svg"])
            self.assertIn(SETS[key].badge_states()["red"][0], files["dynamic/ci.svg"])


if __name__ == "__main__":
    unittest.main()
