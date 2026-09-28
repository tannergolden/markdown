# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""How the page's theme draws the badges, what each says, and the README block the rows make."""
from __future__ import annotations

import datetime as dt
import re
import unittest

from tests import support

from domain.badges import classic as C
from domain.badges import data as BD
from domain.badges import live
from domain.badges import plates as P

support.install()
DAY = dt.date(2026, 9, 28)
STATUS = {"name": "status", "label": "Status", "message": "Active", "icon": "pulse", "message_color": "green",
          "link": "./"}
PLATE = {"name": "role", "label": "Role", "message": "Profile", "icon": "home", "style": "blueprint-for-the-badge",
         "print": "greenprint"}
CI = {"name": "ci", "label": "Standards CI", "icon": "check", "link": "https://example.com/?a=1&b=2",
      "measure": live.parse({"workflow": "self-checks.yml"})}
LAST = {"name": "last-commit", "label": "Last Commit", "icon": "commit", "measure": live.parse("last-commit")}
MEASURED = {"ci": live.value("Failing", "red"), "last-commit": live.value("This Month", "yellow")}


def plan(badges, measured=None, theme="standard", shade=None, day=DAY):
    return BD.plan(badges, MEASURED if measured is None else measured, theme=theme, shade=shade, today=day,
                   folder="assets/markdown/badges", base="assets/markdown/badges")


class Themes(unittest.TestCase):
    def test_in_standard_each_badge_is_drawn_as_written(self):
        files = plan([STATUS, PLATE, CI])["files"]
        self.assertEqual(sorted(files), ["assets/markdown/badges/dynamic/ci.svg",
                                         "assets/markdown/badges/static/role-dark.svg",
                                         "assets/markdown/badges/static/role.svg",
                                         "assets/markdown/badges/static/status.svg"])
        self.assertEqual(files["assets/markdown/badges/static/status.svg"],
                         C.render("Status", "Active", "black", "green", "pulse", "for-the-badge") + "\n")
        self.assertEqual(files["assets/markdown/badges/static/role-dark.svg"],
                         P.render_blueprint("Role", "Profile", "home", "blueprint-for-the-badge", "greenprint", True)
                         + "\n")
        self.assertEqual(files["assets/markdown/badges/dynamic/ci.svg"],
                         C.render("Standards CI", "Failing", "gold", "red", "check", "for-the-badge") + "\n")

    def test_in_a_print_every_badge_is_its_plate_in_that_print(self):
        files = plan([STATUS, PLATE, CI], theme="blackprint")["files"]
        self.assertEqual(sorted(files), ["assets/markdown/badges/dynamic/ci.svg",
                                         "assets/markdown/badges/static/role-dark.svg",
                                         "assets/markdown/badges/static/role.svg",
                                         "assets/markdown/badges/static/status-dark.svg",
                                         "assets/markdown/badges/static/status.svg"])
        reserve = ("Passing", "Failing", "No Data")
        self.assertEqual(files["assets/markdown/badges/static/status.svg"],
                         P.render_blueprint("Status", "Active", "pulse", "blueprint-for-the-badge", "blackprint")
                         + "\n", "a static badge is its plate in the page's print")
        self.assertEqual(files["assets/markdown/badges/static/role.svg"],
                         P.render_blueprint("Role", "Profile", "home", "blueprint-for-the-badge", "blackprint")
                         + "\n", "the page's print wins over a plate's own")
        self.assertEqual(files["assets/markdown/badges/dynamic/ci.svg"],
                         P.render_live("Standards CI", "Failing", "check", "blueprint-for-the-badge", "red", reserve)
                         + "\n", "a live badge is a live plate in its state's print, with room for every value")

    def test_a_plate_that_names_rainbowprint_follows_the_page(self):
        b = {**PLATE, "print": "rainbowprint"}
        on_teal = plan([b], shade="tealprint")["files"]
        self.assertEqual(on_teal, plan([{**PLATE, "print": "tealprint"}])["files"])
        self.assertEqual(plan([b])["files"], plan([{**PLATE, "print": "redprint"}])["files"])

    def test_a_repository_print_draws_the_badges_too(self):
        from domain import prints
        try:
            prints.use(support.install(), {"goldprint": {"line": "#B8860B", "ink": "#5C4400", "sheet": "#7A5B00"}})
            svg = plan([STATUS], theme="goldprint")["files"]["assets/markdown/badges/static/status.svg"]
            self.assertIn('stroke="#B8860B"', svg)
            self.assertEqual(BD.lint(svg), [])
        finally:
            prints.use(support.install())

    def test_a_plate_that_cannot_letter_a_badge_says_so(self):
        b = {"name": "kanji", "label": "Name", "message": "漢字"}
        self.assertTrue(plan([b])["files"], "a classic badge sets any character in the reader's font")
        with self.assertRaisesRegex(BD.BadgesError, "kanji: message '漢字'.*a print theme draws every badge as a plate"):
            plan([b], theme="blueprint")


