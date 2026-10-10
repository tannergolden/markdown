# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The case's rules: the catalogue's promises, the tier arithmetic, the calendar, and what a commit says."""
from __future__ import annotations

import datetime as dt
import unittest

from tests import support

from domain.palette import ICONS as SHARED_ICONS
from domain.palette import PALETTE
from domain.trophies import calendar as cal
from domain.trophies import catalogue as c
from domain.trophies.scan import CONVENTIONAL, EMOJI, SEMVER, classify, empty_stats, merge_stats, without_refreshes

support.install()
D = dt.date


def days(*spans):
    """{date: 1} from (start, length) spans."""
    out = {}
    for start, n in spans:
        for i in range(n):
            out[start + dt.timedelta(days=i)] = 1
    return out


class Catalogue(unittest.TestCase):
    def test_exactly_one_hundred_public_achievements_a_mode(self):
        self.assertEqual(len([a for a in c.ACH if not a.only]), 100)
        self.assertEqual(len([a for a in c.RACH if not a.only]), 100)

    def test_the_owner_only_entries_name_the_repositories_that_draw_and_rule_the_page(self):
        self.assertEqual({a.only for a in c.ACH if a.only},
                         {"tannergolden/markdown", "tannergolden/standards", "tannergolden/path"})

    def test_slugs_are_unique_and_url_safe(self):
        for ach in (c.ACH, c.RACH):
            slugs = [a.slug for a in ach]
            self.assertEqual(len(slugs), len(set(slugs)))
            for s in slugs:
                self.assertRegex(s, r"^[a-z0-9]+(-[a-z0-9]+)*$")

    def test_every_icon_and_token_exists(self):
        for a in c.ACH + c.RACH:
            self.assertIn(a.icon, c.ICONS, a.name)
            self.assertIn(a.tok, c.PAL, a.name)
        for core in c.CORE + c.RCORE:
            self.assertIn(core.icon, c.ICONS)
            self.assertIn(core.tok, c.PAL)

    def test_the_colours_and_icons_are_the_kits_own(self):
        self.assertTrue(all(c.PAL[k] == PALETTE[k] for k in c.PAL))
        own = {k for k in c.ICONS if k not in SHARED_ICONS or c.ICONS[k] != SHARED_ICONS[k]}
        self.assertEqual(own, {"pull", "issue", "q", "tick", "check"})
        self.assertEqual(c.ICONS["tick"], SHARED_ICONS["check"], "the case's tick is the kit's check")

    def test_tiered_entries_have_one_rarity_per_tier(self):
        for a in c.ACH + c.RACH:
            self.assertEqual(len(a.tiers), len(a.rarities), a.name)
            self.assertEqual(list(a.tiers), sorted(a.tiers), a.name)

    def test_eight_core_trophies_with_rising_thresholds(self):
        for cores in (c.CORE, c.RCORE):
            self.assertEqual(len(cores), 8)
            for core in cores:
                self.assertEqual(list(core.steps), sorted(core.steps))

    def test_the_catalogue_page_is_written_from_this_catalogue(self):
        from domain.trophies import catalogue_md
        page = (support.ROOT / "docs" / "Catalogue.md").read_text(encoding="utf-8")
        self.assertEqual(page, catalogue_md.page(), "docs/Catalogue.md is stale: run make catalogue")

    def test_every_achievement_has_a_line_in_its_modes_measurer(self):
        # The measurers need GitHub to run, so this reads their source: a slug
        # never written there is one a live run would refuse.
        parts = support.SRC / "app" / "parts" / "trophies"
        for name, ach in (("profile.py", c.ACH), ("repository.py", c.RACH)):
            src = (parts / name).read_text(encoding="utf-8")
            self.assertEqual([a.slug for a in ach if f'"{a.slug}"' not in src], [], name)


