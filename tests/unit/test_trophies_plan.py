# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The case's settings, its ledger, its README block, and what a commit says about it."""
from __future__ import annotations

import datetime as dt
import json
import unittest

from tests import support

from app.parts import trophies as part
from domain.trophies import block as B
from domain.trophies import catalogue as c
from domain.trophies import ledger
from domain.trophies import plan as P
from domain.trophies import sample
from domain.trophies import settings as TS

support.install()


def result(mode: str = "profile") -> dict:
    return json.loads(json.dumps(sample.SAMPLES[mode]))


def planned(section: dict | None = None, mode: str = "profile", owners: dict | None = None) -> dict:
    r = result(mode)
    r["owners"] = owners or {}
    return P.plan(r, TS.check(section or {}), folder="assets/markdown/trophies", base="assets/markdown/trophies")


class Settings(unittest.TestCase):
    def test_the_defaults(self):
        cfg = TS.check(None)
        self.assertEqual((cfg["style"], cfg["case"], cfg["embed"], cfg["banner"], cfg["block"]),
                         ("trophy", "both", "picture", True, True))
        self.assertEqual(TS.check(True), cfg)

    def test_the_documented_shapes(self):
        cfg = TS.check({"style": "crest", "core": ["stars", "forks"], "enamel": {"stars": "amber"}, "card": "rank",
                        "scan-pages": 5, "private": "true"})
        self.assertEqual((cfg["core"], cfg["enamel"], cfg["card"], cfg["scan_pages"], cfg["private"]),
                         (["stars", "forks"], {"stars": "amber"}, ["rank"], 5, True))

    def test_what_is_wrong_is_named(self):
        for bad, why in (({"colour": "red"}, "unknown key 'colour'"), ({"style": "neon"}, "style: 'neon'"),
                         ({"core": ["nonsense"]}, "not a core trophy"), ({"card": ["glow"]}, "card: 'glow'"),
                         ({"scan_pages": -1}, "whole number"), ({"achievements": 3}, "all, none or a list"),
                         ({"ledger": False}, "set lock at the top"), ({"mode": "profile"}, "set mode at the top"),
                         ({"theme": "fragment"}, "called embed"), ({"readme": "none"}, "called block"), ("x", "expected false")):
            with self.assertRaisesRegex(TS.TrophiesSettingsError, why, msg=repr(bad)):
                TS.check(bad)

    def test_a_trophy_of_the_other_mode_is_named_when_the_case_is_drawn(self):
        cfg = TS.check({"core": ["stars", "forks"]})  # forks is a repository's trophy
        self.assertEqual(TS.for_mode(cfg, "repository"), [])
        self.assertIn("'forks' is not a profile trophy", TS.for_mode(cfg, "profile")[0])
        with self.assertRaisesRegex(P.TrophiesError, "not a profile trophy"):
            part.plan(result("profile") | {"owners": {}}, cfg, out="assets/markdown", readme="README.md")


class Ledger(unittest.TestCase):
    def test_a_new_ribbon_for_seven_days_then_quiet(self):
        led = ledger.new()
        today = dt.date(2026, 9, 24)
        self.assertTrue(ledger.update(led, result(), c.CORE, c.ACH, today)["new"]["commits"])
        self.assertFalse(ledger.update(led, result(), c.CORE, c.ACH, today + dt.timedelta(days=8))["new"]["commits"])

    def test_history_is_sparse_and_the_weekly_change_reads_it(self):
        led = ledger.new()
        r = result()
        d0 = dt.date(2026, 9, 1)
        ledger.update(led, r, c.CORE, c.ACH, d0)
        ledger.update(led, r, c.CORE, c.ACH, d0 + dt.timedelta(days=1))
        self.assertEqual(len(led["history"]["commits"]), 1, "a value that did not move writes nothing")
        r["values"]["commits"] += 50
        self.assertEqual(ledger.update(led, r, c.CORE, c.ACH, d0 + dt.timedelta(days=8))["delta"]["commits"], 50)

    def test_remember_keeps_what_check_needs_and_nothing_else(self):
        r = result()
        r["scan"] = {"huge": "cache"}
        led = {}
        ledger.remember(led, r)
        self.assertTrue(set(ledger.last(led)) <= set(ledger.LAST_KEYS))
        self.assertNotIn("scan", ledger.last(led))
        self.assertIsNone(ledger.last({}))

    def test_the_trophies_kits_lock_is_taken_over_without_its_scan(self):
        old = {"version": 1, "reached": {"commits": {"3.0": "2026-01-02"}}, "history": {"commits": {"2026-01-02": 2400}},
               "scan": {"octo/x": {"head": "abc"}}, "snapshot": "2026-09-01", "last": {"mode": "profile"}}
        self.assertEqual(part.adopt(json.dumps(old)), {"reached": old["reached"], "history": old["history"], "scan": {}})
        self.assertIsNone(part.adopt(None))
        self.assertIsNone(part.adopt("not json"))


