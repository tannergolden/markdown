# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
import datetime as dt
import unittest
import zoneinfo
from unittest import mock

from tests import support

from domain import lettering, prints
from infra import clock, resources


class ResourcesTest(unittest.TestCase):
    def test_install_hands_the_domain_its_outlines_and_prints(self):
        catalogue = support.install()
        self.assertEqual(set(lettering.fonts()), {"serif", "meta", "num", "mono", "sans", "sans-bold"})
        self.assertEqual(tuple(catalogue), prints.BUILTIN)
        for face in lettering.fonts().values():
            self.assertGreater(len(face["g"]), 60)
            self.assertTrue(all(isinstance(g[0], str) and g[1] >= 0 for g in face["g"].values()))

    def test_every_font_ships_with_its_licence(self):
        for name in ("OFL-Cinzel.txt", "OFL-Barlow-Condensed.txt", "OFL-JetBrains-Mono.txt"):
            text = (resources.FONTS / name).read_text(encoding="utf-8")
            self.assertIn("SIL Open Font License", text, name)
        text = (resources.FONTS / "Bitstream-Vera-DejaVu-Sans.txt").read_text(encoding="utf-8")
        self.assertIn("Bitstream Vera Fonts Copyright", text)
        self.assertIn("DejaVu changes are in public domain", text)

    def test_the_catalogue_uses_only_palette_tokens(self):
        from domain.palette import PALETTE
        for name, spec in resources.catalogue().items():
            for k in ("line", "ink", "sheet", "night"):
                if k in spec:
                    self.assertIn(spec[k], PALETTE, f"{name}.{k}")


class ClockTest(unittest.TestCase):
    def test_the_day_is_taken_in_the_pages_zone(self):
        moment = dt.datetime(2026, 10, 30, 3, 0, tzinfo=dt.timezone.utc)
        self.assertEqual(clock.today("UTC", moment), dt.date(2026, 10, 30))
        self.assertEqual(clock.today("America/New_York", moment), dt.date(2026, 10, 29))
        self.assertEqual(clock.today("Asia/Tokyo", dt.datetime(2026, 12, 31, 16, 0, tzinfo=dt.timezone.utc)),
                         dt.date(2027, 1, 1))

    def test_an_unknown_zone_is_a_setting_to_fix(self):
        with self.assertRaises(ValueError):
            clock.today("Mars/Olympus_Mons")

    def without_legacy(self):
        """A zone database with the canonical names only, the way Ubuntu 26.04 installs it."""
        real = zoneinfo.ZoneInfo

        def lookup(key):
            if key in clock.FIXED or key in clock.CANONICAL:
                raise zoneinfo.ZoneInfoNotFoundError(f"No time zone found with key {key}")
            return real(key)
        return mock.patch("zoneinfo.ZoneInfo", side_effect=lookup)

    def test_a_legacy_fixed_zone_is_its_offset_where_the_database_left_it_out(self):
        winter = dt.datetime(2026, 11, 2, 4, 30, tzinfo=dt.timezone.utc)
        summer = dt.datetime(2026, 7, 1, 4, 30, tzinfo=dt.timezone.utc)
        with self.without_legacy():
            est = clock.zone("EST")
            self.assertEqual(clock.today("EST", winter), dt.date(2026, 11, 1))
            self.assertEqual(clock.today("EST", summer), dt.date(2026, 6, 30))
            self.assertEqual(clock.zone("MST").utcoffset(None), dt.timedelta(hours=-7))
            self.assertEqual(clock.zone("HST").utcoffset(None), dt.timedelta(hours=-10))
        self.assertEqual(est.utcoffset(None), dt.timedelta(hours=-5))
        self.assertEqual(winter.astimezone(est).tzname(), "EST")

    def test_a_legacy_alias_with_daylight_saving_is_its_canonical_zone(self):
        summer = dt.datetime(2026, 7, 1, 4, 30, tzinfo=dt.timezone.utc)
        with self.without_legacy():
            self.assertEqual(clock.zone("US/Eastern"), zoneinfo.ZoneInfo("America/New_York"))
            self.assertEqual(clock.zone("PST8PDT"), zoneinfo.ZoneInfo("America/Los_Angeles"))
            # EDT, UTC-4 in July, puts 04:30 UTC past midnight, where EST would not.
            self.assertEqual(clock.today("EST5EDT", summer), dt.date(2026, 7, 1))

    def test_every_canonical_zone_the_aliases_name_exists(self):
        for alias, name in clock.CANONICAL.items():
            self.assertIsInstance(zoneinfo.ZoneInfo(name), zoneinfo.ZoneInfo, alias)

    def test_an_unknown_zone_says_an_old_alias_may_be_missing(self):
        with self.assertRaisesRegex(clock.ClockError, "tzdata-legacy"):
            clock.zone("Asia/Calcutta_Nowhere")


if __name__ == "__main__":
    unittest.main()