class TierMaths(unittest.TestCase):
    def test_measure_walks_the_tiers(self):
        core = c.CORE[0]  # commits: 100, 500, 2000, 5000, 10000
        self.assertEqual(c.measure(core, 0)["t"], 0)
        self.assertEqual(c.measure(core, 99)["next"], "Bronze")
        self.assertEqual(c.measure(core, 100)["t"], 1)
        self.assertEqual(c.measure(core, 3610)["t"], 3)
        self.assertAlmostEqual(c.measure(core, 3610)["pct"], (3610 - 2000) / 3000)

    def test_stars_past_diamond_double_each_time(self):
        core = c.CORE[0]
        self.assertEqual(c.measure(core, 10000)["stars"], 0)
        self.assertEqual(c.measure(core, 20000)["stars"], 1)
        self.assertEqual(c.measure(core, 23500)["next"], "star 2")
        self.assertEqual(c.measure(core, 320000)["stars"], 5)
        self.assertIsNone(c.measure(core, 320000)["next"])

    def test_an_achievement_earns_its_tiers(self):
        poly = next(a for a in c.ACH if a.name == "Polyglot")  # 5, 10, 20
        st = c.ach_state(poly, 12)
        self.assertTrue(st["earned"])
        self.assertEqual((st["k"], st["tier"], st["next_tier"], st["next"]), (2, "II", "III", 20))
        self.assertEqual(st["rarity"], poly.rarities[1])
        self.assertFalse(st["done"])
        self.assertTrue(c.ach_state(poly, 20)["done"])
        self.assertFalse(c.ach_state(poly, 4)["earned"])

    def test_unmeasured_is_not_earned_and_a_secret_stays_one(self):
        secret = next(a for a in c.ACH if a.secret)
        st = c.ach_state(secret, None)
        self.assertFalse(st["measured"])
        self.assertTrue(st["secret"])
        self.assertFalse(c.ach_state(secret, 1)["secret"], "earned, it is revealed")


class Calendar(unittest.TestCase):
    def test_streaks(self):
        self.assertEqual(cal.longest_streak(days((D(2026, 1, 1), 5), (D(2026, 2, 1), 9))), 9)
        self.assertEqual(cal.longest_streak({}), 0)
        d = days((D(2026, 9, 20), 4))  # 20..23
        self.assertEqual(cal.current_streak(d, D(2026, 9, 24)), 4, "today may not be over yet")
        self.assertEqual(cal.current_streak(d, D(2026, 9, 23)), 4)
        self.assertEqual(cal.current_streak(d, D(2026, 9, 26)), 0)

    def test_gaps_and_comebacks(self):
        d = days((D(2025, 1, 1), 1), (D(2025, 5, 1), 1))
        self.assertTrue(cal.came_back_after(d, 90))
        self.assertFalse(cal.came_back_after(d, 365))

    def test_months_seasons_weekends_and_weekdays(self):
        self.assertEqual(cal.perfect_months(days((D(2026, 2, 1), 28))), 1)
        self.assertFalse(cal.all_twelve_months(days((D(2026, 2, 1), 28))))
        year = days((D(2026, 1, 1), 365))
        self.assertTrue(cal.all_twelve_months(year))
        self.assertEqual(cal.max_days_in_a_year(year), 365)
        self.assertGreaterEqual(cal.weekends_in_a_year(year), 52)
        self.assertGreaterEqual(cal.weekdays_in_a_year(year), 260)

    def test_every_week_of_a_completed_year_only(self):
        self.assertTrue(cal.every_week_of_a_year(days((D(2025, 1, 1), 365)), D(2026, 9, 24)))
        self.assertFalse(cal.every_week_of_a_year(days((D(2026, 1, 1), 265)), D(2026, 9, 24)))

    def test_special_dates(self):
        d = {D(2024, 2, 29): 1, D(2026, 1, 1): 1, D(2026, 2, 13): 1}
        self.assertTrue(cal.on_date(d, 2, 29))
        self.assertTrue(cal.on_date(d, 1, 1))
        self.assertTrue(cal.on_friday_13th(d))
        self.assertTrue(cal.on_anniversary(d, D(2020, 1, 1)))
        self.assertFalse(cal.on_anniversary(d, D(2026, 1, 1)))

    def test_runs_and_maxima(self):
        self.assertEqual(cal.consecutive_weeks(cal.weeks_of(days((D(2026, 1, 5), 70)))), 10)
        self.assertEqual(cal.consecutive_months({(2026, 1), (2026, 2), (2026, 4)}), 2)
        d = {D(2026, 3, 2): 40, D(2026, 3, 3): 70, D(2026, 3, 10): 5}
        self.assertEqual((cal.max_in_a_day(d), cal.max_in_a_week(d), cal.max_in_a_month(d)), (70, 110, 115))