class ReachedToday(unittest.TestCase):
    def test_a_tier_lost_to_a_raised_threshold_is_not_named(self):
        cores = [next(k for k in c.CORE if k.key == "followers")]
        today = dt.date(2026, 9, 24)
        r = {"values": {"followers": 13}, "curs": {}}
        led = {"reached": {"followers": {"1.0": "2026-09-24"}}}  # Bronze recorded when it was 10; it is 25 now
        self.assertEqual(ledger.reached_on(led, r, cores, [], today)["tiers"], [])
        r["values"]["followers"] = 30
        self.assertEqual(ledger.reached_on(led, r, cores, [], today)["tiers"], [("Bronze", "Followers")])

    def test_a_second_run_on_one_day_names_only_what_it_reached_itself(self):
        record = ledger.new()
        section = TS.check({})
        day = dt.date(2026, 9, 27)
        first = part.fold(record, result(), section, day)
        self.assertIn(("Platinum", "Commits"), first["tiers"])
        self.assertTrue(first["achievements"])
        moved = result()
        moved["values"]["commits"] += 13  # still Platinum
        self.assertEqual(part.fold(record, moved, section, day), {"tiers": [], "achievements": []})
        crossed = result()
        crossed["values"]["followers"] = 100  # from Bronze to Silver
        self.assertEqual(part.fold(record, crossed, section, day), {"tiers": [("Silver", "Followers")], "achievements": []})
        self.assertEqual(record["last"]["values"]["followers"], 100, "the record keeps what the case is drawn from")


class Block(unittest.TestCase):
    def test_picture_is_the_default_and_fragment_still_exists(self):
        self.assertIn("<picture>", planned()["block"])
        self.assertNotIn("#gh-dark-mode-only", planned()["block"])
        self.assertIn("#gh-dark-mode-only", planned({"embed": "fragment"})["block"])

    def test_it_sits_on_the_kits_markers_and_every_card_links_to_its_entry(self):
        block = planned()["block"]
        self.assertTrue(block.startswith("<!-- markdown:trophies:start -->\n<p align=\"center\">"))
        self.assertTrue(block.endswith("</sub></p>\n<!-- markdown:trophies:end -->"))
        self.assertIn(f'href="{B.CATALOGUE}#profile-commits"', block)
        self.assertIn(f'href="{B.CATALOGUE}#profile-polyglot"', block)
        self.assertIn(f'href="{B.CATALOGUE}#profile">the catalogue</a>', block)
        self.assertIn("https://github.com/tannergolden/markdown/blob/HEAD/docs/Catalogue.md", block)
        self.assertIn('srcset="assets/markdown/trophies/commits.svg"', block)

    def test_a_case_that_shows_no_achievements_has_no_drawer_and_counts_none(self):
        p = planned({"achievements": "none"})
        self.assertNotIn("<details>", p["block"])
        self.assertTrue(P.describe(p).startswith("trophies commits "), P.describe(p))
        self.assertIn("The case stands with commits at", P.news(p, result(), {}, None)[0].replace("\n", " "))
        self.assertIn("<details>", planned()["block"])

    def test_block_false_draws_the_files_and_leaves_the_readme(self):
        p = planned({"block": False})
        self.assertIsNone(p["block"])
        self.assertTrue(p["files"])


class Plan(unittest.TestCase):
    def test_owner_only_pins_appear_only_for_the_owner(self):
        self.assertEqual(planned()["total"], 100)
        p = planned(owners={a.only: "octo-dev" for a in c.ACH if a.only})
        self.assertEqual(p["total"], 104)
        self.assertIn("assets/markdown/trophies/achievements/trophy-maker.svg", p["files"])

    def test_a_core_subset_in_its_order_and_an_enamel(self):
        p = planned({"core": ["stars", "commits"], "enamel": {"stars": "crimson"}})
        self.assertEqual([k for k in ("stars", "commits", "pulls") if f"assets/markdown/trophies/{k}.svg" in p["files"]],
                         ["stars", "commits"])
        self.assertIn(c.PAL["crimson"], p["files"]["assets/markdown/trophies/stars.svg"])

    def test_one_case_draws_one_file_per_image(self):
        night, day = planned({"case": "night"})["files"], planned({"case": "day"})["files"]
        self.assertEqual({f.removesuffix(".svg") + "-day.svg" for f in night}, set(day))
        self.assertEqual(planned()["files"], {**night, **day})

    def test_every_file_passes_the_lint(self):
        for mode in ("profile", "repository"):
            for rel, svg in planned(mode=mode)["files"].items():
                self.assertEqual(P.lint(svg), [], rel)


class Commit(unittest.TestCase):
    def test_the_headline_prefers_a_tier_then_an_achievement_then_movement(self):
        self.assertEqual(P.headline({"tiers": [("Gold", "Stars Earned")], "achievements": ["Polyglot II"]}, {}, "octo"),
                         "reach Gold on Stars Earned")
        self.assertEqual(P.headline({"tiers": [], "achievements": ["Polyglot II"]}, {}, "octo"), "earn Polyglot II")
        self.assertEqual(P.headline({}, {"commits": 124, "stars": 9, "pulls": 3, "repos": 1}, "octo"),
                         "refresh the case, commits +124, stars +9, pulls +3")
        self.assertEqual(P.headline({}, {}, "octo"), "refresh the case for octo")

    def test_the_news_is_wrapped_and_names_what_moved(self):
        p = planned()
        r = result() | {"today": "2026-09-24"}
        paras = P.news(p, r, {"tiers": [("Platinum", "Commits")], "achievements": ["Polyglot II"]}, "7")
        text = "\n\n".join(paras)
        self.assertTrue(paras[0].startswith("Measured octo-dev on 2026-09-24 in run 7. The case stands at 56 of 100"),
                        paras[0])
        for part_ in ("Newly reached: Platinum on Commits.", "Newly earned: Polyglot II.", "Moved this week: "):
            self.assertIn(part_, text.replace("\n", " "))
        self.assertTrue(all(len(line) <= 72 for line in text.splitlines()))
        self.assertFalse(P.news(p, result(), {}, None)[0].startswith("Measured"), "the banners say it already")


if __name__ == "__main__":
    unittest.main()
