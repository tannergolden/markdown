# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Every element, every variant, every theme and print: well formed, within budget, deterministic, and doing
what each drawing promises. The data is the driftmark specimen's."""
from __future__ import annotations

import datetime as dt
import re
import unittest
import xml.dom.minidom as minidom

from tests import support

from domain.canvas import BUDGET, lint
from domain.elements import data as ED
from domain.elements import draw as E
from domain.elements import layout as L
from domain.prints import PRINTS
from infra.yaml_reader import loads

support.install()
SPECIMEN = support.ROOT / "tests" / "fixtures" / "driftmark"
SETTINGS = loads((SPECIMEN / ".github" / "markdown.yaml").read_text(encoding="utf-8"))
SECTION = ED.check(SETTINGS["elements"])
ELEMENTS = ED.merged(SECTION, {}, subject="driftmark/driftmark")
# The banned dashes, spelled by code point so this file never carries one.
DASHES = ("–", "—", "―")


class EveryFile(unittest.TestCase):
    """The specimen's every element in every variant, theme and print."""

    def test_every_variant_and_theme_is_well_formed_within_budget_and_deterministic(self):
        for eid, d in ELEMENTS.items():
            kind = d["kind"]
            for variant in E.variants(kind, d):
                for theme in ("day", "dark"):
                    svg = E.draw(kind, d, "blueprint", theme, variant)
                    minidom.parseString(svg)
                    self.assertEqual(svg, E.draw(kind, d, "blueprint", theme, variant), (eid, variant, theme))
                    self.assertIn('role="img"', svg)
                    self.assertNotIn("<text", svg, "lettering must be paths")
                    self.assertEqual(lint(svg, budget=BUDGET[E.KINDS[kind][2]]), [], (eid, variant, theme))
                    for ch in DASHES:
                        self.assertNotIn(ch, svg)

    def test_every_print_draws_every_element(self):
        for tone in PRINTS:
            for eid, d in ELEMENTS.items():
                svg = E.draw(d["kind"], d, tone, "day", "wide")
                self.assertEqual(lint(svg, budget=BUDGET[E.KINDS[d["kind"]][2]]), [], (eid, tone))

    def test_narrow_files_are_phone_wide_and_wide_files_page_wide(self):
        for eid, d in ELEMENTS.items():
            kind = d["kind"]
            for variant in E.variants(kind, d):
                w = int(re.search(r'width="(\d+)"', E.draw(kind, d, "blueprint", "day", variant)).group(1))
                if variant == "narrow":
                    self.assertLessEqual(w, 404, (eid, variant))
                elif variant in ("wide", "still") and kind != "placard":
                    self.assertEqual(w, 830, (eid, variant))

    def test_night_lettering_follows_the_print(self):
        d = ELEMENTS["how-it-runs"]
        self.assertIn("#000000", E.draw("schematic", d, "orangeprint", "dark", "wide"))
        self.assertNotIn("#000000", E.draw("schematic", d, "blueprint", "dark", "wide"))

    def test_the_specimen_is_24_files(self):
        self.assertEqual(len(ED.render(ELEMENTS, "blueprint")), 24)


