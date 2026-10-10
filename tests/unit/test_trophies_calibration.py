# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Every threshold and rarity pinned to a share of a reference population, and the sampler that measures it."""
from __future__ import annotations

import unittest

from tests import support

from app import calibrate
from domain.trophies import art
from domain.trophies import calibration as cal
from domain.trophies import catalogue as c
from infra import github, resources

support.install()


class Coverage(unittest.TestCase):
    def test_every_achievement_has_a_share_and_nothing_else_does(self):
        for mode, ach in (("profile", c.ACH), ("repository", c.RACH)):
            self.assertEqual(set(cal.SHARE[mode]), {a.slug for a in ach}, mode)
            for a in ach:
                self.assertEqual(len(cal.shares(mode, a.slug)), len(a.tiers), a.slug)
                self.assertIn(cal.basis(mode, a.slug), cal.BASIS_NAMES)

    def test_every_core_has_anchors_on_its_steps(self):
        for mode, cores in (("profile", c.CORE), ("repository", c.RCORE)):
            for core in cores:
                pts, b, note = cal.CORE_PCT[(mode, core.key)]
                self.assertEqual(tuple(x for x, _ in pts), tuple(core.steps), core.key)
                shares = [p for _, p in pts]
                self.assertEqual(shares, sorted(shares, reverse=True), core.key)
                self.assertIn(b, cal.BASIS_NAMES)
                self.assertTrue(note)


class RarityFollowsTheShare(unittest.TestCase):
    def test_bands(self):
        self.assertEqual([cal.rarity_of(x) for x in (100, 40, 39.9, 15, 14.9, 4, 3.9, 1, 0.9, 0)],
                         [1, 1, 2, 2, 3, 3, 4, 4, 5, 5])

    def test_every_rarity_in_the_catalogue_is_its_share_banded_and_never_rises(self):
        for mode, ach in (("profile", c.ACH), ("repository", c.RACH)):
            for a in ach:
                sh = cal.shares(mode, a.slug)
                self.assertEqual(a.rarities, tuple(cal.rarity_of(x) for x in sh), a.slug)
                self.assertEqual(list(sh), sorted(sh, reverse=True), a.slug)


class TheChip(unittest.TestCase):
    def test_measured_followers(self):
        f = next(k for k in c.CORE if k.key == "followers")
        self.assertAlmostEqual(art.top_pct(f, 25), 57.96)
        self.assertAlmostEqual(art.top_pct(f, 1000), 3.35)
        self.assertEqual(art.top_pct(f, 0), 100.0)
        self.assertTrue(29.03 < art.top_pct(f, 50) < 57.96)
        self.assertTrue(art.top_pct(f, 100000) < 0.2)
        self.assertGreaterEqual(art.top_pct(f, 10**9), 0.001)

    def test_modes_that_share_a_key_read_their_own_anchors(self):
        pc = next(k for k in c.CORE if k.key == "commits")
        rc = next(k for k in c.RCORE if k.key == "commits")
        self.assertNotEqual(art.top_pct(pc, 500), art.top_pct(rc, 500))

    def test_label_formats(self):
        self.assertEqual([art.pct_label(p) for p in (57.96, 3.35, 1.0, 0.081, 0.001)],
                         ["TOP 58%", "TOP 3.4%", "TOP 1%", "TOP 0.081%", "TOP 0.001%"])


class Sampler(unittest.TestCase):
    def test_a_link_header_gives_the_count(self):
        link = ('<https://api.github.com/repositories/1/commits?per_page=1&page=2>; rel="next", '
                '<https://api.github.com/repositories/1/commits?per_page=1&page=1234>; rel="last"')
        self.assertEqual(github.link_last(link), 1234)
        self.assertIsNone(github.link_last(""))

    def test_band_queries(self):
        self.assertEqual(calibrate.band_query(10, 99), "stars:10..99")
        self.assertEqual(calibrate.band_query(10000, None), "stars:>=10000")
        self.assertEqual((calibrate.BANDS[0][0], calibrate.BANDS[-1][1]), (1, None))

    def test_stratified_shares_weight_by_band_and_never_rise(self):
        bands = [{"weight": 0.9, "repos": [{"commits": 5}, {"commits": 150}]},
                 {"weight": 0.1, "repos": [{"commits": 3000}]},
                 {"weight": 0.5, "repos": []}]  # an empty band contributes nothing and takes no weight
        self.assertEqual(calibrate.estimate(bands, {"commits": (100, 500, 2000, 5000)})["commits"],
                         [[100, 55.0], [500, 10.0], [2000, 10.0], [5000, 0.0]])
        noisy = [{"weight": 1.0, "repos": [{"commits": 600}, {"commits": None}]}]
        self.assertEqual(calibrate.estimate(noisy, {"commits": (100, 500)})["commits"], [[100, 100.0], [500, 100.0]])

    def test_exact_shares_from_the_population_counts(self):
        pop = {"base": 1000, "stars": {"10": 250, "100": 40, "500": 45}}
        self.assertEqual(calibrate.exact_shares(pop, "stars", (10, 100, 500)), [[10, 25.0], [100, 4.0], [500, 4.0]])

    def test_the_measured_keys_are_repository_cores(self):
        self.assertTrue(set(calibrate.MEASURED) <= {x.key for x in c.RCORE})
        self.assertNotIn("active", calibrate.MEASURED, "active days cannot be read from the API")


class HandedIn(unittest.TestCase):
    def sample(self, cores):
        return {"date": "2026-10-01", "base": 38000000, "n": 200,
                "bands": [{"band": "1-9", "weight": 0.9, "population": 1, "sampled": 40}], "cores": cores}

    def tearDown(self):
        support.install()

    def test_no_sample_leaves_the_estimates(self):
        cal.use(None)
        self.assertEqual(cal.CORE_PCT, cal.ESTIMATED)
        self.assertEqual(cal.CORE_PCT[("repository", "stars")][1], "e")

    def test_matching_steps_are_measured_and_the_rest_keep_their_estimates(self):
        stars = next(x for x in c.RCORE if x.key == "stars")
        anchors = [[t, p] for t, p in zip(stars.steps, (9.0, 1.2, 0.3, 0.05, 0.01))]
        cal.use(self.sample({"stars": {"anchors": anchors},
                             "commits": {"anchors": [[1, 50.0], [2, 40.0]]},  # not the catalogue's steps: stale
                             "nonsense": {"anchors": [[1, 1.0]]}}))
        pts, basis, note = cal.CORE_PCT[("repository", "stars")]
        self.assertEqual((basis, pts), ("m", tuple((int(t), float(p)) for t, p in anchors)))
        self.assertIn("2026-10-01", note)
        self.assertEqual(cal.CORE_PCT[("repository", "commits")][1], "e")
        self.assertNotIn(("repository", "nonsense"), cal.CORE_PCT)
        self.assertEqual(cal.ESTIMATED[("repository", "stars")][1], "e", "the estimates are never touched")

    def test_the_committed_sample_is_handed_in_on_every_run(self):
        sample = resources.repository_sample()
        self.assertIsNotNone(sample, "calibrate has run and its file is committed")
        self.assertEqual(cal.REPOSITORY_SAMPLE, sample)
        self.assertEqual(sample["n"], sum(b["sampled"] for b in sample["bands"]))
        for key in calibrate.MEASURED:
            self.assertEqual(cal.CORE_PCT[("repository", key)][1], "m", key)
        self.assertEqual(cal.CORE_PCT[("repository", "active")][1], "e")


if __name__ == "__main__":
    unittest.main()