class Says(unittest.TestCase):
    def test_a_badge_that_measures_shows_what_was_measured(self):
        p = plan([CI, LAST])
        self.assertEqual(p["says"], {"ci": "Failing", "last-commit": "This Month"})
        self.assertIn('alt="Last Commit: This Month"', p["block"])

    def test_until_it_is_measured_it_shows_no_data(self):
        p = plan([CI], measured={})
        self.assertEqual(p["says"], {"ci": "No Data"})
        self.assertIn("#57606A", p["files"]["assets/markdown/badges/dynamic/ci.svg"].upper(), "in slate")

    def test_a_black_label_measures_only_its_message(self):
        b = {**LAST, "label_color": "black", "message_color": "teal"}
        svg = plan([b])["files"]["assets/markdown/badges/static/last-commit.svg"]
        self.assertEqual(svg, C.render("Last Commit", "This Month", "black", "teal", "commit", "for-the-badge") + "\n")

    def test_a_rotating_colour_is_the_same_all_week_and_changes_with_it(self):
        b = {**STATUS, "message_color": "rotate"}
        monday, sunday, next_week = dt.date(2026, 9, 28), dt.date(2026, 10, 4), dt.date(2026, 10, 5)
        self.assertEqual(BD.week(monday), "2026W40")
        self.assertEqual(plan([b], day=monday)["files"], plan([b], day=sunday)["files"])
        colours = {BD.rotate("status", BD.week(monday + dt.timedelta(weeks=n))) for n in range(12)}
        self.assertGreater(len(colours), 1)
        self.assertTrue(colours <= set(C.STATIC_RANDOM_POOL))
        self.assertEqual(BD.rotate("status", "2026W40"), BD.rotate("status", "2026W40"))


class Block(unittest.TestCase):
    def test_static_badges_make_a_row_and_live_ones_a_row_under_it(self):
        block = plan([CI, STATUS, PLATE, LAST])["block"]
        self.assertTrue(block.startswith("<!-- markdown:badges:start -->\n<div align=\"center\">\n\n"))
        self.assertTrue(block.endswith("\n\n</div>\n<!-- markdown:badges:end -->"))
        rows = block.split("\n\n")[1:-1]
        self.assertEqual(len(rows), 2)
        self.assertEqual([re.findall(r'alt="([^"]+)"', row) for row in rows],
                         [["Status: Active", "Role: Profile"], ["Standards CI: Failing", "Last Commit: This Month"]])

    def test_a_plate_is_a_picture_and_a_link_is_kept_as_written(self):
        rows = plan([STATUS, PLATE, CI])["block"].split("\n\n")[1:-1]
        static = rows[0].splitlines()
        self.assertEqual(static[0], '<a href="./"><img alt="Status: Active" '
                                    'src="assets/markdown/badges/static/status.svg"></a>')
        self.assertEqual(static[1], '<picture><source media="(prefers-color-scheme: dark)" '
                                    'srcset="assets/markdown/badges/static/role-dark.svg"><img alt="Role: Profile" '
                                    'src="assets/markdown/badges/static/role.svg"></picture>', "no link, no anchor")
        self.assertIn('href="https://example.com/?a=1&amp;b=2"', rows[1])

    def test_no_badges_is_no_block(self):
        self.assertIsNone(plan([])["block"])
        self.assertEqual(plan([STATUS])["block"].count("\n\n"), 2, "one row")

    def test_alt_text_is_escaped(self):
        block = plan([{"name": "q", "label": 'Say "hi"', "message": "<b>"}])["block"]
        self.assertIn('alt="Say &quot;hi&quot;: &lt;b&gt;"', block)


if __name__ == "__main__":
    unittest.main()