class Elements(unittest.TestCase):
    """Behaviours the drawings promise."""

    def test_a_character_no_face_has_is_spelled_plainly_or_marked(self):
        E.WARNINGS.clear()
        # The mono face has an ellipsis; it has no arrow and no accented e, which get their plain spellings.
        self.assertEqual(E.plain("done … → next é", "mono"), "done … -> next e")
        self.assertEqual(E.WARNINGS, [])
        self.assertEqual(E.plain("漢", "mono"), "?")
        self.assertTrue(E.WARNINGS)

    def test_counters_show_every_digit(self):
        d = dict(ELEMENTS["vitals"], counters=[["TESTS", 2241], ["A", 7], ["B", 12345]])
        svg = E.draw("instruments", d, "blueprint", "day", "wide")
        # Four digits get four cells; a five-digit count is shown in thousands.
        self.assertEqual(len(re.findall(r'<rect x="\d+" y="252" width="18" height="28" rx="2"', svg)), 4 + 3 + 3)
        self.assertEqual(lint(svg, budget=BUDGET["sheet"]), [])

    def test_schematic_wires_never_cross_a_box(self):
        d = ELEMENTS["how-it-runs"]
        boxes = [L.Box(k) for k in d["boxes"]]
        edges = [(a, b) for a, b, *_ in d["wires"]]
        L.snake(boxes, edges, left=46, top=118, width=738, per_row=3, box_w=224, box_h=52, gap_x=72, gap_y=64)
        by = {b.key: b for b in boxes}
        for a, b, *_ in d["wires"]:
            pts = L.route(by[a], by[b], 72, boxes)
            for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                self.assertFalse(L._crosses(x0, y0, x1, y1, boxes, (a, b)), (a, b, pts))

    def test_the_first_row_sits_under_the_title_unless_a_group_needs_the_room(self):
        def first_row(boxes: dict) -> float:
            d = {"kind": "schematic", "subject": "x/y", "boxes": boxes, "groups": {"g": "GROUP"},
                 "wires": [["a", "b", "ONE"], ["b", "c", "TWO"], ["c", "d", "THREE"]]}
            svg = E.draw("schematic", d, "blueprint", "day", "wide")
            return min(float(y) for y in re.findall(r'<rect x="[\d.]+" y="([\d.]+)" width="[\d.]+" height="52" rx="3"', svg))
        plain = {k: {"title": k.upper(), "path": k} for k in "abcd"}
        self.assertEqual(first_row(plain), 78)
        self.assertEqual(first_row(dict(plain, d=dict(plain["d"], **{"in": "g"}))), 78)
        self.assertEqual(first_row(dict(plain, b=dict(plain["b"], **{"in": "g"}))), 96)

    def test_a_schematic_with_a_cycle_still_draws(self):
        cyc = {"kind": "schematic", "subject": "x/y",
               "boxes": {"a": {"title": "A", "path": "a"}, "b": {"title": "B", "path": "b"}, "c": {"title": "C", "path": "c"}},
               "wires": [["a", "b", "ONE"], ["b", "c", "TWO"], ["c", "a", "BACK"]]}
        for variant in ("wide", "narrow"):
            minidom.parseString(E.draw("schematic", cyc, "blueprint", "day", variant))
        self.assertEqual(L.layers(["a", "b", "c"], [("a", "b"), ("b", "c"), ("c", "a")]), {"a": 0, "b": 1, "c": 2})

    def test_a_history_of_patch_releases_alone_still_draws_its_newest_on_a_phone(self):
        d = {"kind": "milestones", "subject": "x/y", "today": "2026-09-27",
             "events": [{"date": "2026-09-20", "tag": "V1.6.1", "major": False},
                        {"date": "2026-09-26", "tag": "V1.6.2", "major": False}]}
        for variant in ("wide", "narrow"):
            svg = E.draw("milestones", d, "blueprint", "day", variant)
            minidom.parseString(svg)
            self.assertEqual(lint(svg, budget=BUDGET["sheet"]), [], variant)
        planned = dict(d, events=d["events"] + [{"date": "2026-10-30", "tag": "V1.7.0", "major": False, "next": True}])
        minidom.parseString(E.draw("milestones", planned, "blueprint", "day", "narrow"))

    def test_timeline_cuts_only_a_quiet_stretch_and_keeps_the_scale_monotonic(self):
        s = L.timeline(dt.date(2026, 7, 22), dt.date(2026, 10, 8),
                       [dt.date(2026, 7, 25), dt.date(2026, 7, 27), dt.date(2026, 9, 24)], 46, 784)
        self.assertEqual(len(s.breaks), 1)
        xs = [s.x(dt.date(2026, 7, 22) + dt.timedelta(days=i)) for i in range(0, 78, 3)]
        self.assertEqual(xs, sorted(xs))
        dates = [E._date(e["date"]) for e in SECTION["history"]["events"]]
        s2 = L.timeline(dt.date(2025, 3, 1), dt.date(2026, 12, 15), dates, 46, 784)
        self.assertEqual(s2.breaks, [], "fourteen releases over eighteen months leave nothing quiet enough to cut")

    def test_alt_text_comes_from_the_data(self):
        self.assertTrue(E.alt("schematic", ELEMENTS["how-it-runs"]).startswith("Schematic of driftmark"))
        self.assertEqual(E.alt("placard", {"alt": "The card"}), "The card")

    def test_a_ring_shrinks_to_fit_its_arc(self):
        d = dict(ELEMENTS["conformance"], ring_top="A VERY MUCH LONGER RING OF LETTERING THAN THE ARC HAS ROOM FOR")
        self.assertEqual(lint(E.draw("certificate", d, "blueprint", "day", "wide"), budget=BUDGET["sheet"]), [])

    def test_a_check_that_is_not_met_is_drawn_as_not_met(self):
        d = {"checks": [["Licensed", "LICENSE", True], ["Security policy", "none", False], ["By hand", "a claim"]],
             "ring_top": "RING", "ring_bottom": "V1", "name": "X", "subject": "x/y"}
        svg = E.draw("certificate", d, "blueprint", "day", "wide")
        self.assertIn("not met: Security policy", svg)
        self.assertEqual(lint(svg, budget=BUDGET["sheet"]), [])

    def test_half_page_elements_on_one_page_stand_at_one_height(self):
        roster, cert = ELEMENTS["contributors"], ELEMENTS["conformance"]
        alone = {k: E.draw(d["kind"], d, "blueprint", "day", "half") for k, d in (("roster", roster), ("cert", cert))}
        heights = {k: int(re.search(r'height="(\d+)"', svg).group(1)) for k, svg in alone.items()}
        self.assertNotEqual(heights["roster"], heights["cert"], "the pair differ on their own, which is the point")
        shared = E.half_height(ELEMENTS)
        self.assertEqual(shared, max(heights.values()))
        files = ED.render(ELEMENTS, "blueprint")
        self.assertEqual(re.search(r'height="(\d+)"', files["contributors-day.svg"]).group(1),
                         re.search(r'height="(\d+)"', files["conformance-day.svg"]).group(1))
        self.assertIsNone(E.half_height({"a": {"kind": "placard"}}), "a page with no half elements shares nothing")


