# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Forge set's own rules, which the checks every set shares cannot know, and those shared checks run over the
set itself, since it is a theme the calendar does not register.

Its own rules: embers rise only across a wide moving header by night, its still twin keeps the far ones where
they lie, and a phone's header has none; the fire burns in the hearth and the hot iron lights what stands near it
only by night; a title is polished steel by day and red-hot iron by night, hottest toward the middle of the line,
with a glow of one ring on a small title and three on the biggest, and is set a line at a time however long it
runs; a counter's digits keep an ink of their own, so they are set over the plates they are stamped into; a
strip's hero is the armoury's trophy, as tall as the strip; a wide H1 hangs the rack over the smith, its short form
beside a long title; every phone header stands its scene in rows of its own
under its words, clear of them and as tall as the hand's composition asks; the most a page can say keeps its whole
scene and its motion within the budget, a drawing made lighter thins only texture, and ordinary pages keep room to
spare at full weight with the month's mark; a steel strap lies along every badge's top two rows with the letters
under it; the frame's foot is lit from below by night; a helm's initials read on its faceplate, its slit is dark and
its crest is the knight's own colour; a footer carries the heavy riveted band, lies on a floor of the hearth's stone
with coal heaped on it and the smith's anvil at its right end where the cells leave it room, the touchmark in its
closing cell and beside its scale bar, a dome at every join of its rules and by night the forge's glow along its
foot; a link is a stamped steel tag under its budget; the schematic's icons are stamped into recessed plates and its
wires pinned where they turn; the dial's needle glows by night; a long strap is buckled in brass; and the placard
bears the touchmark. The set is the medieval collection's November, drawn in the collection's hand: the hand's check
finds nothing, as the month's design or kept all year; its words are in the hand's inks and its plate in the hand's
bands; every flame, coal, ember and spark burns on the hand's flame; the smith is drawn to the hand's canon on its
skin; every motion keeps the hand's timing; and the month's mark has its box clear, the mail parting either side of
it."""
from __future__ import annotations

import datetime as dt
import re
import unittest
import xml.dom.minidom as minidom
from collections import Counter
from unittest import mock

from tests import support
from tests.unit.test_holiday_sets import DASHES, ELEMENTS, HEIGHTS, STAMP, contents

from domain import KIT, KIT_VERSION
from domain.badges import data as BD
from domain.banners.content import Footer, Header
from domain.banners.designs import DESIGNS, budget, variants
from domain.canvas import BUDGET, DARK, DAY, colours, lint
from domain.elements import draw as E
from domain.holidays.designs import NARROW, WIDE, Holiday
from domain.holidays.designs.badges import PLATE, STATES, STYLES, STYLES as BADGE_STYLES, TOP, nearest
from domain.holidays.designs.banners import MARK_Y
from domain.collections.hand import MEDIEVAL, CollectionSet, check, lab
from domain.collections.medieval_forge import CRESTS, SET, UNDER, Forge
from domain.collections.medieval_forge import art as A
from domain.collections.medieval_forge.palette import C, NIGHT_SKY, RAMP, X
from domain.holidays.pixel import BLINKS, Pix, contrast
from domain.palette import PALETTE

support.install()
KEY = SET.key
HEADER = Header(tone="standard", holiday=KEY)
WIDE_TITLE = HEADER.with_(title="W" * 24)      # two lines on a phone, each as wide as the room allows
STEEL, COAL, IRON, BRASS, FIRE = RAMP["steel"], RAMP["coal"], RAMP["iron"], RAMP["brass"], RAMP["fire"]
HELD = SET.on(dt.date(2026, 11, 3))     # the set drawn as the collection's November, carrying the month's mark
# The proof sheet's own contents, ordinary pages too: a repository's banners, a profile, and a title alone.
PROOF = {
    "banners": Header(title="BANNERS", tagline=("Blueprint headers and footers a README draws for itself. Measured "
                                                "nightly, never fetched, so they are up for as long as GitHub is."),
                      motto="Drafted, never fetched.", notes=(), description="",
                      figures=(("PROJECT", "tannergolden/banners"), ("RELEASE", "v1.8.0"), ("STARS", "0"),
                               ("FORKS", "0"), ("OPEN ISSUES", "0"), ("LANGUAGE", "Python"), ("LICENSE", "MIT")),
                      tone=KEY),
    "profile": Header(title="Tanner Golden", tagline=("Infrastructure for AI research. Reproducibility, supply-chain "
                                                      "hygiene, and CI that fails for the right reasons."),
                      motto="Built to be rebuilt.", notes=("All times in EST.",), description="",
                      figures=(("ACCOUNT", "@tannergolden"), ("REPOSITORIES", "9"), ("CONTRIBUTIONS", "1,054"),
                               ("LANGUAGE", "Python"), ("MEMBER SINCE", "2016"), ("SITE", "tannergolden.com")),
                      tone=KEY),
    "bare": Header(title="x", tagline="", motto="", notes=(), description="", figures=(), tone=KEY),
}
# The pieces of the smithy, each drawn by its own function of the set's art.
PIECES = ("hearth", "flames", "coals", "smoke", "bellows", "tools", "anvil", "blade", "smith", "sparks", "bucket",
          "rack", "sword_over_shield", "trophy", "heater", "embers", "title", "title_glints", "lamp", "pool", "heat",
          "footer_floor", "smiths_mark", "maker_mark")


def mark_at(p: Pix, night: bool):
    """Where the smith's touchmark is struck into `p`, its top-left, or None."""
    cut = IRON[2] if night else IRON[0]
    cells = [(i, j) for j, row in enumerate(A.MARK) for i, ch in enumerate(row) if ch != "."]
    i0, j0 = cells[0]
    base = p.layers["base"]
    for (x, y), c in base.items():
        if c == cut and all(base.get((x - i0 + i, y - j0 + j)) == cut for (i, j) in cells):
            return (x - i0, y - j0)
    return None


def crowns(p: Pix, night: bool) -> set:
    """Every pixel of `p` that is a rivet's or a dome's lit crown."""
    crown = IRON[5] if night else C["white"]
    return {q for q, c in p.layers["base"].items() if c in (crown, IRON[6] if night else crown)}


def draw_banners() -> list:
    """Every banner file the set draws for the contents every set is held to: (content, code, file name, svg)."""
    out = []
    for name, (h, f) in contents(KEY).items():
        for code, design in DESIGNS.items():
            content = h if design.kind == "header" else f
            drawer = SET.header if design.kind == "header" else SET.footer
            for suffix, wide, motion, theme in variants(design):
                out.append((name, code, f"{design.kind}-{suffix}.svg", drawer(code, content, theme, wide, motion)))
            if design.kind == "footer" and f.on("links"):
                for i, (label, _) in enumerate(f.links):
                    for theme in (DAY, DARK):
                        out.append((name, code, f"link-{i}-{theme['name']}.svg", SET.link(label, theme, i)))
    return out


def drawn(draw) -> tuple:
    """What `draw()` returns, and for every drawing it made on the way, the pieces of the smithy drawn on it."""
    seen: dict = {}

    def counting(name, fn):
        def piece(p, *a, **k):
            seen.setdefault(p, Counter())[name] += 1
            return fn(p, *a, **k)
        return piece
    with mock.patch.multiple(A, **{name: counting(name, getattr(A, name)) for name in PIECES}):
        return draw(), seen


def served(code, h, theme) -> tuple:
    """A wide moving header as the kit draws it, fitted to its budget: the file, the drawing it was written from,
    and the pieces of the smithy on that drawing."""
    made = []
    write = Pix.svg

    def svg(p, *a, **k):
        made.append((p, write(p, *a, **k)))
        return made[-1][1]
    with mock.patch.object(Pix, "svg", svg):
        out, seen = drawn(lambda: SET.header(code, h, theme, True, True))
    p = next(q for q, text in made if text == out)
    return out, p, seen.get(p, Counter())


