# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The `badges:` section: its two shapes, every rule a badge is held to, what `measure:` accepts, and `set`."""
from __future__ import annotations

import unittest

from tests import support

from domain import settings
from domain.badges import data as BD
from domain.badges import live
from domain.badges import settings as BS
from infra.yaml_reader import loads

support.install()


def errors(**b) -> list[str]:
    return BD.validate([{"name": "x", **b}])


# A live badge whose value a workflow measures and writes with `markdown-kit set`.
SET = live.parse("set")


class Shape(unittest.TestCase):
    def test_a_list_and_a_map_with_its_list_are_the_same_section(self):
        listed = [{"name": "status", "label": "Status", "message": "Active"}]
        self.assertEqual(BD.check(listed), BD.check({"list": listed}))
        self.assertEqual(BD.check(listed), {"list": [{"name": "status", "label": "Status", "message": "Active"}],
                                            "localize": False})

    def test_left_out_or_true_is_no_badges_and_no_localizing(self):
        for given in (None, True, {}, {"list": None}):
            self.assertEqual(BD.check(given), {"list": [], "localize": False}, given)

    def test_the_settings_hand_the_section_to_its_check(self):
        cfg = settings.validate({"badges": [{"name": "a", "label": "A", "message": "B"}]}, parts={"badges": BD.check})
        self.assertEqual(cfg["badges"]["list"][0]["name"], "a")
        cfg = settings.validate({"badges": False}, parts={"badges": BD.check})
        self.assertIs(cfg["badges"], False)

    def test_an_unknown_key_or_field_is_named(self):
        with self.assertRaisesRegex(BD.BadgesError, "unknown key 'rows'"):
            BD.check({"rows": []})
        with self.assertRaisesRegex(BD.BadgesError, r"badges\[0\]: unknown field 'colour'"):
            BD.check([{"name": "a", "label": "A", "colour": "red"}])
        with self.assertRaisesRegex(BD.BadgesError, "expected a map"):
            BD.check(["status"])
        with self.assertRaisesRegex(BD.BadgesError, "localize: expected true or false"):
            BD.check({"localize": "sometimes"})

    def test_hyphens_are_underscores_and_every_value_reads_as_text(self):
        section = BD.check(loads("- name: v\n  label: Version\n  message: 2.0\n  label-color: black\n"
                                 "  reserve: [1.0, 10.10]\n"))
        b = section["list"][0]
        self.assertEqual((b["message"], b["label_color"], b["reserve"]), ("2.0", "black", "1.0, 10.1"))
        self.assertEqual(BD.reserve(b), ("1.0", "10.1"))


