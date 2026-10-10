# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""A run of the banners through the command line, on a real folder, with the measurement standing in for GitHub."""
from __future__ import annotations

import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests import support
from tests.fakes.github import FakeGitHub

from app import cli
from app.parts import banners as banners_part
from app.ports import Ports
from domain import prints
from domain.banners import plan, sample
from domain.banners import settings as banners_settings
from domain.palette import PALETTE
from infra import files

LOCK = Path(".github") / "markdown.lock.json"
SETTINGS = Path(".github") / "markdown.yaml"


def run(argv: list[str], measurement: dict | None = None, here: str = "tannergolden/banners") -> tuple[int, str]:
    """The command line on real files, with `measurement` standing in for GitHub, as it runs off a runner."""
    out = io.StringIO()

    def measured(gh, mode, subject, where, *, today):
        return copy.deepcopy(measurement) | {"today": today}

    ports = Ports(catalogue=support.install(), read_text=files.read_text, parse_yaml=__import__("infra.yaml_reader",
                  fromlist=["loads"]).loads, today=lambda zone: __import__("datetime").date(2026, 9, 25),
                  write_text=files.write_text, append_text=files.append_text, drawn=files.drawn, prune=files.prune,
                  remove=files.remove, github=lambda: FakeGitHub({}), env={"GITHUB_REPOSITORY": here}, out=out,
                  err=io.StringIO())
    with mock.patch.object(banners_part, "measure", measured):
        code = cli.main(argv, ports)
    return code, out.getvalue() + ports.err.getvalue()


class Folder(unittest.TestCase):
    """A temporary repository with a README, in the blueprint unless a test says otherwise."""

    settings = "theme: blueprint\n"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "README.md").write_text("# Banners\n\nWhat it draws.\n", encoding="utf-8")
        self.set(self.settings)
        self.msg = self.root.parent / f"{self.root.name}-commit.txt"

    def tearDown(self):
        self.tmp.cleanup()
        self.msg.unlink(missing_ok=True)
        support.install()

    def set(self, text: str) -> None:
        """The page's settings; these tests are the banners', so the trophy case is off unless a test says."""
        (self.root / SETTINGS).parent.mkdir(exist_ok=True)
        text += "" if "trophies" in text else "trophies: false\n"
        (self.root / SETTINGS).write_text(text, encoding="utf-8")

    def lock(self) -> dict:
        return json.loads((self.root / LOCK).read_text(encoding="utf-8"))

    def svg(self, name: str) -> str:
        return (self.root / "assets" / "banners" / name).read_text(encoding="utf-8")

    def first(self, measurement: dict = sample.REPOSITORY):
        return run(["run", "--root", str(self.root), "--today", "2026-09-25", "--commit-file", str(self.msg)],
                   measurement)