def moving(p: Pix) -> set:
    """Every layer of a drawing that moves and has something on it."""
    return {name for name, (_, _, anim) in p.meta.items()
            if anim and (p.layers[name] or p.uses[name] or p.shapes[name])}


def phone(code, h, night) -> tuple:
    """A phone's header as the set draws it, the pixels its scene hooks drew on it, and the pieces of the smithy on
    it."""
    found = []
    narrow, under = Forge.scene_narrow, Forge.scene_under

    def watch(p, draw):
        before = {name: dict(cells) for name, cells in p.layers.items()}
        draw()
        found.append((p, {q for name, cells in p.layers.items()
                          if not name.startswith(("haze", "pool", "fb", "fl", "glow"))
                          for q, c in cells.items() if ":" not in c and before.get(name, {}).get(q) != c}))

    def spy_narrow(self, design, p, y, night):
        watch(p, lambda: narrow(self, design, p, y, night))

    def spy_under(self, design, p, y0, y1, night):
        watch(p, lambda: under(self, design, p, y0, y1, night))
    with mock.patch.object(Forge, "scene_narrow", spy_narrow), mock.patch.object(Forge, "scene_under", spy_under):
        p, seen = drawn(lambda: getattr(SET, f"{code.lower()}_narrow")(h, night))
    cells = set()
    for q, new in found:
        if q is p:
            cells |= new
    return p, cells, seen.get(p, Counter())


DRAWN: list = []


def every_banner() -> list:
    if not DRAWN:
        DRAWN.extend(draw_banners())
    return DRAWN