class Rules(unittest.TestCase):
    def test_a_name_is_kebab_case_and_unique(self):
        self.assertIn("missing name", BD.validate([{"label": "A"}])[0])
        self.assertIn("kebab-case", errors(name="Build_Status", label="A")[0])
        problems = BD.validate([{"name": "a", "label": "A"}, {"name": "a", "label": "B"}])
        self.assertTrue(any("duplicate name" in p for p in problems), problems)

    def test_a_badge_says_something(self):
        self.assertIn("needs a label or a message", errors()[0])
        self.assertEqual(errors(label="A"), [])
        self.assertEqual(errors(measure=live.parse("release")), [])

    def test_styles_icons_and_colours_come_from_the_kit(self):
        self.assertIn("unknown style", errors(label="A", style="3d")[0])
        self.assertIn("unknown icon", errors(label="A", icon="unicorn")[0])
        self.assertIn("for label_color", errors(label="A", label_color="chartreuse")[0])
        self.assertIn("for message_color", errors(label="A", message_color="#12345")[0])
        self.assertEqual(errors(label="A", label_color="#123456", message_color="rotate"), [])

    def test_only_a_live_badge_wears_the_gold_label(self):
        for gold in ("gold", "#C0A062"):
            self.assertIn("only a live badge wears the gold label", errors(label="A", label_color=gold)[0], gold)
            self.assertIn("measure: set", errors(label="A", message="Hardened", label_color=gold,
                                                 message_color="green")[0], gold)
        self.assertEqual(errors(label="Coverage", measure=SET), [], "a badge a workflow sets is gold by default")
        self.assertEqual(errors(label="Coverage", message="87%", message_color="green", measure=SET), [],
                         "and keeps the message and the state its workflow wrote")
        self.assertEqual(errors(label="Version", message="v2", label_color="black", measure=SET), [])

    def test_a_live_badge_paints_its_message_in_a_state(self):
        self.assertIn("not 'teal'", errors(label="A", label_color="gold", message_color="teal", measure=SET)[0])
        for state in ("green", "yellow", "red", "slate", "#2EA043", "#2ea043"):
            self.assertEqual(errors(label="A", label_color="gold", message_color=state, measure=SET), [], state)
        self.assertEqual(errors(label="A", label_color="#C0A062", message_color="red", measure=SET), [],
                         "gold as its hex")
        self.assertIn("cannot rotate", errors(label="A", label_color="gold", message_color="rotate", measure=SET)[0])

    def test_set_takes_nothing_and_is_live(self):
        self.assertEqual(SET, {"kind": "set", "target": "", "repository": "", "branch": ""})
        with self.assertRaisesRegex(live.MeasureError, "set takes nothing"):
            live.parse({"set": "coverage"})
        b = {"name": "coverage", "label": "Coverage", "measure": SET}
        self.assertTrue(BD.is_live(b) and BD.has_gold_label(b))
        self.assertFalse(BD.kit_measures(b), "a workflow measures it, not the kit")
        self.assertEqual(BD.folder_of(b), "dynamic")
        self.assertEqual(BD.says(b, {}, "2026W40"), ("No Data", "slate"), "no data until a workflow sets it")
        self.assertEqual(BD.says({**b, "message": "87%", "message_color": "green"}, {}, "2026W40"), ("87%", "green"))

    def test_a_badge_that_measures_takes_its_message_and_state_from_the_kit(self):
        m = live.parse("last-commit")
        self.assertEqual(errors(label="Last Commit", measure=m), [])
        self.assertIn("drop message", errors(label="A", message="This Week", measure=m)[0])
        self.assertIn("drop message_color", errors(label="A", message_color="green", measure=m)[0])
        b = {"name": "x", "label": "A", "measure": m}
        self.assertTrue(BD.has_gold_label(b) and BD.is_live(b))
        black = {**b, "label_color": "black"}
        self.assertFalse(BD.has_gold_label(black), "a black label takes any colour")
        self.assertTrue(BD.is_live(black), "and the run still measures it, so it is live")
        self.assertEqual(BD.folder_of(black), "dynamic")
        self.assertEqual(errors(label="A", label_color="black", message_color="rotate", measure=m), [])

    def test_a_plate_refuses_what_it_cannot_honour(self):
        base = {"label": "A", "message": "B", "style": "blueprint-flat"}
        for bad, why in (({"message_color": "teal"}, "drop message_color"),
                         ({"print": "goldprint"}, "unknown print 'goldprint'"),
                         ({"label_color": "navy"}, "black (static) or gold (live)"),
                         ({"label_color": "gold", "message_color": "green", "print": "redprint", "measure": SET},
                          "drop print"),
                         ({"style": "blueprint-3d"}, "unknown style")):
            self.assertIn(why, " ".join(errors(**{**base, **bad})), why)
        self.assertIn("print is for a blueprint style", errors(label="A", print="redprint")[0])
        for good in ({}, {"print": "yellowprint"}, {"print": "rainbowprint"},
                     {"label_color": "gold", "message_color": "slate", "reserve": "C, D", "measure": SET}):
            self.assertEqual(errors(**{**base, **good}), [], good)
        self.assertEqual(errors(label="A", reserve="Failing"), [], "a classic badge keeps room for when it is a plate")

    def test_a_night_file_cannot_collide_with_another_badge(self):
        problems = BD.validate([{"name": "x", "label": "A"}, {"name": "x-dark", "label": "B"}])
        self.assertTrue(any("static/x-dark.svg" in p for p in problems), problems)
        self.assertEqual(BD.validate([{"name": "x", "label": "A", "label_color": "gold", "message_color": "green",
                                       "measure": SET}, {"name": "x-dark", "label": "B"}]), [],
                         "a live badge has no night file")
        measured = {"name": "x", "label": "A", "label_color": "black", "measure": {"kind": "release", "target": ""}}
        gold = {"name": "x-dark", "label": "B", "label_color": "gold", "message_color": "green", "measure": SET}
        problems = BD.validate([measured, gold])
        self.assertTrue(any("dynamic/x-dark.svg" in p for p in problems), "both are live, so both write there")
        self.assertEqual(BD.validate([{"name": "x", "label": "A"}, gold]), [], "one is static and one live")


