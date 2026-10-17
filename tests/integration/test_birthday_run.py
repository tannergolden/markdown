# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""A page through its birthday, run by run: the Birthday set goes up at the birthday's midnight, checks, and comes
down the day after, each change named in its commit; a person's birthday from the settings, a repository's from the
day GitHub created it, which the lock keeps; the birthday wins over a holiday's set for its day and hands it back;
and with the birthday off the set never goes up."""
from __future__ import annotations

import copy
import datetime as dt
import io
import unittest
from unittest import mock

from tests import support
from tests.fakes.github import FakeGitHub
from tests.integration import test_banners_run as B

from app import cli
from app.parts import banners as banners_part
from app.ports import Ports
from domain.banners import sample
from infra import files
from infra.yaml_reader import loads

HERE = "tannergolden/banners"


def run(argv: list[str], measurement: dict, created: str | None = "2025-10-17T12:00:00Z",
        zone: dt.tzinfo = dt.timezone.utc) -> tuple[int, str, FakeGitHub]:
    """The command line on real files, as `test_banners_run.run` runs it, with GitHub saying the repository was
    created at `created`, and the page's time zone `zone`."""
    out = io.StringIO()
    gh = FakeGitHub({}, paths={f"/repos/{HERE}": {"created_at": created}} if created else {})

    def measured(gh_, mode, subject, where, *, today):
        return copy.deepcopy(measurement) | {"today": today}

    ports = Ports(catalogue=support.install(), read_text=files.read_text, parse_yaml=loads,
                  today=lambda zone: dt.date(2026, 9, 25), write_text=files.write_text,
                  append_text=files.append_text, drawn=files.drawn, prune=files.prune, remove=files.remove,
                  github=lambda: gh, zone=lambda name: zone, env={"GITHUB_REPOSITORY": HERE}, out=out,
                  err=io.StringIO())
    with mock.patch.object(banners_part, "measure", measured):
        code = cli.main(argv, ports)
    return code, out.getvalue() + ports.err.getvalue(), gh


class Folder(B.Folder):
    measurement = sample.REPOSITORY
    created: str | None = "2025-10-17T12:00:00Z"
    zone: dt.tzinfo = dt.timezone.utc

    def day(self, when: str) -> tuple[int, str]:
        self.msg.unlink(missing_ok=True)
        code, out, self.gh = run(["run", "--root", str(self.root), "--today", when, "--commit-file", str(self.msg)],
                                 self.measurement, self.created, self.zone)
        return code, out

    def up(self) -> bool:
        return "<!--markdown-kit v1 birthday H2 day-->" in self.svg("header-day.svg")

    def message(self) -> str:
        return self.msg.read_text(encoding="utf-8")

    def checks(self) -> None:
        self.assertEqual(B.run(["check", "--root", str(self.root)])[0], 0)


class ARepository(Folder):
    def test_its_birthday_is_the_day_github_created_it_from_the_first_anniversary(self):
        code, out = self.day("2026-10-16")
        self.assertEqual(code, 0, out)
        self.assertFalse(self.up())
        self.assertEqual(self.lock()["drawn"]["born"], "2025-10-17")

        code, out = self.day("2026-10-17")
        self.assertEqual(code, 0, out)
        self.assertIn("in the Birthday set", out)
        self.assertTrue(self.up())
        self.assertIn("<!--markdown-kit v1 birthday F1 day-->", self.svg("footer-day.svg"))
        drawn = self.lock()["drawn"]
        self.assertEqual((drawn["holiday"], drawn["born"]), ("birthday", "2025-10-17"))
        msg = self.message()
        self.assertEqual(msg.splitlines()[0], "chore(markdown): \U0001F484 put up the Birthday set")
        self.assertIn(f"It is the 1st birthday of {HERE}", msg.replace("\n", " "))
        self.assertIn("tomorrow the page is drawn in blueprint again", msg.replace("\n", " "))
        self.checks()

        code, out = self.day("2026-10-18")
        self.assertEqual(code, 0, out)
        self.assertFalse(self.up())
        self.assertIsNone(self.lock()["drawn"]["holiday"])
        self.assertEqual(self.message().splitlines()[0], "chore(markdown): \U0001F484 take down the Birthday set")
        self.checks()

    def test_the_day_it_was_made_is_no_birthday(self):
        self.created = "2026-10-17T12:00:00Z"
        self.day("2026-10-17")
        self.assertFalse(self.up())

    def test_its_birthday_is_the_day_it_was_made_in_the_pages_zone(self):
        self.set("theme: blueprint\ntimezone: America/New_York\n")
        self.created = "2025-10-18T02:00:00Z"            # still the 17th in New York
        self.zone = dt.timezone(dt.timedelta(hours=-4))
        self.day("2026-10-17")
        self.assertTrue(self.up())
        self.assertEqual(self.lock()["drawn"]["born"], "2025-10-17")

    def test_with_the_birthday_off_nothing_is_asked_and_the_set_never_goes_up(self):
        self.set("theme: blueprint\nbirthday: false\n")
        self.day("2026-10-17")
        self.assertFalse(self.up())
        self.assertNotIn(f"/repos/{HERE}", [what for what, _ in self.gh.asked])
        self.assertNotIn("born", self.lock()["drawn"])

    def test_a_repository_may_not_name_another_day(self):
        self.set("theme: blueprint\nbirthday: 03-14\n")
        code, out = self.day("2026-03-14")
        self.assertEqual(code, 2, out)
        self.assertIn("the day GitHub created it", out)


class APerson(Folder):
    measurement = sample.PROFILE
    settings = "mode: profile\nsubject: tannergolden\ntheme: blueprint\nbirthday: 10-31\n"

    def test_their_birthday_takes_the_page_from_a_holiday_for_its_day_and_hands_it_back(self):
        self.day("2026-10-30")
        self.assertEqual(self.lock()["drawn"]["holiday"], "halloween")

        code, out = self.day("2026-10-31")
        self.assertEqual(code, 0, out)
        self.assertTrue(self.up())
        self.assertEqual(self.lock()["drawn"]["holiday"], "birthday")
        msg = self.message()
        self.assertEqual(msg.splitlines()[0], "chore(markdown): \U0001F484 put up the Birthday set")
        self.assertIn("It is @tannergolden's birthday", msg.replace("\n", " "))
        self.assertIn("tomorrow the page is drawn in the Halloween set", msg.replace("\n", " "))
        self.checks()

        self.day("2026-11-01")
        self.assertEqual(self.lock()["drawn"]["holiday"], "halloween")
        self.assertEqual(self.message().splitlines()[0], "chore(markdown): \U0001F484 put up the Halloween set")
        self.checks()

    def test_a_year_gives_their_age(self):
        self.set("mode: profile\nsubject: tannergolden\ntheme: blueprint\nbirthday: 1990-10-31\n")
        self.day("2026-10-31")
        self.assertTrue(self.up())
        self.assertIn("It is the 36th birthday of @tannergolden", self.message().replace("\n", " "))
        self.checks()

    def test_the_holidays_off_leave_the_birthday_on(self):
        self.set("mode: profile\nsubject: tannergolden\ntheme: blueprint\nbirthday: 10-31\nholidays: false\n")
        self.day("2026-10-31")
        self.assertTrue(self.up())
        self.day("2026-10-30")
        self.assertFalse(self.up())


if __name__ == "__main__":
    unittest.main()
