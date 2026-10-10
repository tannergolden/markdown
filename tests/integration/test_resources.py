# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
import datetime as dt
import unittest

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


if __name__ == "__main__":
    unittest.main()