class Measure(unittest.TestCase):
    def test_a_kind_alone_is_left_to_the_page(self):
        for kind in ("last-commit", "release"):
            self.assertEqual(live.parse(kind), {"kind": kind, "target": "", "repository": "", "branch": ""})

    def test_a_map_names_one_kind_and_what_it_reads(self):
        self.assertEqual(live.parse({"workflow": "self-checks.yml", "repository": "tannergolden/standards",
                                     "branch": "Development"}),
                         {"kind": "workflow", "target": "self-checks.yml", "repository": "tannergolden/standards",
                          "branch": "Development"})
        self.assertEqual(live.parse({"last_commit": "tannergolden"})["target"], "tannergolden")
        self.assertEqual(live.parse({"release": "tannergolden/markdown"})["target"], "tannergolden/markdown")

    def test_what_it_cannot_read_is_named(self):
        for bad, why in (("workflow", "named by its file"), ("stars", "not one of"), (3, "expected one of"),
                         ({"workflow": "a.yml", "release": "a/b"}, "exactly one"),
                         ({"workflow": "checks"}, "not a workflow's file"),
                         ({"release": "markdown"}, "not owner/name"),
                         ({"release": "a/b", "branch": "main"}, "repository and branch are a workflow's"),
                         ({"workflow": "a.yml", "repo": "a/b"}, "unknown key 'repo'"),
                         ({"workflow": "a.yml", "branch": "no spaces"}, "not a branch's name"),
                         ({"last-commit": "a b"}, "neither a login nor owner/name")):
            with self.assertRaisesRegex(live.MeasureError, why, msg=repr(bad)):
                live.parse(bad)

    def test_a_badge_says_where_its_measure_is_wrong(self):
        with self.assertRaisesRegex(BD.BadgesError, r"badges\[0\] \(ci\): measure:"):
            BD.check([{"name": "ci", "label": "CI", "measure": "workflow"}])

    def test_each_value_has_its_state(self):
        self.assertEqual(live.workflow("success"), ("Passing", "green"))
        for failed in ("failure", "timed_out", "startup_failure"):
            self.assertEqual(live.workflow(failed), ("Failing", "red"))
        for quiet in ("cancelled", "skipped", "neutral", None):
            self.assertEqual(live.workflow(quiet), live.NO_DATA)
        self.assertEqual([live.last_commit(d)[0] for d in (0, 7, 8, 31, 32, None)],
                         ["This Week", "This Week", "This Month", "This Month", "Over a Month", "No Data"])
        self.assertEqual(live.release("", None), ("No Release", "slate"))
        self.assertEqual([live.release("v1", d)[1] for d in (0, 90, 91, 365, 366)],
                         ["green", "green", "yellow", "yellow", "red"])

    def test_a_plate_keeps_room_for_every_value_it_can_show(self):
        b = {"name": "ci", "label": "CI", "reserve": "Queued", "measure": live.parse({"workflow": "a.yml"})}
        self.assertEqual(BD.reserve(b), ("Queued", "Passing", "Failing", "No Data"))


SETTINGS = """\
# the page
theme: blackprint
badges:
  # the static row
  - name: status
    label: Status
    message: Active    # as of now
  - name: score
    label: Score
    message: '1'
    label_color: gold
    message_color: green
    measure: set
elements:
  roster:
    kind: roster
    people:
      - name: status
        message: not a badge
"""


class Set(unittest.TestCase):
    def test_a_colon_is_a_colour_only_when_a_colour_follows_it(self):
        self.assertEqual(BS.update("score=1:2"), ("score", "1:2", None))
        self.assertEqual(BS.update("status=Paused:yellow"), ("status", "Paused", "yellow"))
        self.assertEqual(BS.update("status=a:#2EA043"), ("status", "a", "#2EA043"))
        with self.assertRaisesRegex(ValueError, "NAME=MESSAGE"):
            BS.update("status")

    def test_values_are_set_in_place_and_the_rest_of_the_file_is_kept(self):
        new, missing = BS.set_values(SETTINGS, {"status": ("Paused", "yellow"), "score": ("7.10", "red")})
        self.assertEqual(missing, [])
        self.assertIn("  # the static row\n", new)
        self.assertIn("    message: Paused\n    message_color: yellow\n", new, "a colour line is added")
        self.assertIn("    message: '7.10'\n", new, "a number stays the text it is")
        self.assertIn("    message_color: red\n", new)
        self.assertIn("        message: not a badge", new, "only the badges section is touched")
        cfg = loads(new)
        self.assertEqual(cfg["badges"][1]["message"], "7.10")

    def test_a_live_badge_no_workflow_has_set_gets_its_message_under_its_name(self):
        text = SETTINGS.replace("elements:", "  - name: coverage   # set by the tests' workflow\n    label: Coverage\n"
                                "    measure: set\nelements:")
        new, missing = BS.set_values(text, {"coverage": ("87%", "green"), "status": ("Paused", None)})
        self.assertEqual(missing, [])
        self.assertIn("  - name: coverage   # set by the tests' workflow\n    message: '87%'\n"
                      "    message_color: green\n    label: Coverage\n", new)
        self.assertEqual(loads(new)["badges"][2]["message"], "87%")
        self.assertIn("  - name: status\n    label: Status\n    message: Paused\n", new, "an entry with one keeps it")

    def test_nothing_is_set_when_a_badge_is_missing(self):
        new, missing = BS.set_values(SETTINGS, {"status": ("X", None), "nope": ("Y", None)})
        self.assertEqual((new, missing), (SETTINGS, ["nope"]))

    def test_what_yaml_would_misread_is_quoted(self):
        for text in ("yes", "No", "on", "null", "1.0", "-1", "a: b", "# x", "[a]", "", " x", "*star", "x "):
            self.assertEqual(loads(f"v: {BS.scalar(text)}\n")["v"], text, text)
        self.assertEqual(BS.scalar("Active"), "Active")


if __name__ == "__main__":
    unittest.main()
