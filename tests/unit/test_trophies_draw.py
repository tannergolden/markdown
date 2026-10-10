# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The trophy case's drawings: the trophies kit's own, byte for byte, in every style, tier, case and state."""
from __future__ import annotations

import hashlib
import json
import re
import unittest
import xml.dom.minidom as minidom

from tests import support

from domain.trophies import art as A
from domain.trophies import catalogue as C
from domain.trophies import plan as P
from domain.trophies import sample as S
from domain.trophies import settings as TS

support.install()
GOLDEN = json.loads((support.ROOT / "tests" / "fixtures" / "trophies" / "golden.json").read_text(encoding="utf-8"))
VALUES = tuple(GOLDEN["values"])
OPTIONS = ({}, {"rank": True, "delta": 5, "new": True})


def digest(parts) -> str:
    d = hashlib.sha256()
    for p in parts:
        d.update(p.encode())
        d.update(b"\0")
    return d.hexdigest()


def sample(mode: str) -> dict:
    s = json.loads(json.dumps(S.SAMPLES[mode]))
    s["owners"] = {a.only: s["subject"].split("/")[0] for a in C.MODES[mode]["ach"] if a.only}
    return s


class TheTrophiesKitsOwn(unittest.TestCase):
    def test_every_card_is_drawn_as_the_trophies_kit_drew_it(self):
        for style, draw in A.STYLES.items():
            for case in ("night", "day"):
                for mode in ("profile", "repository"):
                    got = digest(draw(A.CASES[case], core, v, o)
                                 for core in C.MODES[mode]["core"] for v in VALUES for o in OPTIONS)
                    self.assertEqual(got, GOLDEN["groups"][f"card {style} {mode} {case}"], (style, mode, case))

    def test_every_pin_and_both_banner_cards_are_drawn_as_it_drew_them(self):
        for mode in ("profile", "repository"):
            s = S.SAMPLES[mode]
            m = C.MODES[mode]
            for case in ("night", "day"):
                th = A.CASES[case]
                self.assertEqual(digest(A.pin(th, a, cur) for a in m["ach"] for cur in (None, 0, a.tiers[0], a.tiers[-1])),
                                 GOLDEN["groups"][f"pins {mode} {case}"], (mode, case))
                foot = ("flame", "#E36209", "12-DAY STREAK", "  ·  LONGEST 43 DAYS")
                self.assertEqual(digest([A.level_card(th, m["core"], s["values"], m["ach"], s["curs"], s["subject"], foot)]),
                                 GOLDEN["groups"][f"level {mode} {case}"])
                self.assertEqual(digest([A.next_up_card(th, m["core"], s["values"], m["ach"], s["curs"])]),
                                 GOLDEN["groups"][f"next-up {mode} {case}"])

    def test_a_whole_case_is_planned_as_it_planned_it(self):
        for mode in ("profile", "repository"):
            planned = P.plan(sample(mode), TS.check({}), folder="assets/trophies", base="assets/trophies")
            names = sorted(planned["files"])
            got = digest([n.removeprefix("assets/trophies/") for n in names] + [planned["files"][n] for n in names])
            self.assertEqual(got, GOLDEN["groups"][f"case {mode}"], mode)