class Settings(unittest.TestCase):
    def test_true_or_nothing_names_no_elements(self):
        self.assertEqual(ED.check(True), {})
        self.assertEqual(ED.check(None), {})

    def test_the_shape_is_checked(self):
        for bad, words in (("yes", "expected false, or a map"), ({"How It Fits": {"kind": "schematic"}}, "kebab-case"),
                           ({"a": ["schematic"]}, "a map with its kind"), ({"a": {"title": "x"}}, "a map with its kind")):
            with self.assertRaisesRegex(ED.ElementsError, words):
                ED.check(bad)

    def test_a_retired_kind_is_named_precisely(self):
        for eid, kind, release in (("layout", "plan", "1.3.0"), ("stamp", "seal", "1.4.0")):
            errors = ED.validate({eid: {"kind": kind, "measure": {}}}, {})
            self.assertEqual(len(errors), 1, kind)
            self.assertIn(f"{kind} element was retired in banners v{release}", errors[0])

    def test_bad_data_is_named_precisely(self):
        broken = dict(SECTION)
        schematic = dict(broken["how-it-runs"])
        schematic["wires"] = schematic["wires"][:-1] + [["collector", "alarms", "PAST THE THRESHOLD"]]
        broken["how-it-runs"] = schematic
        broken["contributors"] = dict(broken["contributors"], kind="rooster")
        errors = " ".join(ED.validate(broken, {}))
        self.assertIn("names a box that is not there: alarms", errors)
        self.assertIn("unknown kind 'rooster'", errors)

    def test_what_is_measured_fills_what_the_settings_leave_out_and_never_wins(self):
        section = {"vitals": {"kind": "instruments", "caption": "MINE", "measure": {}}}
        measured = {"vitals": {"caption": "MEASURED", "histogram": {}, "dial": {}, "materials": {}, "counters": []}}
        d = ED.merged(section, measured, subject="a/b", today="2026-09-25")["vitals"]
        self.assertEqual((d["caption"], d["subject"], d["today"], "measure" in d), ("MINE", "a/b", "2026-09-25", False))
        self.assertEqual(ED.validate(section, {}), ["vitals: a instruments needs histogram, dial, materials, counters "
                                                    "(a run measures them)"])


if __name__ == "__main__":
    unittest.main()