class Run(Folder):
    def test_first_run_draws_everything_and_places_both_blocks(self):
        code, out = self.first()
        self.assertEqual(code, 0, out)
        text = (self.root / "README.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("<!-- markdown:header:start -->"))
        self.assertIn("# Banners\n\nWhat it draws.\n\n<!-- markdown:footer:start -->", text)
        self.assertTrue(text.rstrip().endswith("<!-- markdown:footer:end -->"))
        drawn = sorted(p.name for p in (self.root / "assets" / "banners").iterdir())
        # The banners in a folder of their own, beside the other parts', and no folder named for the kit.
        self.assertFalse((self.root / "assets" / "markdown").exists())
        # Six header files, four footer files, and a day and a dark button for each of the four links.
        self.assertEqual(len(drawn), 18)
        lk = self.lock()
        self.assertEqual(lk["parts"]["banners"]["last"]["subject"], "tannergolden/banners")
        self.assertEqual((lk["snapshot"], lk["drawn"]["theme"]), ("2026-09-25", "blueprint"))
        msg = self.msg.read_text(encoding="utf-8")
        self.assertTrue(msg.startswith("chore(markdown): \U0001FAA7 draw the banners for tannergolden/banners\n\n"))
        self.assertIn("release v1.0.0, 0 stars", msg.replace("\n", " "))

    def test_a_page_that_sets_nothing_draws_the_section_and_reads_everything_from_github(self):
        self.set("# nothing to set\ntheme: blueprint\n")
        code, out = self.first()
        self.assertEqual(code, 0, out)
        self.assertIn("H2 Section and F1 Title block in blueprint", out)
        header, footer = self.svg("header-day.svg"), self.svg("footer-day.svg")
        self.assertIn("<!--markdown-kit v1 H2 day-->", header)
        self.assertIn("<!--markdown-kit v1 F1 day-->", footer)
        repo = sample.REPOSITORY["repository"]
        self.assertIn(f'<title id="t">{repo["name"]}</title>', header)
        self.assertIn(repo["description"], header)
        self.assertIn("Stars: 0.", header)
        self.assertIn("Last updated September 25, 2026.", footer)

    def test_a_quiet_day_writes_nothing(self):
        self.first()
        self.msg.unlink()
        code, out = run(["run", "--root", str(self.root), "--today", "2026-09-26", "--commit-file", str(self.msg)],
                        sample.REPOSITORY)
        self.assertEqual(code, 0)
        self.assertIn("nothing changed", out)
        self.assertFalse(self.msg.exists())

    def test_a_week_on_the_lock_is_written_to_keep_the_schedule_alive(self):
        self.first()
        _, out = run(["run", "--root", str(self.root), "--today", "2026-10-02"], sample.REPOSITORY)
        self.assertIn("1 files changed", out)
        self.assertEqual(self.lock()["snapshot"], "2026-10-02")

    def test_a_moved_figure_is_redrawn_and_named_in_the_commit(self):
        self.first()
        m = copy.deepcopy(sample.REPOSITORY)
        m["repository"]["stars"] = 1
        m["repository"]["release"] = "v1.1.0"
        run(["run", "--root", str(self.root), "--today", "2026-09-26", "--commit-file", str(self.msg)], m)
        msg = self.msg.read_text(encoding="utf-8")
        self.assertEqual(msg.splitlines()[0], "chore(markdown): \U0001FAA7 redraw with release v1.1.0 and 1 star")
        self.assertIn("release v1.1.0 (was v1.0.0)", msg.replace("\n", " "))

    def test_check_passes_on_what_run_wrote_and_fails_on_a_hand_edit(self):
        self.first()
        self.assertEqual(run(["check", "--root", str(self.root)])[0], 0)
        svg = self.root / "assets" / "banners" / "header-day.svg"
        svg.write_text(svg.read_text(encoding="utf-8").replace("Stars: 0.", "Stars: 9,999."), encoding="utf-8")
        code, out = run(["check", "--root", str(self.root)])
        self.assertEqual(code, 1)
        self.assertIn("header-day.svg (differs)", out)

    def test_check_fails_on_a_drifted_block_and_changed_settings(self):
        self.first()
        path = self.root / "README.md"
        path.write_text(path.read_text(encoding="utf-8").replace("Back to Top", "Up"), encoding="utf-8")
        self.assertIn("footer block differs", run(["check", "--root", str(self.root)])[1])
        self.first()
        self.set("theme: brownprint\n")
        self.assertEqual(run(["check", "--root", str(self.root)])[0], 1)

    def test_a_design_set_to_none_takes_its_files_and_block_away(self):
        self.first()
        self.set("theme: blueprint\nbanners:\n  footer: none\n")
        run(["run", "--root", str(self.root), "--today", "2026-09-26"], sample.REPOSITORY)
        names = [p.name for p in (self.root / "assets" / "banners").iterdir()]
        self.assertFalse([n for n in names if n.startswith(("footer-", "link-"))])
        self.assertNotIn("markdown:footer", (self.root / "README.md").read_text(encoding="utf-8"))
        self.assertEqual(run(["check", "--root", str(self.root)])[0], 0)

    def test_banners_turned_off_take_everything_away(self):
        self.first()
        self.set("theme: blueprint\nbanners: false\n")
        run(["run", "--root", str(self.root), "--today", "2026-09-26"], sample.REPOSITORY)
        self.assertFalse((self.root / "assets" / "banners").exists(), "the folder goes with the last of its files")
        self.assertEqual((self.root / "README.md").read_text(encoding="utf-8"), "# Banners\n\nWhat it draws.\n")

    def test_a_file_drawn_by_hand_is_never_removed(self):
        self.first()
        hand = self.root / "assets" / "banners" / "logo.svg"
        hand.write_text("<svg><!-- mine --></svg>", encoding="utf-8")
        self.set("theme: blueprint\nbanners:\n  footer: none\n")
        run(["run", "--root", str(self.root), "--today", "2026-09-26"], sample.REPOSITORY)
        self.assertTrue(hand.exists())

    def test_bad_settings_fail_with_the_key_named(self):
        self.set("banners:\n  figures: [followers]\n")
        code, out = self.first()
        self.assertEqual(code, 2)
        self.assertIn("figures", out)

    def test_the_old_kits_markers_move_over_on_the_first_run(self):
        (self.root / "README.md").write_text(
            "<!-- banners:header:start -->\nold\n<!-- banners:header:end -->\n\n# Banners\n\n"
            "<!-- banners:footer:start -->\nold\n<!-- banners:footer:end -->\n", encoding="utf-8")
        self.first()
        text = (self.root / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("banners:header", text)
        self.assertEqual(text.count("<!-- markdown:header:start -->"), 1)
        self.assertEqual(text.count("<!-- markdown:footer:start -->"), 1)
        self.assertEqual(run(["check", "--root", str(self.root)])[0], 0)


class Rainbow(Folder):
    """rainbowprint: each update is drawn in the next colour of the spectrum, and a quiet day keeps its colour."""

    settings = "theme: rainbowprint\n"

    def run_on(self, day: str, stars: int) -> str:
        m = copy.deepcopy(sample.REPOSITORY)
        m["repository"]["stars"] = stars
        self.msg.unlink(missing_ok=True)
        run(["run", "--root", str(self.root), "--today", day, "--commit-file", str(self.msg)], m)
        self.assertEqual(run(["check", "--root", str(self.root)])[0], 0)
        return self.lock()["drawn"]["rainbow"]

    def drawn_in(self, token: str) -> bool:
        return PALETTE[token] in self.svg("header-day.svg")

    def test_each_update_takes_the_next_colour_and_a_quiet_day_keeps_it(self):
        self.assertEqual(self.run_on("2026-09-25", 1284), "redprint")
        self.assertTrue(self.drawn_in(prints.PRINTS["redprint"]["line"]))
        self.assertIn("colour 1 of 9; the next update will be the orangeprint",
                      self.msg.read_text(encoding="utf-8").replace("\n", " "))
        self.assertEqual(self.run_on("2026-09-26", 1284), "redprint")
        self.assertFalse(self.msg.exists())
        self.assertEqual(self.run_on("2026-09-27", 1285), "orangeprint")
        self.assertTrue(self.drawn_in(prints.PRINTS["orangeprint"]["line"]))
        self.assertFalse(self.drawn_in(prints.PRINTS["redprint"]["line"]))

    def test_the_spectrum_wraps_round(self):
        self.run_on("2026-09-25", 1284)
        lk = self.lock()
        lk["drawn"]["rainbow"] = "pinkprint"
        (self.root / LOCK).write_text(json.dumps(lk), encoding="utf-8")
        run(["render", "--root", str(self.root)])
        self.assertEqual(self.run_on("2026-09-26", 1300), "redprint")

    def test_a_weekly_snapshot_is_not_an_update(self):
        self.run_on("2026-09-25", 1284)
        self.assertEqual(self.run_on("2026-10-02", 1284), "redprint")


class Preview(unittest.TestCase):
    def test_a_preview_folder_checks_like_a_real_one(self):
        for mode in ("repository", "profile"):
            with tempfile.TemporaryDirectory() as tmp:
                self.assertEqual(run(["preview", "--root", tmp, "--input", f"mode={mode}"])[0], 0)
                self.assertEqual(run(["check", "--root", tmp, "--input", f"mode={mode}"])[0], 0)


class TopLink(unittest.TestCase):
    """The footer is always the way back to the top of the README."""

    def blocks(self, **given) -> dict:
        cfg = {**banners_settings.check(given), "theme": "blueprint", "out": "assets", "readme_path": "README.md"}
        return plan.plan(copy.deepcopy(sample.REPOSITORY), cfg, draw=False)["blocks"]

    def assertLinksTheImage(self, footer: str):
        # The link opens on a line of its own and nothing inside it is blank,
        # so Markdown reads it as one HTML block, with the image inside it.
        start = footer.index('<a href="#top">\n<picture>\n')
        body = footer[start:footer.index("</picture>\n</a>", start)]
        self.assertNotIn("\n\n", body)
        self.assertIn('src="assets/banners/footer-day.svg"', body)

    def test_the_whole_footer_links_to_the_anchor_in_the_header(self):
        blocks = self.blocks()
        self.assertLinksTheImage(blocks["footer"])
        self.assertIn('<a name="top"></a>', blocks["header"])

    def test_hiding_the_words_keeps_the_way_back(self):
        self.assertLinksTheImage(self.blocks(hide=["top"])["footer"])

    def test_with_no_header_the_top_is_still_there(self):
        blocks = self.blocks(header="none")
        self.assertLinksTheImage(blocks["footer"])
        self.assertIn('<a name="top"></a>', blocks["header"])
        self.assertNotIn("<picture>", blocks["header"])

    def test_with_no_footer_nothing_is_added(self):
        self.assertEqual(self.blocks(header="none", footer="none"), {})


class Prints(Folder):
    """A repository's own prints, under `prints:` in its settings, draw the banners in its own colours."""

    settings = ("theme: goldprint\nprints:\n  goldprint: {label: Goldprint, line: '#B8860B', ink: '#5C4400', "
                "sheet: '#7A5B00'}\n")

    def test_a_repository_print_draws_the_banners_in_its_own_colours(self):
        code, out = self.first()
        self.assertEqual(code, 0, out)
        self.assertIn("#B8860B", self.svg("header-day.svg"))
        self.assertIn("#7A5B00", self.svg("header-dark.svg"))
        self.assertEqual(run(["check", "--root", str(self.root)])[0], 0, "and check draws it the same way")

    def test_the_stub_can_name_a_repository_print(self):
        self.set("prints:\n  goldprint: {line: '#B8860B', ink: '#5C4400', sheet: '#7A5B00'}\n")
        code, out = run(["run", "--root", str(self.root), "--today", "2026-09-25", "--input", "theme=goldprint"],
                        sample.REPOSITORY)
        self.assertEqual(code, 0, out)
        self.assertIn("#5C4400", self.svg("header-day.svg"))

    def test_a_print_nobody_defined_points_at_prints(self):
        self.set("theme: goldprint\n")
        code, out = self.first()
        self.assertEqual(code, 2)
        self.assertIn("under prints", out)


class Section(unittest.TestCase):
    def test_unknown_keys_and_values_fail_loudly(self):
        for given in ({"colour": "navy"}, {"hide": ["repo"]}, {"figures": ["nope"]}, {"links": ["no bar"]},
                      {"header": "cover"}, {"notes": ["a", "b", "c"]}):
            with self.assertRaises(banners_settings.BannersError, msg=given):
                banners_settings.check(given)

    def test_a_page_setting_in_the_section_says_where_it_goes(self):
        with self.assertRaisesRegex(banners_settings.BannersError, "theme is the page's"):
            banners_settings.check({"theme": "redprint"})

    def test_a_checked_section_checks_again_unchanged(self):
        cfg = banners_settings.check({"links": {"Docs": "docs/"}, "hide": ["motto"]})
        self.assertEqual(banners_settings.check(cfg), cfg)

    def test_what_the_old_kit_set_aside_is_still_set_aside(self):
        self.assertEqual(banners_settings.check({"emoji": "\U0001FAB5", "hide": ["emoji", "divider", "motto"]}),
                         banners_settings.check({"hide": ["motto"]}))


if __name__ == "__main__":
    unittest.main()