class Cards(unittest.TestCase):
    def test_every_style_is_well_formed_deterministic_and_passes_the_lint_in_both_cases(self):
        for style, draw in A.STYLES.items():
            for case in ("night", "day"):
                for v in (0, 1240, 640000):
                    svg = draw(A.CASES[case], C.CORE[0], v, {"rank": True, "delta": 3, "new": True})
                    minidom.parseString(svg)
                    self.assertEqual(svg, draw(A.CASES[case], C.CORE[0], v, {"rank": True, "delta": 3, "new": True}))
                    self.assertEqual(P.lint(svg), [], (style, case, v))

    def test_cards_declare_the_phone_size_on_the_design_viewbox(self):
        svg = A.STYLES["crest"](A.NIGHT, C.CORE[0], 1240)
        self.assertIn('width="164" height="222" viewBox="0 0 180 244"', svg)

    def test_no_external_references_and_no_text_elements(self):
        for style, draw in A.STYLES.items():
            svg = draw(A.DAY, C.CORE[0], 3610, {"rank": True})
            self.assertNotIn("<text", svg)
            self.assertNotRegex(svg, r'(?:href|src)="(?!#)')

    def test_glyphs_are_embedded_once_and_used(self):
        svg = A.STYLES["trophy"](A.NIGHT, C.CORE[0], 3610, {"rank": True})
        ids = re.findall(r'<path id="([smn]\d+)"', svg)
        self.assertEqual(len(ids), len(set(ids)))
        for i in ids:
            self.assertIn(f'href="#{i}"', svg)

    def test_alt_text_says_tier_value_and_progress(self):
        svg = A.STYLES["crest"](A.NIGHT, C.CORE[0], 3610, {"rank": True, "delta": 12, "new": True})
        alt = re.search(r'aria-label="([^"]+)"', svg).group(1)
        self.assertTrue(alt.startswith("Commits trophy: Gold, 3,610, "), alt)
        for part in ("% to Platinum", "top ", "up 12 this week", "newly reached"):
            self.assertIn(part, alt)

    def test_the_stamp_names_the_kit_and_the_case(self):
        self.assertIn("<!--markdown-kit v1 trophy night-->", A.STYLES["crest"](A.NIGHT, C.CORE[0], 1))
        self.assertIn("<!--markdown-kit v1 trophy day-->", A.STYLES["crest"](A.DAY, C.CORE[0], 1))

    def test_motion_starts_at_gold_and_stops_for_reduced_motion(self):
        silver = A.STYLES["trophy"](A.NIGHT, C.CORE[0], 2000 - 1)
        gold = A.STYLES["trophy"](A.NIGHT, C.CORE[0], 2000)
        self.assertNotIn("@keyframes", silver)
        self.assertIn("@keyframes", gold)
        self.assertIn("prefers-reduced-motion:reduce", gold)


class Pins(unittest.TestCase):
    def test_every_state_renders(self):
        for a in C.ACH + C.RACH:
            for cur in (None, 0, a.tiers[0], a.tiers[-1]):
                self.assertEqual(P.lint(A.pin(A.NIGHT, a, cur)), [], (a.slug, cur))

    def test_a_secret_shows_question_marks_until_earned(self):
        secret = next(a for a in C.ACH if a.secret)
        self.assertIn("Secret achievement", A.pin(A.NIGHT, secret, 0))
        self.assertNotIn("Secret achievement", A.pin(A.NIGHT, secret, secret.tiers[-1]))

    def test_a_tier_numeral_is_in_the_label(self):
        tiered = next(a for a in C.ACH if a.goals)
        self.assertIn(f'aria-label="{tiered.name} II: earned', A.pin(A.NIGHT, tiered, tiered.tiers[1]))


class BannerCards(unittest.TestCase):
    def test_a_long_subject_still_fits(self):
        m = C.MODES["repository"]
        s = S.SAMPLES["repository"]
        svg = A.level_card(A.NIGHT, m["core"], s["values"], m["ach"], s["curs"], "octo/an-extraordinarily-long-repository-name",
                           ("tag", "#1F9E8F", "NO RELEASE YET", ""))
        self.assertEqual(P.lint(svg), [])

    def test_next_up_skips_what_time_does_and_what_is_secret(self):
        items = A.next_up_items(C.CORE, S.PROFILE["values"], C.ACH, S.PROFILE["curs"], n=200)
        names = {i["name"] for i in items}
        for a in C.ACH:
            if a.passive or a.secret:
                self.assertFalse(any(n == a.name or n.startswith(a.name + " ") for n in names), a.name)


if __name__ == "__main__":
    unittest.main()