class Embers(unittest.TestCase):
    def test_embers_rise_only_across_a_wide_moving_header_by_night(self):
        moving = SET.header("H1", HEADER, DARK, True, True)
        still = SET.header("H1", HEADER, DARK, True, False)
        phone = SET.header("H1", HEADER, DARK, False, False)
        day = SET.header("H1", HEADER, DAY, True, True)
        for depth in ("far", "near"):
            self.assertIn(f'href="#em{depth}g"', moving)
        self.assertIn('clip-path="url(#emfarc)"', still, "the still twin keeps the far embers where they lie")
        self.assertNotIn("emnear", still, "and leaves the near ones, which would sit on its letters, out")
        self.assertNotIn("emfar", phone)
        self.assertNotIn("emfar", day)
        self.assertNotIn("emnear", day)

    def test_a_lighter_drawing_keeps_its_embers_rising_at_both_depths_but_half_as_many(self):
        counts = []
        rise = A.embers

        def embers(p, *a, **k):
            counts.append((p.lite, a[4]))
            return rise(p, *a, **k)
        full = SET.header("H2", HEADER, DARK, True, True)
        with mock.patch.dict(BUDGET, {"header": len(full.encode("utf-8")) - 1}), mock.patch.object(A, "embers", embers):
            lighter = SET.header("H2", HEADER, DARK, True, True)
        for depth in ("far", "near"):
            self.assertIn(f'href="#em{depth}g"', lighter, depth)
        (_, n), (lite, half) = counts
        self.assertTrue(lite)
        self.assertEqual(half, n // 2)


class Fire(unittest.TestCase):
    def test_the_fire_burns_by_day_and_night_but_only_the_night_lights_what_is_near(self):
        night = SET.h1(HEADER, True, True)
        day = SET.h1(HEADER, False, True)
        for p in (night, day):
            self.assertTrue(p.layers.get("fire0") and p.layers.get("fire1"), "the fire's two frames")
        self.assertIn(FIRE[6], set(night.layers["fire1"].values()), "white at the heart by night")
        self.assertNotIn(FIRE[6], set(day.layers["fire1"].values()), "duller by day")
        self.assertTrue(night.lamps, "the hearth and the blade are registered as hot things")
        self.assertFalse(day.lamps)
        self.assertIn(X["heat"], SET.header("H1", HEADER, DARK, True, True))
        self.assertNotIn(X["heat"], SET.header("H1", HEADER, DAY, True, True))
        self.assertNotIn("fb0", day.layers, "no glow flickers round the mouth by day")

    def test_the_hammer_swings_in_a_moving_header_and_rests_mid_swing_in_its_still_twin(self):
        moving = SET.h1(HEADER, True, True)
        for frame in ("swup", "swmid", "swdown", "sp0", "sp1", "sp2"):
            self.assertTrue(moving.layers.get(frame), frame)
        still = SET.h1(HEADER, True, False)
        self.assertFalse(any(name.startswith("sw") for name in still.layers if still.layers[name]))
        kept = [name for name, meta in moving.meta.items() if name.startswith("sw") and meta[2] and meta[2][4]]
        self.assertEqual(kept, ["swmid"])


class Titles(unittest.TestCase):
    def test_a_title_is_steel_by_day_and_red_hot_iron_by_night_hottest_toward_the_middle(self):
        day = SET.header("H1", HEADER, DAY, True, True)
        night = SET.header("H1", HEADER, DARK, True, True)
        self.assertIn('id="pasteel4d"', day)
        self.assertNotIn("pahot", day)
        self.assertIn('id="pahot4n2"', night, "the letters toward the middle are white hot")
        self.assertIn('id="pahot4n0"', night, "and those at the ends have cooled")
        self.assertNotIn("pasteel", night)
        self.assertEqual([A._heat(m) for m in (0.02, 0.2, 0.5, 0.8, 0.98)], [0, 1, 2, 1, 0])
        core = A.hot_fill(3 * 4, 0, 4, True, 2)
        self.assertEqual(core, RAMP["flame"][6])
        self.assertIn(A.hot_fill(0, 0, 4, True, 2), RAMP["ember"])
        self.assertIn(A.hot_fill(6 * 4, 0, 4, True, 0), RAMP["ember"])

    def test_the_night_glow_has_one_ring_on_a_small_title_and_three_on_the_biggest(self):
        for lite in (False, True):
            for scale, rings in ((2, 1), (3, 1), (4, 3)):
                p = Pix(200, 60, lite=lite)
                SET.title_text(p, 4, 4, "ABC", True, scale)
                self.assertEqual(len(p.uses["glow"]) + len(p.shapes["glow"]), rings, (lite, scale))
        p = Pix(200, 60)
        SET.title_text(p, 4, 4, "ABC", False, 4)
        self.assertNotIn("glow", p.layers, "steel has no glow")

    def test_a_title_is_set_a_line_at_a_time_however_long_it_runs(self):
        for night in (False, True):
            p = Pix(415, 60)
            SET.title_text(p, 10, 10, "W" * 13, night, 2)
            uses = p.uses["base"]
            self.assertEqual(sum(1 for u in uses if u[0] == IRON[0]), 4, "its edge, the line four times a pixel off")
            paint = [u for u in uses if u[0].startswith("url(")]
            self.assertEqual(len(paint), 5 if night else 1, "a use for each run of letters one paint covers")
            self.assertEqual(len({u[0] for u in paint}), 3 if night else 1, "hottest toward the middle by night")
            self.assertEqual(len(p.uses.get("glow", [])), 1 if night else 0, "and its glow's ring once")
            self.assertEqual(p.words, [(9, 9, 10 + 13 * 12 - 2 + 1, 10 + 14 + 1)], "taking the room its letters take")


class Scenes(unittest.TestCase):
    def test_a_strips_hero_is_the_armourys_trophy_as_tall_as_the_strip(self):
        """A wide strip's hero is the armoury's trophy at its right, a shield of red enamel bearing the smith's arms
        in brass, the helm over it and two swords crossed behind it, hung from under the mail and rising the strip's
        full height, clear of every word; where the words leave the floor clear, the smith works at his anvil before
        it."""
        scene, rules = Forge.scene, []

        def spy(self, design, p, rule, night, motion):
            rules.append(rule)
            return scene(self, design, p, rule, night, motion)
        for name in ("kit", "repository", "profile", "least"):
            h, _ = contents(KEY)[name]
            for night in (False, True):
                with mock.patch.object(A, "trophy", wraps=A.trophy) as trophy, mock.patch.object(Forge, "scene", spy):
                    p, seen = drawn(lambda: SET.h3(h, night, True))
                (call,) = [c for c in trophy.call_args_list if c.args[0] is p]
                top, rule = call.args[2], rules[-1]
                self.assertGreaterEqual(rule - top, 55, (name, night, "as tall as the strip"))
                self.assertEqual(top, A.TROPHY_TOP + max(0, (rule - 3 - A.TROPHY_TOP - A.TROPHY_H) // 2))
                gold = [q for q, c in p.layers["base"].items() if c in BRASS and q[0] > 360]
                self.assertGreaterEqual(len(gold), 60, (name, night, "the smith's arms in brass"))
                if name == "least":
                    self.assertTrue(seen[p]["smith"], (night, "the smith before it on a clear floor"))
        self.assertEqual(A.TROPHY_H, 55)

    def test_a_wide_h1_hangs_the_rack_over_the_smith_and_its_short_form_beside_a_long_title(self):
        """A wide H1 hangs the rack of shields and an axe on the wall over the smith, its beam 68 rows over the
        rule, so the right of the smithy rises at least 70 percent of the way from the mail to the rule; where the
        words reach toward it, as a long title does, its short form, the red shield and the axe, hangs at the right
        end instead, clear of every word."""
        scene, rules = Forge.scene, []

        def spy(self, design, p, rule, night, motion):
            rules.append(rule)
            return scene(self, design, p, rule, night, motion)
        for name, short in (("kit", False), ("repository", False), ("least", False), ("profile", True)):
            h, _ = contents(KEY)[name]
            for night in (False, True):
                where = (name, night)
                with mock.patch.object(A, "rack", wraps=A.rack) as rack, mock.patch.object(Forge, "scene", spy):
                    p = SET.h1(h, night, False)
                (call,) = [c for c in rack.call_args_list if c.args[0] is p]
                x0, x1, beam, rule = call.args[1], call.args[2], call.args[3], rules[-1]
                self.assertEqual(rule - beam, 68, where)
                self.assertGreaterEqual(rule - beam, 0.7 * (rule - A.TROPHY_TOP), where)
                self.assertEqual(call.kwargs.get("short", False), short, where)
                self.assertEqual(x1 - x0, A.RACK_SHORT_W if short else 57, where)
                self.assertTrue(p.clear_of_words(x0 - 2, beam - 2, x1, beam + 26), where)

    def test_the_phones_hearth_and_blade_throw_a_stronger_light_by_night_than_the_moving_headers(self):
        h = contents(KEY)["profile"][0]
        phone = SET.header("H1", h, DARK, False, False)
        wide = SET.header("H1", h, DARK, True, True)
        self.assertIn('rx="24" ry="17"', phone, "the hearth's pool on the phone")
        self.assertIn('rx="20" ry="15"', wide, "and the wide header's smaller one, which its motion carries")
        self.assertNotIn('rx="24" ry="17"', wide)

    def test_the_frames_foot_is_lit_from_below_by_night(self):
        day = SET.footer("F1", contents(KEY)["repository"][1], DAY, True, False)
        night = SET.footer("F1", contents(KEY)["repository"][1], DARK, True, False)
        self.assertIn('id="frw"', night)
        self.assertNotIn('id="frw"', day)


class Phones(unittest.TestCase):
    def test_every_phone_header_stands_its_scene_under_its_words_as_tall_as_the_hand_asks(self):
        """Every phone header of every shared content, by day and by night, stands its scene in rows of its own
        under its words, at least two clear of every one, as tall as the hand's composition asks: the whole smithy
        across an H1, at least 48 rows tall, its hearth, bellows, anvil, smith and quench bucket; the smithy on an
        H2 and the armoury's trophy over the anvil on an H3, at least 40 rows each. By night the forge's light falls
        on what stands near it."""
        named = {"H1": ("hearth", "bellows", "anvil", "blade", "smith", "bucket"),
                 "H2": ("hearth", "bellows", "anvil", "blade", "smith", "sparks"),
                 "H3": ("trophy", "heater", "anvil", "blade", "bucket")}
        tall = {"H1": 48, "H2": 40, "H3": 40}
        for name, (h, _) in contents(KEY).items():
            for code in ("H1", "H2", "H3"):
                for night in (False, True):
                    where = (name, code, night)
                    p, cells, pieces = phone(code, h, night)
                    for piece in named[code]:
                        self.assertTrue(pieces[piece], (where, piece))
                    top, foot = min(y for _, y in cells), max(y for _, y in cells)
                    self.assertGreaterEqual(foot + 1 - top, tall[code], where)
                    if code == "H1":
                        xs = [x for x, _ in cells]
                        self.assertTrue(min(xs) <= 8 and max(xs) >= NARROW - 8, (where, "across the phone"))
                    if night:
                        self.assertTrue(p.lamps, (where, "the forge's light on what stands near"))
                    for (x, y) in cells:
                        self.assertTrue(p.clear_of_words(x - 2, y - 2, x + 3, y + 3), (where, x, y))

    def test_a_phones_h2_and_h3_ask_for_the_rows_their_heroes_stand_in(self):
        """A phone's H2 and H3 are the kit's layouts with the rows their heroes stand in asked for under the words,
        whatever the words; an H1 asks for the rows its smithy stands in, its notes set under its words."""
        for name, (h, _) in contents(KEY).items():
            for code in ("H2", "H3"):
                own = getattr(Holiday, f"{code.lower()}_narrow")(SET, h, False)    # the kit's layout alone
                p = getattr(SET, f"{code.lower()}_narrow")(h, False)
                self.assertEqual(p.h - own.h, UNDER[code], (name, code))
            own = Holiday.h1_narrow(SET, h, False)
            self.assertGreater(SET.h1_narrow(h, False).h, own.h, name)
        self.assertGreaterEqual(SET.SMITHY, 48)


class Budget(unittest.TestCase):
    def test_the_most_contents_wide_headers_keep_their_whole_scene_and_their_motion_within_the_budget(self):
        most = contents(KEY)["most"][0]
        for code in ("H1", "H2"):
            for theme in (DAY, DARK):
                where = (code, theme["name"])
                svg, p, pieces = served(code, most, theme)
                with mock.patch.dict(BUDGET, {"header": 10 ** 9}):
                    _, full, whole = served(code, most, theme)
                self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"], where)
                self.assertIn("<animate", svg, where)
                for piece in ("hearth", "flames", "smoke", "bellows", "tools", "anvil", "blade", "smith", "sparks",
                              "title", "title_glints"):
                    self.assertTrue(pieces[piece], (where, piece))
                if theme["dark"]:
                    for piece in ("embers", "lamp", "pool", "heat"):
                        self.assertTrue(pieces[piece], (where, piece))
                self.assertEqual(pieces, whole, (where, "every piece the full drawing has"))
                self.assertEqual(moving(p), moving(full), (where, "and all its motion"))

    def test_a_drawing_made_lighter_thins_only_texture(self):
        most = contents(KEY)["most"][0]
        for code in ("H1", "H2", "H3"):
            for theme in (DAY, DARK):
                where = (code, theme["name"])
                with mock.patch.dict(BUDGET, {"header": 10 ** 9}):
                    whole_svg, full, whole = served(code, most, theme)
                with mock.patch.dict(BUDGET, {"header": len(whole_svg.encode("utf-8")) - 1}):
                    svg, p, pieces = served(code, most, theme)
                self.assertTrue(p.lite and len(svg) < len(whole_svg), where)
                self.assertIn("<animate", svg, where)
                self.assertEqual(pieces, whole, (where, "every figure, prop and light"))
                self.assertEqual(moving(p), moving(full), (where, "and all the motion"))
                # what goes is texture: the plate's grain, every other rivet on the rule, the hearth's darker
                # stones, and the faint outer ring of each pool of light
                self.assertIn(X["grain_n" if theme["dark"] else "grain_lo"], whole_svg, where)
                self.assertNotIn(X["grain_n" if theme["dark"] else "grain_lo"], svg, where)
                self.assertIn('id="rv11', whole_svg, where)
                self.assertIn('id="rv22', svg, where)
                if code != "H3":
                    self.assertGreater(len(full.layers["base"]), len(p.layers["base"]), (where, "darker stones"))
                if theme["dark"] and code != "H3":
                    self.assertLess(svg.count("<ellipse"), whole_svg.count("<ellipse"), (where, "outer rings"))
                    self.assertIn(X["heat"], svg, (where, "the forge's light on what stands near"))


class Footers(unittest.TestCase):
    def footers(self):
        ft = contents(KEY)["repository"][1]
        for narrow in (False, True):
            for code in ("F1", "F2"):
                for night in (False, True):
                    draw = getattr(SET, f"{code.lower()}_narrow" if narrow else code.lower())
                    yield code, narrow, night, draw(ft, night)

    def test_the_heavy_band_runs_along_every_footers_top_edge_with_a_dome_every_nine_pixels(self):
        for code, narrow, night, p in self.footers():
            base = p.layers["base"]
            tones = (IRON[4], IRON[6], IRON[5], IRON[2]) if night else (STEEL[6], C["white"], STEEL[3])
            self.assertTrue(all(base.get((x, 1)) in tones for x in range(8, p.w - 8)), (code, narrow, night))
            domes = [x for x in range(8, p.w - 8) if base.get((x, 1)) == (IRON[6] if night else C["white"])]
            self.assertGreaterEqual(len(domes), (p.w - 16) // 9 - 1, (code, narrow, night))
            self.assertTrue(all(b - a == 9 for a, b in zip(domes, domes[1:])), "evenly spaced")

    def test_the_touchmark_is_struck_into_the_closing_cell_of_every_f1_with_a_closing_note(self):
        for name, (_, ft) in contents(KEY).items():
            for narrow in (False, True):
                for night in (False, True):
                    p = (SET.f1_narrow if narrow else SET.f1)(ft, night)
                    at = mark_at(p, night)
                    if not ft.get("closing"):
                        self.assertIsNone(at, (name, narrow, night))
                        continue
                    self.assertIsNotNone(at, (name, narrow, night))
                    x, y = at
                    self.assertTrue(all(p.clear_of_words(x + i, y + j, x + i + 1, y + j + 1)
                                        for j, row in enumerate(A.MARK) for i, ch in enumerate(row) if ch != "."),
                                    "and lies on no word")
                    lip = RAMP["stone"][5] if night else C["white"]
                    self.assertIn(lip, {p.layers["base"].get((x + i + 1, y + j + 1)) for i, j in ((2, 0), (0, 2))},
                                  "with the lip of light the strike pushed up")

    def test_the_touchmark_is_struck_beside_every_f2s_scale_bar(self):
        """Every F2, wide and on a phone, by day and by night, has the smith's touchmark struck beside its scale
        bar, on no word."""
        for name, (_, ft) in contents(KEY).items():
            for narrow in (False, True):
                for night in (False, True):
                    p = (SET.f2_narrow if narrow else SET.f2)(ft, night)
                    at = mark_at(p, night)
                    self.assertIsNotNone(at, (name, narrow, night))
                    x, y = at
                    n = len(A.MARK)
                    self.assertTrue(p.clear_of_words(x - 2, y - 2, x + n + 2, y + n + 2), (name, narrow, night))

    def test_a_dome_sits_on_every_join_of_a_footers_rules(self):
        for code, narrow, night, p in self.footers():
            base = p.layers["base"]
            rule = SET.ink(night)["rule"]
            uprights = {x for (x, y), c in base.items() if c == rule and y == p.h // 2
                        and base.get((x, p.h // 2 - 1)) == rule and base.get((x, p.h // 2 + 1)) == rule}
            if code == "F1" and not narrow:
                self.assertGreaterEqual(len(uprights), 3)
            tops = crowns(p, night) | ({q for q, c in base.items() if c == RAMP["stone"][6]} if night else set())
            for x in uprights:
                where = (code, narrow, night, x)
                self.assertTrue(any((x - 1, yy) in tops for yy in range(2, 8)), (*where, "a dome at its head"))
                foot = max(y for (xx, y), c in base.items() if xx == x and c == rule)
                self.assertTrue(any((x - 1, yy) in tops for yy in range(foot - 1, foot + 4)),
                                (*where, "and at its foot, on the floor"))

    def test_every_footer_lies_on_a_floor_of_the_hearths_stone_with_coal_heaped_on_it(self):
        """Every footer of every shared content, wide and on a phone, by day and by night, lies on a floor of the
        hearth's stone laid along its foot between the frame's sides, its rules standing on it, and coal heaped on
        it wherever the cells leave a stretch clear, every lump two rows clear of every word."""
        floors = []
        real = A.footer_floor

        def spy(p, night, rule):
            floors.append((p, real(p, night, rule)))
            return floors[-1][1]
        for name, (_, ft) in contents(KEY).items():
            for code in ("F1", "F2"):
                for wide in (True, False):
                    for night in (False, True):
                        where = (name, code, wide, night)
                        with mock.patch.object(A, "footer_floor", spy):
                            SET.footer(code, ft, DARK if night else DAY, wide, False)
                        p, tops = floors[-1]
                        laid = re.findall(r'<rect x="4" y="(\d+)" width="(\d+)" height="(\d+)" fill="url\(#mf\)"/>',
                                          "".join(p.shapes["base"]))
                        self.assertEqual(len(laid), 1, where)
                        y, w, h = (int(v) for v in laid[0])
                        self.assertEqual((w, y + h), (p.w - 8, p.h), (where, "along the whole foot"))
                        rule = SET.ink(night)["rule"]
                        self.assertFalse([xy for xy, c in p.layers["base"].items() if c == rule and xy[1] >= y],
                                         (where, "the rules stand on it"))
                        for x in range(p.w):
                            if tops[x] < y:
                                self.assertTrue(p.clear_of_words(x - 2, tops[x] - 2, x + 3, tops[x] + 3), (where, x))

    def test_where_the_cells_leave_room_the_smiths_anvil_stands_at_the_right_end(self):
        """A title block without notes leaves a long stretch of its foot clear after Back to Top: there the smith's
        anvil stands at the right end of the floor with the hammer laid on it, and coal is heaped along the stretch,
        a few of its coals glowing on the hand's flame, by day and by night."""
        ft = Footer(closing="", top="Back to Top", handle="@tannergolden", license="MIT", updated="2026-09-25",
                    links=(), tone=KEY)
        for night in (False, True):
            with mock.patch.object(A, "smiths_mark", wraps=A.smiths_mark) as mark:
                p = SET.f1(ft, night)
            (call,) = mark.call_args_list
            x = call.args[1]
            self.assertGreater(x, max(b[2] for b in p.words), (night, "after every word"))
            self.assertGreaterEqual(x + A.SMITHS_MARK_W, p.w - 12, (night, "at the right end"))
            glowing = {c for c in p.layers["base"].values() if c in FIRE}
            self.assertTrue(glowing, (night, "coals glowing in the heap"))

    def test_the_forges_glow_lies_along_a_footers_foot_by_night(self):
        ft = contents(KEY)["repository"][1]
        for code in ("F1", "F2"):
            for wide in (True, False):
                night = SET.footer(code, ft, DARK, wide, False)
                day = SET.footer(code, ft, DAY, wide, False)
                self.assertIn('<linearGradient id="fg"', night, (code, wide))
                self.assertIn('fill="url(#fg)"', night, (code, wide))
                self.assertNotIn('id="fg"', day, (code, wide))


class Links(unittest.TestCase):
    def test_a_link_is_a_stamped_steel_tag_under_its_budget(self):
        for night in (False, True):
            p = SET.link_button("Pull requests", 1, night)
            fill, edge, ink, shade = SET.link_colours(night)
            base = p.layers["base"]
            self.assertGreaterEqual(contrast(ink, fill), 4.5)
            self.assertEqual(base.get((0, 7)), edge, "a dark edge")
            self.assertEqual(base.get((p.w // 2, 3)), IRON[4] if night else STEEL[6], "lit along its top")
            self.assertEqual(base.get((p.w - 2, 7)), COAL[0] if night else STEEL[2], "shaded down its right")
            crown = IRON[5] if night else C["white"]
            self.assertEqual(base.get((2, 6)), crown, "a rivet at each end")
            self.assertEqual(base.get((p.w - 5, 6)), crown)
            uses = p.uses["base"]
            dark = [(x, y) for (s, _, x, y, _) in uses if s == ink]
            white = [(x, y) for (s, _, x, y, _) in uses if s == C["white"]]
            self.assertEqual(len(dark), len("PULL REQUESTS") - 1, "the letters, each a use of its glyph")
            if night:
                self.assertFalse(white, "by night the letters are bright on dark iron")
                foot = {base.get((x, 12)) for x in range(5, p.w - 5)}
                self.assertEqual(foot, {RAMP["ember"][2]}, "an ember-lit foot")
            else:
                self.assertEqual(sorted(white), sorted((x + 1, y + 1) for (x, y) in dark),
                                 "by day each letter is cut into the steel, a lip of light below and right of it")
                self.assertLess(uses.index(next(u for u in uses if u[0] == C["white"])),
                                uses.index(next(u for u in uses if u[0] == ink)), "the lips lie under the letters")
            for i in range(4):
                svg = SET.link("Pull requests", DARK if night else DAY, i)
                self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["link"])


class Elements(unittest.TestCase):
    def test_the_schematics_icons_are_stamped_into_recessed_plates_and_its_wires_pinned_where_they_turn(self):
        d = ELEMENTS["how-it-runs"]
        for night in (False, True):
            p = SET.draw_element("schematic", E.describe("schematic", d), night, "wide")
            base = p.layers["base"]
            recess = COAL[2] if night else STEEL[5]
            self.assertGreater(sum(1 for c in base.values() if c == recess), 100, "the icon cells' plates")
            if not night:
                body = SET.ink(night)["body"]
                icons = [q for q, c in base.items() if c == body and base.get((q[0] + 1, q[1] + 1)) == C["white"]]
                self.assertTrue(icons, "the icons' lips of light")
            wire = SET.wire_ink(night)
            pins = [q for q in crowns(p, night)
                    if any(base.get((q[0] + dx, q[1] + dy)) == wire for dx in (-1, 0, 1, 2) for dy in (-1, 0, 1, 2))]
            self.assertGreaterEqual(len(pins), 4, "rivets along the rods")

    def test_the_dials_needle_glows_by_night(self):
        vitals = ELEMENTS["vitals"]
        for night in (False, True):
            p = SET.draw_element("instruments", E.describe("instruments", vitals), night, "wide")
            cx, cy, r = p.dial
            reach = r - 11
            near = [(q, c) for q, c in p.layers["base"].items()
                    if (q[0] + 0.5 - cx) ** 2 + (q[1] + 0.5 - cy) ** 2 <= reach ** 2]
            hot = [q for q, c in near if c in (RAMP["flame"][6], RAMP["flame"][5], RAMP["flame"][4])]
            red = [q for q, c in near if c == RAMP["ember"][5]]
            if night:
                self.assertIn(RAMP["flame"][6], [c for q, c in near], "white heat at the needle's point")
                self.assertGreater(len(hot), len(red), "and most of it yellow, only the hub's end red")
                self.assertTrue(any(c.startswith(RAMP["ember"][5]) for c in p.layers["haze"].values()),
                                "its light round it")
            else:
                self.assertFalse(hot)

    def test_each_knights_helm_has_a_dark_slit_and_a_crest_of_their_own_colour(self):
        for night in (False, True):
            p = SET.draw_element("roster", E.describe("roster", ELEMENTS["contributors"]), night, "wide")
            worn = {c for c in p.layers["base"].values() if c in CRESTS}
            self.assertGreaterEqual(len(worn), 3, "a colour each")
            for i in range(3):
                q = Pix(40, 40)
                SET.avatar(q, 20, 20, i, {"initials": "AB", "name": "T", "n": 1}, night)
                slit = [x for x in range(13, 28) if q.layers["base"].get((x, 18)) == COAL[0]]
                self.assertGreaterEqual(len(slit), 9, (night, i))

    def test_a_strap_long_enough_for_a_name_is_buckled_in_brass(self):
        for night in (False, True):
            k = -1 if night else 0
            p = SET.draw_element("certificate", E.describe("certificate", ELEMENTS["conformance"]), night, "wide")
            base = p.layers["base"]
            leather = RAMP["leather"][3]
            buckled = [q for q, c in base.items() if c == BRASS[5 + k] and base.get((q[0] + 4, q[1])) == leather
                       and base.get((q[0], q[1] + 1)) == BRASS[5 + k]]
            self.assertGreaterEqual(len(buckled), 8, "the frame of a buckle at the ribbon's start and the tag's")

    def test_the_placard_bears_the_touchmark(self):
        for eid in ("action", "grafana", "terraform-probes", "baselines-spec"):
            for night in (False, True):
                p = SET.draw_element("placard", E.describe("placard", ELEMENTS[eid]), night, "wide")
                at = mark_at(p, night)
                self.assertIsNotNone(at, (eid, night))
                x, y = at
                self.assertTrue(all(p.clear_of_words(x + i, y + j, x + i + 1, y + j + 1)
                                    for j, row in enumerate(A.MARK) for i, ch in enumerate(row) if ch != "."),
                                (eid, night, "and it lies on no word"))

    def test_a_counters_digits_have_an_ink_of_their_own_and_are_set_over_their_plates(self):
        vitals = ELEMENTS["vitals"]
        for night in (False, True):
            k = SET.ink(night)
            words = {k[role] for role in ("title", "shadow", "body", "muted", "rule", "accent", "tag_ink")}
            p = SET.draw_element("instruments", E.describe("instruments", vitals), night, "wide")
            svg = p.svg("t", "d", still=True)
            plate = svg.index(f'href="#{p.syms[(("stamp", ("cell", night)), "base")]}"')
            for dim in (False, True):
                ink = SET.counter_ink(night, dim)
                self.assertNotIn(ink, words, (night, dim))
                face = RAMP["iron"][3] if night else STEEL[4]
                self.assertGreaterEqual(contrast(ink, face), 4.5, (night, dim))
                self.assertLess(plate, svg.index(f'<g stroke="{ink}">'), (night, dim))

    def test_the_latest_release_hangs_as_a_brass_tag_and_a_planned_one_as_an_outline(self):
        history = ELEMENTS["history"]
        for night in (False, True):
            p = SET.draw_element("milestones", E.describe("milestones", history), night, "wide")
            k = -1 if night else 0
            brass = [(x, y) for (x, y), c in p.layers["base"].items() if c == RAMP["brass"][4 + k] and 70 < y < 90]
            self.assertTrue(20 <= len(brass) <= 120, "one tag of brass")
            latest = max(t[0] for t in p.tags)
            self.assertTrue(all(abs(x - latest) <= 5 for x, _ in brass), "and it is the one hung last")
            outline = STEEL[3 + k]
            self.assertIn(outline, {c for (x, y), c in p.layers["base"].items() if x > latest + 6 and 70 < y < 90},
                          "the planned release's empty tag beyond it")

    def test_a_helms_initials_read_on_its_faceplate(self):
        for night in (False, True):
            for ini in ("TG", "WW", "I"):
                p = Pix(40, 40)
                SET.avatar(p, 20, 20, 0, {"initials": ini, "name": "T", "n": 1}, night)
                letters = [b for b in p.words if b[1] >= 20]
                self.assertEqual(len(letters), 1)
                x0, y0, x1, y1 = letters[0]
                faces = {p.layers["base"].get((x, y)) for x in range(x0 + 1, x1 - 1) for y in range(y0 + 1, y1 - 1)}
                for face in faces:
                    self.assertGreaterEqual(contrast(COAL[0], face), 4.5, (night, ini, face))


class Badges(unittest.TestCase):
    def test_a_steel_strap_lies_along_every_badges_top_rows_with_the_letters_under_it(self):
        for style in BADGE_STYLES:
            for night in (False, True):
                p = SET.plate_badge(style, "License", "MIT", "scale", "night" if night else "day")
                top = {c for (x, y), c in p.layers["base"].items() if y == 0}
                self.assertIn(STEEL[3] if night else STEEL[4], top, (style, night))
                self.assertIn(RAMP["iron"][5] if night else C["white"], top, "a rivet's lit crown")
                self.assertTrue(all(y >= TOP for _, _, _, y, _ in p.uses["base"]), "the letters sit under the strap")
                self.assertEqual(SET.plate_colours("night" if night else "day")["dot"],
                                 SET.plate_colours("night" if night else "day")["paper"], "a plate has no dots")
            classic = SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                        SET.badge_states()["green"])
            h = STYLES[style]["h"]
            base = classic.layers["base"]
            self.assertTrue(any(base.get((x, h - 2)) == C["white"] for x in range(4)), "a rivet in the label's corner")
            self.assertTrue(any(base.get((x, h - 2)) == C["white"] for x in range(classic.w - 4, classic.w)),
                            "and in the value's")
            foot = {base.get((x, h - 1)) for x in range(3, classic.w - 3)}
            self.assertTrue(foot & {COAL[0], COAL[1]}, "the iron block's shadow along its foot")
            self.assertIn(RAMP["green"][1], foot, "and the enamel's bevel")


class Hand(unittest.TestCase):
    """The set is the medieval collection's November, drawn in the collection's hand."""

    def test_it_keeps_to_its_hand_as_the_months_design_and_kept_all_year(self):
        self.assertIsInstance(SET, CollectionSet)
        self.assertEqual(SET.collection, "medieval")
        self.assertEqual(check(SET), [])
        self.assertEqual(check(HELD), [])

    def test_its_words_are_in_the_hands_two_inks(self):
        for night in (False, True):
            k = SET.ink(night)
            self.assertEqual((k["body"], k["muted"]), (MEDIEVAL.body[night], MEDIEVAL.muted[night]), night)

    def test_its_plate_falls_in_the_hands_bands_a_cool_slate_by_day(self):
        """By day the hammered plate and a card's face fall in the hand's day band, the plate a cool slate with
        colour enough to be one; by night every band of the forge-lit plate falls in the hand's night band."""
        lo, hi, most = MEDIEVAL.day_ground
        for c in (C["plate"], C["fill_day"]):
            light, chroma, _ = lab(c)
            self.assertTrue(lo <= light <= hi and chroma <= most, (c, light, chroma))
        light, chroma, hue = lab(C["plate"])
        self.assertTrue(light >= 72 and chroma >= 6 and 220 <= hue <= 290, (light, chroma, hue))
        lo, hi, most = MEDIEVAL.night_ground
        for c in NIGHT_SKY:
            light, chroma, _ = lab(c)
            self.assertTrue(lo <= light <= hi and chroma <= most, (c, light, chroma))

    def test_every_flame_coal_ember_and_spark_burns_on_the_hands_flame(self):
        """The forge's fire and its coals, the sparks off the blade, the blade's heat, the embers rising across the
        night sheet and the coals glowing in a footer's floor are all tones of the hand's flame ramp."""
        flame = set(MEDIEVAL.ramp("flame"))
        self.assertEqual(FIRE, MEDIEVAL.ramp("flame"))

        def colours(q):
            return {c.split(":")[0] for layer in q.layers.values() for c in layer.values()}
        for night in (False, True):
            q = Pix(60, 40)
            A.coals(q, 10, 30, 30, night)
            A.flames(q, 20, 30, night, True)
            A.sparks(q, 40, 30, night, True)
            self.assertLessEqual(colours(q), flame, night)
            q = Pix(60, 40)
            A.blade(q, 5, 20, night, length=24)
            hot = colours(q) - set(STEEL) - set(IRON)
            self.assertTrue(hot and hot <= flame, (night, hot - flame))
        svg = SET.header("H1", HEADER, DARK, True, True)
        rising = re.findall(r'<g id="em(?:far|near)g">(.*?)</g><use', svg)
        self.assertTrue(rising, "the embers")
        self.assertLessEqual({c.upper() for c in re.findall(r"#[0-9A-Fa-f]{6}", "".join(rising))}, flame)

    def test_the_smith_is_drawn_to_the_hands_canon_on_its_skin(self):
        """The smith stands twenty-eight rows tall, his head about a fifth of it, his eye a single dark unit; his
        face and his arms are on the hand's skin by day and by night."""
        self.assertEqual(RAMP["skin"], MEDIEVAL.ramp("skin1"))
        self.assertTrue(24 <= len(A.SMITH) <= 28)
        head = [j for j, row in enumerate(A.SMITH) if set(row) & set("hRse") and not set(row) & set("bTA")]
        self.assertAlmostEqual(len(head) / len(A.SMITH), 0.2, delta=0.04)
        self.assertEqual(sum(row.count("e") for row in A.SMITH), 1)
        skin = set(MEDIEVAL.ramp("skin1"))
        for night in (False, True):
            q = Pix(40, 40)
            A.smith(q, 14, 38, night, True)
            drawn = {c for layer in q.layers.values() for c in layer.values()}
            self.assertTrue(drawn & skin, night)
            self.assertFalse(drawn & (set(RAMP["flame"]) - set(FIRE)), (night, "no eye glowing like a coal"))

    def test_its_motion_keeps_the_hands_timing(self):
        """The smith's swing and the bellows' breath, with the fire and the sparks that follow them, loop in 4 to 8
        seconds, as figures' loops do, as do the chimney's smoke and the quench bucket's steam; a title's glint
        passes on the hand's period; the embers rise across the night sheet in a slow sweep of 24 to 48 seconds and
        flicker on the engine's cadence; every flicker and twinkle is the engine's."""
        self.assertTrue(4 <= A.SWING <= 8 and 4 <= A.BREATH <= 8 and A.SWING != A.BREATH)
        self.assertTrue(all(24 <= seconds <= 48 for _, _, seconds, _ in A.RISE))
        for night in (False, True):
            p = HELD.h1(HEADER, night, True)
            seen = set()
            for name, (_, _, anim) in p.meta.items():
                if not anim or not (p.layers[name] or p.uses[name] or p.shapes[name]):
                    continue
                if anim[0] == "seq":
                    dur = anim[3]
                    self.assertTrue(4 <= dur <= 8 or dur == MEDIEVAL.glint, (night, name, dur))
                    seen.add(dur)
                else:
                    self.assertIn(anim[0], BLINKS, (night, name))
            self.assertIn(MEDIEVAL.glint, seen, (night, "the title's glint"))
        svg = SET.header("H1", HEADER, DARK, True, True)
        self.assertIn(f'dur="{BLINKS["flicker"][2]:g}s"', svg, "the embers flicker on the engine's cadence")

    def test_the_marks_box_is_clear_of_the_scene_and_the_mail_parts_for_it(self):
        """The box the month's mark takes at the top centre, and two units round it, is clear of the scene in every
        header the shared contents draw, wide and on a phone, by day and by night. Drawn as the month's design, the
        mail across the top hangs in two strips either side of it, as it does for a sign the page chose; kept all
        year without one, in one."""
        n = MEDIEVAL.mark_size
        scene, narrow, under = Forge.scene, Forge.scene_narrow, Forge.scene_under
        found = []

        def watch(p, draw):
            before = {name: set(cells) for name, cells in p.layers.items()}
            out = draw()
            found.append((p, {q for name, cells in p.layers.items() for q in set(cells) - before.get(name, set())}))
            return out
        spies = {"scene": lambda self, d, p, r, ni, m: watch(p, lambda: scene(self, d, p, r, ni, m)),
                 "scene_narrow": lambda self, d, p, y, ni: watch(p, lambda: narrow(self, d, p, y, ni)),
                 "scene_under": lambda self, d, p, y0, y1, ni: watch(p, lambda: under(self, d, p, y0, y1, ni))}
        for name, (h, _) in contents(KEY).items():
            for code in ("H1", "H2", "H3"):
                for night in (False, True):
                    for wide in (True, False):
                        found.clear()
                        with mock.patch.multiple(Forge, **spies):
                            if wide:
                                p = {"H1": HELD.h1, "H2": HELD.h2, "H3": HELD.h3}[code](h, night, True)
                            else:
                                p = {"H1": HELD.h1_narrow, "H2": HELD.h2_narrow, "H3": HELD.h3_narrow}[code](h, night)
                        x0, y0 = p.w // 2 - n // 2, MARK_Y - n // 2
                        cells = {q for d, new in found if d is p for q in new}
                        inside = [q for q in cells if x0 - 2 <= q[0] < x0 + n + 2 and y0 - 2 <= q[1] < y0 + n + 2]
                        self.assertEqual(inside[:4], [], (name, code, night, wide))
        for held, strips in ((HELD, 2), (SET, 1), (SET.signed("leo"), 2)):
            for w in (WIDE, NARROW):
                with mock.patch.object(A, "mail", wraps=A.mail) as mail:
                    held.h1(HEADER, False, True) if w == WIDE else held.h1_narrow(HEADER, False)
                self.assertEqual(mail.call_count, strips, (w, strips))
                if strips == 2:
                    x0 = w // 2 - n // 2
                    (left, right) = mail.call_args_list
                    self.assertLessEqual(left.args[2], x0 - 2)
                    self.assertGreaterEqual(right.args[1], x0 + n + 2)


# ------------------------------------------------------------------ the checks every registered set passes
class SharedBanners(unittest.TestCase):
    def test_every_file_is_the_sets_well_formed_linted_and_deterministic(self):
        drawn = {(n, c, fn): svg for n, c, fn, svg in every_banner()}
        for (name, code, fn), svg in drawn.items():
            minidom.parseString(svg)
            self.assertIn(f"<!--{KIT} v{KIT_VERSION} {KEY} ", svg, (name, fn))
            self.assertNotIn("<text", svg)
            for ch in DASHES:
                self.assertNotIn(ch, svg)
            cap = BUDGET["link"] if fn.startswith("link-") else budget("header" if code.startswith("H") else "footer")
            self.assertEqual(lint(svg, budget=cap, tokens=SET.tokens), [], (name, fn))
        for name, code, fn, svg in draw_banners():
            self.assertEqual(svg, drawn[(name, code, fn)], (name, fn))

    def test_files_are_the_kits_sizes(self):
        for name, code, fn, svg in every_banner():
            w = int(re.search(r'width="(\d+)"', svg).group(1))
            if fn.startswith("link-"):
                self.assertLess(w, 300, fn)
            else:
                self.assertEqual(w, 360 if "narrow" in fn else 830, (name, fn))

    def test_only_a_wide_moving_header_moves(self):
        for name, code, fn, svg in every_banner():
            if "still" in fn or "narrow" in fn or fn.startswith(("footer", "link")):
                self.assertNotIn("<animate", svg, (name, fn))
        h, _ = contents(KEY)["repository"]
        self.assertIn("<animate", SET.header("H2", h, DAY, True, True))

    def test_text_colours_hold_4_5_on_the_plate_and_every_band_of_the_night(self):
        for night in (False, True):
            k = SET.ink(night)
            p = Pix(415, 200)
            grounds = {SET.bg_at(p, night, y) for y in range(p.h)}
            for role in ("title", "body", "muted", "accent"):
                for ground in grounds:
                    self.assertGreaterEqual(contrast(k[role], ground), 4.5, (night, role, ground))
            self.assertGreaterEqual(contrast(k["tag_ink"], k["tag"]), 4.5, (night, "tag"))

    def test_a_file_too_heavy_is_drawn_lighter_then_still_and_stays_the_sets(self):
        h, _ = contents(KEY)["repository"]
        full = SET.header("H2", h, DARK, True, True)
        self.assertIn("<animate", full)
        with mock.patch.dict(BUDGET, {"header": len(full.encode("utf-8")) - 1}):
            lighter = SET.header("H2", h, DARK, True, True)
        self.assertLess(len(lighter), len(full))
        self.assertIn("<animate", lighter, "a lighter drawing keeps its motion while it fits")
        self.assertIn(f"{KEY} H2 dark-->", lighter)
        with mock.patch.dict(BUDGET, {"header": 1000}):
            last = SET.header("H2", h, DARK, True, True)
        self.assertNotIn("<animate", last, "motion is the last thing to go")
        self.assertFalse(SET._lite, "the set is left drawing lighter")
        most, _ = contents(KEY)["most"]
        for code in ("H1", "H2", "H3"):
            for theme in (DAY, DARK):
                svg = SET.header(code, most, theme, True, True)
                self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"], (code, theme["name"]))

    def test_ordinary_content_fits_at_full_weight_with_its_motion_and_room_to_spare(self):
        """Ordinary pages, drawn as the month's design with the month's mark, come out at full weight with their
        motion and at least 1,500 bytes under the budget; their footers too."""
        ordinary = {name: contents(KEY)[name][0] for name in ("kit", "repository", "profile", "least")}
        ordinary.update({f"proof {name}": h for name, h in PROOF.items()})
        for name, h in ordinary.items():
            for code in ("H1", "H2", "H3"):
                for theme in (DAY, DARK):
                    for wide, motion in ((True, True), (True, False), (False, False)):
                        where = (name, code, theme["name"], wide, motion)
                        svg = HELD.header(code, h, theme, wide, motion)
                        with mock.patch.dict(BUDGET, {"header": 10 ** 9}):
                            self.assertEqual(svg, HELD.header(code, h, theme, wide, motion), (where, "at full weight"))
                        self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"] - 1500, where)
        for name in ("kit", "repository", "profile", "least"):
            ft = contents(KEY)[name][1]
            for code in ("F1", "F2"):
                for theme in (DAY, DARK):
                    for wide in (True, False):
                        svg = HELD.footer(code, ft, theme, wide, False)
                        self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["footer"] - 1500, (name, code, wide))


class SharedElements(unittest.TestCase):
    def test_every_element_is_the_sets_linted_deterministic_and_the_kits_files(self):
        for eid, d in ELEMENTS.items():
            kind = d["kind"]
            described = E.describe(kind, d)
            for variant in E.variants(kind, d):
                for theme in (DAY, DARK):
                    svg = SET.element(kind, described, theme, variant)
                    minidom.parseString(svg)
                    self.assertEqual(svg, SET.element(kind, described, theme, variant), (eid, variant))
                    self.assertIn(f"<!--{KIT} v{KIT_VERSION} {KEY} elements {kind} ", svg, (eid, variant))
                    self.assertEqual(lint(svg, budget=BUDGET[E.KINDS[kind][2]], tokens=SET.tokens), [], (eid, variant))
                    w = int(re.search(r'width="(\d+)"', svg).group(1))
                    wanted = (404 if kind == "placard" or variant == "half" or
                              (variant == "narrow" and kind in ("roster", "certificate"))
                              else 360 if variant == "narrow" else 830)
                    self.assertEqual(w, wanted, (eid, variant))

    def test_the_half_page_pair_is_drawn_level(self):
        pair = {eid: ELEMENTS[eid] for eid in ("contributors", "conformance")}
        tall = max(SET.element_height(d["kind"], d) for d in pair.values())
        heights = set()
        for d in pair.values():
            svg = SET.element(d["kind"], E.describe(d["kind"], d), DAY, "half", height=tall)
            heights.add(re.search(r'height="(\d+)"', svg).group(1))
        self.assertEqual(len(heights), 1)

    def test_odd_data_is_drawn_whole(self):
        bare = {"kind": "roster", "subject": "x/y", "people": [
            {"name": "A PERSON WITH A NAME FAR LONGER THAN A COLUMN", "handle": "@" + "h" * 30, "initials": "AP",
             "n": 3, "first": "1 JAN 2020", "last": "31 DEC 2026"}]}
        svg = SET.element("roster", E.describe("roster", bare), DAY, "wide")
        self.assertEqual(lint(svg, budget=BUDGET["sheet"], tokens=SET.tokens), [])
        cert = dict(ELEMENTS["conformance"], name="an-extraordinarily-long-name",
                    ring_bottom="V12 · VERIFIED 31 DECEMBER 2026 AT LENGTH")
        for variant in ("wide", "half"):
            svg = SET.element("certificate", E.describe("certificate", cert), DARK, variant)
            self.assertEqual(lint(svg, budget=BUDGET["sheet"], tokens=SET.tokens), [], variant)


class SharedBadges(unittest.TestCase):
    def badge(self, style, **kw):
        args = dict(style=style, label="Build", message="Passing", icon="pulse", label_hex=PALETTE["black"],
                    message_hex=PALETTE["blue"], live=False, state=None, reserve=(), rels=["static/b.svg"],
                    stamp=STAMP)
        args.update(kw)
        return SET.badge(**args)

    def check_file(self, svg, px_height, what):
        self.assertEqual(BD.lint(svg), [], what)
        self.assertEqual(colours(svg, SET.tokens), [], what)
        minidom.parseString(svg)
        self.assertEqual(int(re.search(r'height="(\d+)"', svg).group(1)), px_height, what)

    def test_every_style_classic_plate_and_live_is_the_kits_height_and_files(self):
        for style in BADGE_STYLES:
            one = self.badge(style)
            self.assertEqual(list(one), ["static/b.svg"])
            self.check_file(one["static/b.svg"], HEIGHTS[style], style)
            two = self.badge(PLATE + style, rels=["static/b.svg", "static/b-dark.svg"])
            self.assertEqual(list(two), ["static/b.svg", "static/b-dark.svg"])
            self.assertNotEqual(*two.values())
            for rel, svg in two.items():
                self.check_file(svg, HEIGHTS[style], (style, rel))
            for state in STATES:
                for form in (style, PLATE + style):
                    live = self.badge(form, live=True, state=state, label_hex=PALETTE["gold"],
                                      message_hex=PALETTE[state], rels=["dynamic/b.svg"])
                    self.assertEqual(list(live), ["dynamic/b.svg"])
                    self.check_file(live["dynamic/b.svg"], HEIGHTS[style], (form, state))

    def test_a_live_plate_keeps_its_width_whatever_it_says(self):
        widths = set()
        for state, message in (("green", "Passing"), ("red", "Failing"), ("slate", "No Data")):
            svg = self.badge(PLATE + "flat", live=True, state=state, message=message,
                             reserve=("Passing", "Failing", "No Data"), rels=["dynamic/b.svg"])["dynamic/b.svg"]
            widths.add(re.search(r'width="(\d+)"', svg).group(1))
        self.assertEqual(len(widths), 1)

    def test_every_letter_holds_4_5_on_its_block(self):
        pairs = [("label", *SET.badge_label()), ("gold", *SET.badge_gold())]
        pairs += [(f"state {s}", *SET.badge_states()[s]) for s in STATES]
        pairs += [(f"swatch {n}", bg, ink) for n, (bg, ink, _) in SET.badge_swatches().items()]
        for mode in ("day", "night"):
            k = SET.plate_colours(mode)
            pairs += [(f"{mode} block", k["block"], k["letters"]), (f"{mode} paper", k["paper"], k["ink"]),
                      (f"{mode} dot", k["dot"], k["ink"])]
        k = SET.plate_colours("live")
        pairs += [("live paper", k["paper"], k["ink"]), ("live dot", k["dot"], k["ink"])]
        for what, ground, ink in pairs:
            self.assertGreaterEqual(contrast(ink, ground), 4.5, what)

    def test_the_swatches_cover_every_hue_family_a_written_colour_can_come_in(self):
        swatches = SET.badge_swatches()
        taken = {name: nearest(PALETTE[name], swatches)
                 for name in ("red", "orange", "yellow", "green", "blue", "purple", "white", "black", "slate", "brown")}
        self.assertEqual(taken["red"], "ember")
        self.assertEqual(taken["green"], "enamel")
        self.assertEqual(taken["blue"], "lapis")
        self.assertEqual(taken["purple"], "plum")
        self.assertEqual(taken["white"], "steel")
        self.assertEqual(taken["black"], "iron")
        self.assertIn(taken["brown"], ("leather", "oak"))
        self.assertIn(taken["orange"], ("amber", "brass"))
        self.assertIn(taken["yellow"], ("amber", "brass"))
        self.assertGreaterEqual(len(set(taken.values())), 9)

    def test_a_written_colour_takes_the_nearest_the_set_has(self):
        for name, (block, _, _) in SET.badge_swatches().items():
            svg = self.badge("flat", message_hex=block)["static/b.svg"]
            self.assertIn(block, svg, name)

    def test_what_the_sets_letters_cannot_draw_is_left_to_the_kit(self):
        self.assertIsNone(self.badge("flat", message="中文"))


if __name__ == "__main__":
    unittest.main()
