# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The standard theme: every banner well formed and within budget, every letter on a ground it holds 4.5:1
against, motion that is complete without SMIL, and nothing drawn that the alt text does not say."""
from __future__ import annotations

import re
import unittest
import xml.dom.minidom as minidom

from tests import support

from domain.banners import sample as BS
from domain.canvas import BUDGET, lint
from domain.lettering import width
from domain.elements import data as ED
from domain.elements import draw as E
from domain.banners.compose import compose
from domain.banners.content import Footer, Header
from domain.banners.designs import DESIGNS, check, render
from domain.banners.settings import check as banners_check
from domain.canvas import DARK, DAY
from domain.palette import PALETTE
from domain.standard import banners as SB
from domain.standard import elements as SE
from domain.standard import pieces as P
from infra.yaml_reader import loads

support.install()
SPECIMEN = loads((support.ROOT / "tests" / "fixtures" / "driftmark" / ".github" / "markdown.yaml").read_text(encoding="utf-8"))
ELEMENTS = ED.merged(ED.check(SPECIMEN["elements"]), {}, subject="driftmark/driftmark")
# The banned dashes, spelled by code point so this file never carries one.
DASHES = ("–", "—", "―")


def contents() -> dict:
    out = {"kit": (Header(tone="standard"), Footer(tone="standard"))}
    for key, m in BS.SAMPLES.items():
        h, f, _ = compose(m, banners_check({}) | {"theme": "standard"})
        out[key] = (h, f)
    return out


CONTENTS = contents()


def every_file():
    for name, (h, f) in CONTENTS.items():
        for code, design in DESIGNS.items():
            for fn, svg in render(design, h if design.kind == "header" else f).items():
                yield name, code, fn, svg


class Pieces(unittest.TestCase):
    def test_letters_on_holds_every_token_to_4_5(self):
        for token in PALETTE:
            self.assertGreaterEqual(P.contrast(P.letters_on(token), token), 4.5, token)

    def test_contrast_is_wcags(self):
        self.assertAlmostEqual(P.contrast("white", "black"), 21, places=6)
        self.assertEqual(P.contrast("white", "white"), 1)

    def test_every_figure_label_the_headers_give_has_a_badge(self):
        from domain.banners.compose import FIGURES
        for mode, labels in FIGURES.items():
            for label in labels.values():
                self.assertIn(label, P.FIGURES, (mode, label))

    def test_a_badge_is_measured_as_the_badges_kit_sets_one(self):
        chip = P.Chip("stars", "1,284", icon="star", size=11)
        self.assertEqual(chip.h, 28)
        self.assertEqual((chip.label, chip.message), ("STARS", "1,284"))
        self.assertAlmostEqual(chip.w, chip.lw + chip.mw)


class EveryBanner(unittest.TestCase):
    def test_every_file_is_well_formed_linted_and_deterministic(self):
        again = {(n, c, fn): svg for n, c, fn, svg in every_file()}
        for (name, code, fn), svg in again.items():
            minidom.parseString(svg)
            self.assertIn("<!--markdown-kit v1 standard ", svg, fn)
            self.assertNotIn("<text", svg)
            for ch in DASHES:
                self.assertNotIn(ch, svg)
        for name, code, fn, svg in every_file():
            self.assertEqual(svg, again[(name, code, fn)], (name, code, fn))
        for name, (h, f) in CONTENTS.items():
            for code, design in DESIGNS.items():
                files = render(design, h if design.kind == "header" else f)
                self.assertEqual(check(design, files), {}, (name, code))

    def test_every_letter_holds_4_5_against_its_ground(self):
        P.PAIRS.clear()
        for _ in every_file():
            pass
        self.assertTrue(P.PAIRS)
        for fill, ground, what in P.PAIRS:
            self.assertGreaterEqual(P.contrast(fill, ground), 4.5, (fill, ground, what))

    def test_narrow_files_are_a_phones_width_and_the_rest_a_pages(self):
        for name, code, fn, svg in every_file():
            w = int(re.search(r'width="(\d+)"', svg).group(1))
            if fn.startswith("link-"):
                self.assertLess(w, 300, fn)
            else:
                self.assertEqual(w, 360 if "narrow" in fn else 830, (name, code, fn))


class Motion(unittest.TestCase):
    def test_a_still_file_and_a_phones_never_move(self):
        for name, code, fn, svg in every_file():
            if "still" in fn or "narrow" in fn or fn.startswith(("footer", "link")):
                self.assertNotIn("<animate", svg, (name, code, fn))

    def test_a_moving_file_rests_on_its_drawing(self):
        h, _ = CONTENTS["repository"]
        svg = SB.section(h, DAY, True, True)
        self.assertIn("<animate", svg)
        for tag in re.findall(r"<animate[^>]*>", svg):
            self.assertIn('fill="freeze"', tag)
        # The band opens from nothing to the card's full width, and the width it rests at is the full width.
        self.assertRegex(svg, r'<rect x="0" y="0" width="830" height="\d+"><animate attributeName="width" '
                              r'values="0;0;830"')
        # Everything that rises in is fully opaque at rest.
        self.assertNotIn('<g opacity="0"', svg)


class WhatIsDrawn(unittest.TestCase):
    def drawn(self, fn, *args) -> set:
        P.PAIRS.clear()
        fn(*args)
        return {what for _, _, what in P.PAIRS}

    def test_the_band_carries_the_release_and_the_kicker_the_path(self):
        h, _ = CONTENTS["repository"]
        said = self.drawn(SB.section, h, DAY, True, True)
        self.assertTrue({"title", "release", "kicker", "tagline", "figure label", "figure message"} <= said, said)

    def test_the_strip_draws_the_path_as_a_badge_rather_than_dropping_it(self):
        h, _ = CONTENTS["repository"]
        msg, kick, rest = SB.parts(h, kicker=False)
        self.assertIsNone(kick)
        self.assertIn("PROJECT", [label for label, _ in rest])
        self.assertNotIn("kicker", self.drawn(SB.strip, h, DAY, True, True))

    def test_a_field_switched_off_is_neither_drawn_nor_spoken(self):
        h = Header(tone="standard", notes=("Two notes.",))
        self.assertIn("motto", self.drawn(SB.section, h, DAY, True, False))
        self.assertIn("description", self.drawn(SB.section, h, DAY, True, False))
        quiet = h.with_(off=frozenset({"motto", "notes", "description", "tagline"}))
        said = self.drawn(SB.section, quiet, DAY, True, False)
        self.assertFalse({"motto", "description", "tagline"} & said, said)
        self.assertNotIn("Drawn, never fetched", SB.section(quiet, DAY, True, False))

    def test_a_long_title_takes_two_lines_on_a_phone_and_the_band_grows(self):
        long = Header(tone="standard", title="An Extraordinarily Long Repository Name")
        size, rows = SB._title(long.caps, 360 - 97 - 40, 17, 12)
        self.assertEqual(len(rows), 2)
        short = SB.section(Header(tone="standard"), DAY, False, False)
        tall = SB.section(long, DAY, False, False)
        band = r'<rect x="0" y="0" width="[\d.]+" height="(\d+)" fill="#000000"/>'
        self.assertGreater(int(re.search(band, tall).group(1)), int(re.search(band, short).group(1)))

    def test_night_draws_its_labels_in_charcoal_on_black_paper(self):
        h, _ = CONTENTS["profile"]
        svg = SB.sheet(h, DARK, True, False)
        self.assertIn('fill="#000000" stroke="#3A414A"', svg, "the paper, with its charcoal hairline")
        self.assertIn('fill="#3A414A"', svg, "the band")


class Footers(unittest.TestCase):
    def test_without_closing_words_the_way_up_joins_the_badges(self):
        ft = Footer(tone="standard", closing="")
        P.PAIRS.clear()
        svg = SB.title_block(ft, DAY, True, False)
        self.assertIn("back to top label", {what for _, _, what in P.PAIRS})
        self.assertNotIn("closing", {what for _, _, what in P.PAIRS})
        self.assertIn(f'fill="{PALETTE["cobalt"]}"', svg)

    def test_the_attribution_says_only_what_is_on(self):
        ft = Footer(tone="standard", off=frozenset({"license"}))
        runs = SB._runs(ft)
        self.assertEqual([r[0] for r in runs], ["BUILT WITH", "UPDATED 2026-09-25"])

    def test_a_phone_stacks_the_way_up_under_the_words(self):
        ft = Footer(tone="standard")
        svg = SB.scale_bar(ft, DAY, False, False)
        self.assertRegex(svg, r'<rect x="0" y="\d+" width="360" height="32" fill="' + PALETTE["cobalt"] + '"/>')

    def test_a_link_carries_its_icon(self):
        from domain.palette import ICONS
        self.assertIn(ICONS["tag"], SB.link("Releases", DAY))
        self.assertIn(ICONS["link"], SB.link("Somewhere Else", DAY))


class Dispatch(unittest.TestCase):
    def test_standard_is_drawn_here_and_a_print_by_its_own_design(self):
        h, _ = CONTENTS["repository"]
        design = DESIGNS["H2"]
        self.assertIn("markdown-kit v1 standard H2 day", render(design, h)["header-day.svg"])
        self.assertNotIn("standard", render(design, h.with_(tone="blueprint"))["header-day.svg"].split("-->")[0])

    def test_the_same_files_in_every_theme(self):
        for code, design in DESIGNS.items():
            h, f = CONTENTS["repository"]
            content = h if design.kind == "header" else f
            self.assertEqual(set(render(design, content)), set(render(design, content.with_(tone="blueprint"))), code)


class EveryElement(unittest.TestCase):
    """The driftmark specimen's every element, in every variant and both themes."""

    def test_every_file_is_well_formed_linted_deterministic_and_the_prints_files(self):
        files = ED.render(ELEMENTS, "standard")
        self.assertEqual(set(files), set(ED.render(ELEMENTS, "blueprint")))
        again = ED.render(ELEMENTS, "standard")
        for eid, d in ELEMENTS.items():
            kind = d["kind"]
            for variant in E.variants(kind, d):
                for theme in ("day", "dark"):
                    name = ED.file_name(eid, variant, theme)
                    svg = files[name]
                    minidom.parseString(svg)
                    self.assertEqual(svg, again[name], name)
                    self.assertIn("<!--markdown-kit v1 standard elements ", svg, name)
                    self.assertEqual(lint(svg, budget=BUDGET[E.KINDS[kind][2]]), [], name)
                    w = int(re.search(r'width="(\d+)"', svg).group(1))
                    wanted = (404 if kind == "placard" or variant == "half" or
                              (variant == "narrow" and kind in ("roster", "certificate"))
                              else 360 if variant == "narrow" else 830)
                    self.assertEqual(w, wanted, name)

    def test_every_letter_holds_4_5_against_its_ground(self):
        P.PAIRS.clear()
        ED.render(ELEMENTS, "standard")
        for fill, ground, what in P.PAIRS:
            self.assertGreaterEqual(P.contrast(fill, ground), 4.5, (fill, ground, what))

    def test_the_half_page_pair_is_drawn_level(self):
        files = ED.render(ELEMENTS, "standard")
        heights = {re.search(r'height="(\d+)"', files[f"{eid}-day.svg"]).group(1) for eid in ("contributors", "conformance")}
        self.assertEqual(len(heights), 1)

    def test_a_placard_is_one_height_whatever_it_says(self):
        d = dict(ELEMENTS["action"])
        short = SE.draw("placard", dict(d, desc="Short."), "day", "wide")
        long = SE.draw("placard", dict(d, desc="A description long enough to take every one of the three lines a "
                                              "placard gives it, and then some more words after that."), "day", "wide")
        self.assertEqual(re.search(r'height="(\d+)"', short).group(1), re.search(r'height="(\d+)"', long).group(1))

    def test_a_check_not_met_is_crossed_and_counted(self):
        d = dict(ELEMENTS["conformance"], checks=[["Licensed", "LICENSE", True], ["Security policy", "none", False]])
        P.PAIRS.clear()
        svg = SE.draw("certificate", d, "day", "wide")
        from domain.palette import ICONS
        self.assertIn(ICONS["cross"], svg)
        self.assertIn(PALETTE["crimson"], svg)

    def test_the_drawings_that_must_survive_odd_data_do(self):
        cyc = {"kind": "schematic", "subject": "x/y",
               "boxes": {"a": {"title": "A", "path": "a"}, "b": {"title": "B"}, "c": {"title": "C", "path": "c"}},
               "wires": [["a", "b", "ONE"], ["b", "c", "TWO"], ["c", "a", "BACK"]]}
        patches = {"kind": "milestones", "subject": "x/y", "today": "2026-09-27",
                   "events": [{"date": "2026-09-20", "tag": "V1.6.1", "major": False},
                              {"date": "2026-09-26", "tag": "V1.6.2", "major": False}]}
        nothing = {"kind": "milestones", "subject": "x/y", "today": "2026-09-27", "events": []}
        for d in (cyc, patches, nothing):
            for variant in ("wide", "narrow"):
                minidom.parseString(SE.draw(d["kind"], d, "day", variant))

    def test_a_character_the_face_lacks_is_spelled_plainly_or_marked(self):
        E.WARNINGS.clear()
        d = dict(ELEMENTS["action"], desc="Arrows → and 漢")
        SE.draw("placard", d, "day", "wide")
        self.assertEqual(E.WARNINGS, ["sans cannot letter '漢'"])

    def test_every_wire_stays_on_the_card(self):
        own = loads((support.ROOT / ".github" / "markdown.yaml").read_text(encoding="utf-8"))
        kit = ED.merged(ED.check(own["elements"]), {}, subject="tannergolden/markdown")["how-it-runs"]
        for d in (ELEMENTS["how-it-runs"], kit):
            for variant, w in (("wide", 830), ("narrow", 360)):
                svg = SE.draw("schematic", d, "day", variant)
                for path in re.findall(r'<path d="([^"]+)" fill="none" stroke="#[0-9A-F]{6}" stroke-width="1.8"', svg):
                    xs = [float(x) for x in re.findall(r"[MLQ ]?(-?[\d.]+) -?[\d.]+", path)]
                    self.assertTrue(xs and all(0 < x < w - 4 for x in xs), (variant, path))

    def test_a_note_too_long_for_a_phone_wraps_evenly(self):
        lines = SE._note_lines("Optional: a page that says nothing is drawn from GitHub", 360 - 40 - 24)
        self.assertGreater(len(lines), 1)
        self.assertTrue(all(width(line, "sans-bold", 8.5, .8) <= 360 - 40 - 24 for line in lines))

    def test_a_phone_puts_the_box_that_goes_on_last_in_its_layer(self):
        edges = [("a", "b"), ("a", "c"), ("c", "d")]
        for keys in (["a", "b", "c", "d"], ["a", "c", "b", "d"]):
            self.assertEqual(SE.phone_order(keys, edges), ["a", "b", "c", "d"], keys)
        d = {"kind": "schematic", "subject": "x/y", "boxes": {k: {"title": k.upper(), "path": k} for k in "acbd"},
             "wires": [list(e) for e in edges]}
        svg = SE.draw("schematic", d, "day", "narrow")
        wires = re.findall(r'<path d="([^"]+)" fill="none" stroke="#[0-9A-F]{6}" stroke-width="1.8"', svg)
        self.assertEqual(len(wires), 3)
        self.assertEqual(sum("Q" in w for w in wires), 1, "only a to c goes round, down the channel")

    def test_a_long_subject_keeps_its_name_in_the_band(self):
        text, size, mw, _ = SE._band(360, "schematic", "an-organisation-with-a-long-name/and-a-long-repository", "")
        self.assertEqual(text, "AND-A-LONG-REPOSITORY")
        self.assertLessEqual(20 + 26 + 90 + mw, 360 + 20)


if __name__ == "__main__":
    unittest.main()