class Commits(unittest.TestCase):
    def test_message_patterns(self):
        self.assertTrue(CONVENTIONAL.match("feat(scope)!: add"))
        self.assertTrue(CONVENTIONAL.match("fix: it"))
        self.assertFalse(CONVENTIONAL.match("Fixed it"))
        self.assertTrue(EMOJI.match("\U0001F389 initialise"))
        self.assertTrue(EMOJI.match(":tada: initialise"))
        self.assertTrue(SEMVER.match("v1.2.3"))
        self.assertTrue(SEMVER.match("2.0.0-rc.1"))
        self.assertFalse(SEMVER.match("v1"))

    def test_classify_counts_what_it_should(self):
        st = empty_stats()
        classify({"message": "fix: \U0001F41B squash", "author": {"date": "2026-03-01T03:12:00-05:00", "user": {"login": "octo"}},
                  "signature": {"isValid": True}, "authors": {"totalCount": 2}, "changedFilesIfAvailable": 1,
                  "additions": 900, "deletions": 200}, st)
        classify({"message": "Revert \"fix\"", "author": {"date": "2026-03-01T00:00:00Z", "user": None, "name": "bot"},
                  "signature": None, "authors": {"totalCount": 1}, "changedFilesIfAvailable": 60, "additions": 1,
                  "deletions": 1}, st)
        self.assertEqual((st["total"], st["conventional"], st["fix"], st["emoji"], st["signed"], st["coauthored"]),
                         (2, 1, 1, 0, 1, 1))
        self.assertEqual((st["onefile"], st["heavy"], st["sweeping"], st["night"], st["midnight"], st["revert"]),
                         (1, 1, 1, 2, 1, 1))
        self.assertEqual(st["days"], ["2026-03-01"])
        self.assertEqual(st["authors"], {"octo": 1, "bot": 1})

    def test_every_kits_refresh_is_set_aside(self):
        st = empty_stats()
        for scope in ("markdown", "trophies", "banners", "badges", "elements"):
            classify({"message": f"chore({scope}): refresh", "author": {"date": "2026-03-02T00:00:00Z",
                                                                        "user": {"login": "tannergolden"}},
                      "changedFilesIfAvailable": 220, "additions": 5000, "deletions": 5000}, st)
        classify({"message": "feat: real work", "author": {"date": "2026-03-02T09:00:00Z", "user": {"login": "tannergolden"}},
                  "changedFilesIfAvailable": 1, "additions": 1, "deletions": 0}, st)
        self.assertEqual((st["refresh"], st["total"], st["midnight"], st["sweeping"], st["heavy"]), (5, 1, 0, 0, 0))
        self.assertEqual(st["refresh_days"], {"2026-03-02": 5})
        self.assertEqual(st["authors"], {"tannergolden": 1})
        merged = merge_stats([{"stats": st}, {"stats": st}])
        self.assertEqual((merged["refresh"], merged["refresh_days"]), (10, {"2026-03-02": 10}))
        self.assertEqual(without_refreshes({D(2026, 3, 2): 12, D(2026, 3, 3): 1}, merged),
                         {D(2026, 3, 2): 2, D(2026, 3, 3): 1})
        self.assertEqual(without_refreshes({D(2026, 3, 2): 2}, merged), {}, "a day left at zero is no active day")


if __name__ == "__main__":
    unittest.main()
