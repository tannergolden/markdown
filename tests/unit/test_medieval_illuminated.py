# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Illuminated set: March's design in the medieval collection, not a holiday, so the checks every
registered set shares run over it here; its collection's hand, which it keeps to as its month's design and
kept all year (its inks, its grounds, its flame, its skins, its motion and the month's mark); its composition,
the heroes of its section and its strip standing as tall as the hand asks; and its own rules, which those
checks cannot know: a candle burns only by night, in a wide header that moves its flame flickers and the
border's gold beads catch the light; a title is gold leaf on a panel behind a decorated initial, every band
of the leaf reading on the panel; its flourish, the creatures in the margin and the leaves on a rule never
touch a word; every phone header stands a scene, and a phone's section and strip stand their heroes under
their words, forty-four rows tall and more, whatever their titles; the most a page can say keeps its whole
scene and its motion within the budget; and its inks and swatches hold 4.5:1."""
from __future__ import annotations

import contextlib
import datetime as dt
import re
import unittest
import xml.dom.minidom as minidom
from unittest import mock

from tests import support
from tests.unit.test_holiday_sets import DASHES, HEIGHTS, STAMP, contents

from domain import KIT, KIT_VERSION
from domain import holidays as H
from domain.badges import data as BD
from domain.canvas import BUDGET, DARK, DAY, colours, lint
from domain.elements import data as ED
from domain.elements import draw as E
from domain.collections.hand import MEDIEVAL as HAND, check, lab
from domain.holidays.designs import NARROW, WIDE
from domain.holidays.designs.badges import PLATE, STATES, STYLES as BADGE_STYLES, TOP, inside, nearest
from domain.holidays.designs.banners import MARK_Y
from domain.collections.medieval_illuminated import (BOOK, PERCHES, QUILL_TALL, QUILL_TOP, SET, UNDER, VINE_SAG,
                                                     VINE_SPAN)
from domain.collections.medieval_illuminated import art as A
from domain.collections.medieval_illuminated.palette import C, NIGHT_SKY, RAMP, X
from domain.holidays.pixel import BLINKS, Pix, contrast, num
from domain.palette import PALETTE
from infra.yaml_reader import loads

support.install()
KEY = SET.key
HELD = SET.on(dt.date(2026, 3, 1))      # the design drawn as March's, the month's mark at the top of its headers
SPECIMEN = loads((support.ROOT / "tests" / "fixtures" / "driftmark" / ".github" / "markdown.yaml")
                 .read_text(encoding="utf-8"))
ELEMENTS = ED.merged(ED.check(SPECIMEN["elements"]), {}, subject="driftmark/driftmark", today="2026-09-25")
HEADER = contents(KEY)["repository"][0]
# The tones only the margin's creatures and the scribe's things are painted in: never a word's backing.
SPRITE_TONES = frozenset(RAMP["verdigris"] + RAMP["wood"] + RAMP["habit"] + RAMP["skin0"] + RAMP["skin1"]
                         + RAMP["skin2"] + RAMP["ash"])
FLAME = frozenset(HAND.ramp("flame"))


def banners() -> dict:
    """Every banner file the set draws for the shared contents: {(content, code, name): svg}."""
    out = {}
    for name, (h, f) in contents(KEY).items():
        for code in ("H1", "H2", "H3"):
            for suffix, wide, motion, theme in (("day", True, True, DAY), ("dark", True, True, DARK),
                                                 ("still-day", True, False, DAY), ("still-dark", True, False, DARK),
                                                 ("narrow-day", False, False, DAY),
                                                 ("narrow-dark", False, False, DARK)):
                out[(name, code, f"header-{suffix}.svg")] = SET.header(code, h, theme, wide, motion)
        for code in ("F1", "F2"):
            for suffix, wide, theme in (("day", True, DAY), ("dark", True, DARK), ("narrow-day", False, DAY),
                                        ("narrow-dark", False, DARK)):
                out[(name, code, f"footer-{suffix}.svg")] = SET.footer(code, f, theme, wide, False)
        for i, label in enumerate(f.link_labels):
            for theme in (DAY, DARK):
                out[(name, "F1", f"link-{i}-{theme['name']}.svg")] = SET.link(label, theme, i)
    return out


DRAWN: dict = {}


def every_banner() -> dict:
    if not DRAWN:
        DRAWN.update(banners())
    return DRAWN


def as_the_kit_draws(code: str, h, theme: dict) -> tuple:
    """A wide moving header's file as the kit draws it for March, the month's mark and all, and the drawing it
    was written from: the last one drawn, at full weight or made lighter to fit its budget (see
    `Holiday._fitted`)."""
    kept, name = [], {"H1": "h1", "H2": "h2", "H3": "h3"}[code]
    real = getattr(HELD, name)
    with mock.patch.object(HELD, name, lambda *a: kept.append(real(*a)) or kept[-1]):
        svg = HELD.header(code, h, theme, True, True)
    return svg, kept[-1]


def pixels(p: Pix, kind: str, solid: bool = False) -> set:
    """Every pixel on the layers whose names begin with `kind`, as (where, colour); only the solid ones when
    `solid`."""
    return {(k, c) for n in p.layers if n.startswith(kind) for k, c in p.layers[n].items() if not solid or ":" not in c}


def without(*hooks):
    """The set's `hooks` drawing nothing, for as long as the context lasts."""
    stack = contextlib.ExitStack()
    for hook in hooks:
        stack.enter_context(mock.patch.object(type(SET), hook, lambda *a, **k: None))
    return stack


def elements() -> dict:
    """Every element file the set draws for the specimen, as the kit asks for them: {name: svg}."""
    halves = [SET.element_height(d["kind"], d) for d in ELEMENTS.values() if E.variants(d["kind"], d) == ("half",)]
    half = max(halves) if halves else None
    out = {}
    for eid, d in ELEMENTS.items():
        kind = d["kind"]
        for variant in E.variants(kind, d):
            for theme in (DAY, DARK):
                name = ED.file_name(eid, variant, theme["name"])
                out[name] = SET.element(kind, E.describe(kind, d), theme, variant, half)
    return out


class Registry(unittest.TestCase):
    def test_the_set_is_a_theme_and_not_a_holiday_on_the_calendar(self):
        self.assertEqual((SET.key, SET.name), ("medieval-illuminated", "Illuminated"))
        self.assertNotIn(KEY, H.SETS)
        self.assertIsNone(H.drawn_by(KEY))
        self.assertTrue(SET.tokens)
        self.assertTrue(all(re.fullmatch(r"#[0-9A-F]{6}", t) for t in SET.tokens))


class Banners(unittest.TestCase):
    def test_every_file_is_the_sets_well_formed_linted_and_deterministic(self):
        drawn = every_banner()
        for (name, code, fn), svg in drawn.items():
            minidom.parseString(svg)
            self.assertIn(f"<!--{KIT} v{KIT_VERSION} {KEY} ", svg, (name, fn))
            self.assertNotIn("<text", svg)
            for ch in DASHES:
                self.assertNotIn(ch, svg)
            kind = "link" if fn.startswith("link-") else ("footer" if code.startswith("F") else "header")
            budget = BUDGET[kind]
            self.assertEqual(lint(svg, budget=budget, tokens=SET.tokens), [], (name, fn))
        for key, svg in banners().items():
            self.assertEqual(svg, drawn[key], key)

    def test_files_are_the_kits_sizes(self):
        for (name, code, fn), svg in every_banner().items():
            w = int(re.search(r'width="(\d+)"', svg).group(1))
            if fn.startswith("link-"):
                self.assertLess(w, 300, fn)
            else:
                self.assertEqual(w, 360 if "narrow" in fn else 830, (name, fn))

    def test_only_a_wide_moving_header_moves_and_the_kits_own_does(self):
        for (name, code, fn), svg in every_banner().items():
            if "still" in fn or "narrow" in fn or fn.startswith(("footer", "link")):
                self.assertNotIn("<animate", svg, (name, fn))
        for code in ("H1", "H2", "H3"):
            for theme in (DAY, DARK):
                self.assertIn("<animate", SET.header(code, HEADER, theme, True, True), (code, theme["name"]))

    def test_text_colours_hold_4_5_on_the_vellum_by_day_and_every_band_by_night(self):
        for night in (False, True):
            k = SET.ink(night)
            p = Pix(WIDE, 200)
            grounds = {SET.bg_at(p, night, y) for y in range(p.h)}
            self.assertEqual(grounds, {C["paper"]} if not night else set(NIGHT_SKY))
            for role in ("title", "body", "muted", "accent"):
                for ground in grounds:
                    self.assertGreaterEqual(contrast(k[role], ground), 4.5, (night, role, ground))
            self.assertGreaterEqual(contrast(k["tag_ink"], k["tag"]), 4.5, night)

    def test_the_nights_bands_are_drawn_where_bg_at_says_they_are(self):
        for h in (35, 43, 91, 106, 141, 173, 253):
            p = Pix(WIDE, h)
            A.paper(p, True)
            edges = A.band_edges(0, h)
            for i in range(len(NIGHT_SKY)):
                for y in range(edges[i], edges[i + 1]):
                    self.assertEqual(A.bg_at(p, True, y), NIGHT_SKY[i], (h, y))

    def test_a_file_too_heavy_is_drawn_lighter_then_still_and_stays_the_sets(self):
        full = SET.header("H2", HEADER, DARK, True, True)
        self.assertIn("<animate", full)
        with mock.patch.dict(BUDGET, {"header": len(full.encode("utf-8")) - 1}):
            lighter = SET.header("H2", HEADER, DARK, True, True)
        self.assertLess(len(lighter), len(full))
        self.assertIn("<animate", lighter, "a lighter drawing keeps its motion while it fits")
        self.assertIn(f"{KEY} H2 dark-->", lighter)
        with mock.patch.dict(BUDGET, {"header": 1000}):
            last = SET.header("H2", HEADER, DARK, True, True)
        self.assertNotIn("<animate", last, "motion is the last thing to go")
        self.assertFalse(SET._lite, "the set is left drawing lighter")
        most, _ = contents(KEY)["most"]
        for code in ("H1", "H2", "H3"):
            for theme in (DAY, DARK):
                svg = SET.header(code, most, theme, True, True)
                self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"], (code, theme["name"]))

    def test_ordinary_content_moves_at_full_weight(self):
        """The kit's own lines and the samples fit the budget with their flourish, their glow, their motion and
        the month's mark, with a kilobyte and a half to spare: only the most a page can say is drawn lighter."""
        for name, (h, _) in contents(KEY).items():
            if name == "most":
                continue
            for code in ("H1", "H2", "H3"):
                for theme in (DAY, DARK):
                    p = {"H1": HELD.h1, "H2": HELD.h2, "H3": HELD.h3}[code](h, bool(theme["dark"]), True)
                    svg = p.svg(h.spoken_title(), h.spoken(), still=False, stamp=HELD.stamp(f"{code} {theme['name']}"))
                    self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"] - 1500, (name, code, theme["name"]))
                    self.assertEqual(HELD.header(code, h, theme, True, True), svg, (name, code, "drawn at full weight"))

    def test_the_most_a_page_can_say_keeps_its_whole_scene_and_its_motion(self):
        """The most content's wide H1 and H2, day and night, drawn as the kit draws them for March, fit the
        budget and still move. A drawing made lighter to fit keeps every piece of the scene in the same pixels:
        the monk at his desk, his quill, his shelf of books, the candle and its flame, the wyvern and its wing,
        the hare and its notes, the snail, the great book on its lectern, the books, every bird on the vines;
        the title's gold leaf, its glow, its initial, its flourish and the glint across it; the border's
        twinkling beads; the month's mark; and the candle's light, of which only the faintest, outermost ring
        is left off."""
        most, _ = contents(KEY)["most"]
        lighter = 0
        for code in ("H1", "H2"):
            for theme in (DAY, DARK):
                night, what = bool(theme["dark"]), (code, theme["name"])
                svg, p = as_the_kit_draws(code, most, theme)
                self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"], what)
                self.assertIn("<animate", svg, what)
                full = {"H1": HELD.h1, "H2": HELD.h2}[code](most, night, True)
                lighter += p.lite
                if code == "H1":
                    self.assertIn(RAMP["habit"][4], p.layers["base"].values(), (what, "the monk"))
                    self.assertIn(RAMP["verdigris"][0], p.layers["base"].values(), (what, "the wyvern"))
                self.assertEqual(p.layers["base"], full.layers["base"], (what, "every figure, prop and beast"))
                for layer in ("panel", "near"):
                    self.assertEqual(p.layers.get(layer), full.layers.get(layer), (what, "the initial, the flourish"))
                self.assertEqual(p.shapes["panel"], full.shapes["panel"], (what, "the panels and their diaper"))
                for layer in full.layers:
                    if layer.startswith(("qu", "wy", "nt", "tw")):
                        self.assertEqual(p.layers[layer], full.layers[layer], (what, layer, "what moves"))
                self.assertEqual(pixels(p, "bd"), pixels(full, "bd"), (what, "every bird, both its frames"))
                self.assertEqual(pixels(p, "fl", True), pixels(full, "fl", True), (what, "every flame"))
                self.assertEqual(len(p.raws), len(full.raws), (what, "the glint across every line of the title"))
                self.assertIn('id="paleaf', svg, what)
                self.assertEqual(bool(p.uses["haze"]), night, (what, "the gold glows by night"))
                self.assertEqual(len(p.lamps), len(full.lamps), (what, "every candle"))
                if night:
                    self.assertTrue(any("ellipse" in s for n in p.shapes if n.startswith("fb") for s in p.shapes[n]),
                                    (what, "the light pooled on the vellum"))
                    lit = {k for k, _ in pixels(p, "fl")}
                    self.assertTrue(lit <= {k for k, _ in pixels(full, "fl")}, (what, "only the light is thinned"))
                    self.assertGreater(len(lit), 100, (what, "the candle's light on what stands near it"))
        self.assertEqual(lighter, 4, "the H1s and the H2s are drawn lighter, and keep it all")


class Night(unittest.TestCase):
    def test_a_candle_burns_only_by_night(self):
        """The candles of H1 and H2, of H1 on a phone and of every footer burn by night; no day file has a
        flame, and a link has no candle."""
        for (name, code, fn), svg in every_banner().items():
            if fn.startswith("link"):
                continue
            lit = any(c in svg for c in FLAME)
            notes = code == "F1" and bool(contents(KEY)[name][1].get("closing"))   # F1 has a candle by its notes
            if "dark" in fn and (code in ("H1", "F2") or notes or (code == "H2" and "narrow" not in fn)):
                self.assertTrue(lit, (name, fn))
            elif "day" in fn:
                self.assertFalse(lit, (name, fn))
        foot = next(f for _, (_, f) in contents(KEY).items() if f.get("closing"))
        for night in (False, True):
            p = SET.h1(HEADER, night, True)
            self.assertEqual(bool(p.lamps), night, "the candle lights what stands near it only when it burns")
            for draw in (SET.f1, SET.f2, SET.f1_narrow, SET.f2_narrow):
                p = draw(foot, night)
                self.assertEqual(bool(p.lamps), night, (draw.__name__, "a footer's candle too"))
                pool = [s for s in p.shapes.get("fb0", []) if "ellipse" in s]
                self.assertEqual(bool(pool), night, (draw.__name__, "its light pooled on the cell"))

    def test_in_a_moving_header_the_flame_flickers_and_the_golds_beads_catch_the_light(self):
        p = SET.h1(HEADER, True, True)
        self.assertTrue(any(name.startswith("fl") and p.layers[name] for name in p.layers), "the flame flickers")
        self.assertTrue(any(name.startswith("tw") and p.layers[name] for name in p.layers), "twinkling beads")
        beads = {q for name in p.layers if name.startswith("tw") for q in p.layers[name]}
        self.assertTrue(all(y in (1, p.h - 3) or x in (1, p.w - 3) for x, y in beads), "every bead lies on the border")
        still = SET.h1(HEADER, True, False)
        self.assertFalse(any(name.startswith("tw") for name in still.layers), "a still header has no beads twinkling")
        self.assertNotIn("<animate", still.svg("t", "d", still=True))
        day = SET.h1(HEADER, False, True)
        self.assertFalse(any(n.startswith("fl") and day.layers[n] for n in day.layers), "nothing flickers by day")


class Titles(unittest.TestCase):
    def test_a_title_is_gold_leaf_on_a_panel_behind_one_decorated_initial(self):
        for night in (False, True):
            ground, other = A.GROUNDS[night]
            for code, draw in (("H1", SET.h1), ("H2", SET.h2), ("H3", SET.h3)):
                p = draw(HEADER, night, True)
                shapes = "".join(p.shapes["panel"])
                self.assertEqual(shapes.count(f'fill="{ground[1]}"'), 1, (code, night, "one panel"))
                self.assertEqual(shapes.count(f'fill="{other[2]}"'), 1, (code, night, "one initial's square"))
                svg = p.svg("t", "d")
                self.assertIn('id="paleaf', svg, "the letters are painted in gold leaf")
            # A two-line title: a panel a line, the initial on the first line only.
            long = HEADER.with_(title="an-organisation-with-a-long-name/and-a-long-repository")
            p = SET.h1(long, night, True)
            shapes = "".join(p.shapes["panel"])
            self.assertGreaterEqual(shapes.count(f'fill="{ground[1]}"'), 2, night)
            self.assertEqual(shapes.count(f'fill="{other[2]}"'), 1, night)

    def test_every_band_of_the_leaf_reads_on_the_panel(self):
        for night in (False, True):
            ground = A.GROUNDS[night][0][1]
            for scale in (1, 2, 3, 4):
                for r in range(7 * scale):
                    for c in range(A.LEAF_PAINT.period):
                        gold = A.leaf_fill(r, c, scale, night)
                        self.assertIn(gold, RAMP["gold"])
                        self.assertGreaterEqual(contrast(gold, ground), 4.5, (night, scale, r, c))

    def test_the_flourish_grows_where_there_is_room_and_never_over_a_word_or_below_the_panel(self):
        for night in (False, True):
            for code, draw in (("H1", SET.h1), ("H2", SET.h2), ("H3", SET.h3)):
                p = draw(HEADER, night, True)
                sprig = p.layers.get("near", {})
                self.assertTrue(sprig, (code, night, "the kit's own title has room for a flourish"))
                foot = max(int(re.search(r'y="(\d+)" width="\d+" height="(\d+)"', s).group(1))
                           + int(re.search(r'height="(\d+)"', s).group(1)) for s in p.shapes["panel"])
                for (x, y) in sprig:
                    self.assertTrue(p.clear_of_words(x, y, x + 1, y + 1), (code, night, x, y))
                    self.assertLess(y, foot, (code, night, x, y, "nothing hangs below the panel, where the tagline is"))
            # A word in the margin leaves no room for one.
            p = Pix(WIDE, 100)
            p.text(20, 30, "x", C["ink"])
            self.assertFalse(A.room(p, 12, 24, 30, 44))
            self.assertTrue(A.room(p, 40, 24, 58, 44))
            self.assertFalse(A.room(p, 2, 24, 20, 44), "nor does the border")

    def test_the_placard_opens_with_a_decorated_initial(self):
        d = E.describe("placard", ELEMENTS["action"])
        for night in (False, True):
            p = SET.placard(d, night)
            ground, other = A.GROUNDS[night]
            self.assertIn(f'fill="{other[2]}"', "".join(p.shapes["panel"]), night)


class Margins(unittest.TestCase):
    def test_no_creature_or_leaf_sits_on_a_word(self):
        for name, (h, _) in contents(KEY).items():
            for code, wide_draw, narrow_draw in (("H1", SET.h1, SET.h1_narrow), ("H2", SET.h2, SET.h2_narrow),
                                                 ("H3", SET.h3, SET.h3_narrow)):
                for night in (False, True):
                    for p in (wide_draw(h, night, True), narrow_draw(h, night)):
                        for layer, cells in p.layers.items():
                            if layer in ("panel", "pool") or layer.startswith(("fl", "tw")):
                                continue
                            for (x, y), c in cells.items():
                                if c in SPRITE_TONES:
                                    where = (name, code, night, layer, x, y)
                                    self.assertTrue(p.clear_of_words(x, y, x + 1, y + 1), where)

    def test_the_wyvern_coils_in_the_margin_of_every_h1_and_beats_its_wing_in_a_moving_one(self):
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                p = SET.h1(h, night, True)
                self.assertTrue(any(n.startswith("wy") for n in p.layers), (name, night))
                still = SET.h1(h, night, False)
                self.assertFalse(any(n.startswith("wy") for n in still.layers), (name, night))
                self.assertIn(RAMP["verdigris"][0], still.layers["base"].values(), (name, night, "its outline"))

    def test_birds_perch_on_the_vine_where_it_hangs_lowest_and_on_the_vine_in_the_margin(self):
        p = SET.h1(HEADER, False, True)
        perches = [name for name in p.layers if name.startswith("bd")]
        above = [name for name in perches if max(y for _, y in p.layers[name]) <= 10]
        self.assertEqual(len(above), 6, "three birds on the vine across the top, two frames each")
        lows = [A.vine_low(5, WIDE - 5, VINE_SPAN, VINE_SAG, i)[0] for i, _, _ in PERCHES]
        for name in above:
            xs = {x for x, _ in p.layers[name]}
            ys = {y for _, y in p.layers[name]}
            self.assertTrue(all(4 <= y <= 10 for y in ys), "under the border, on the stem")
            mid = (min(xs) + max(xs)) / 2
            self.assertLess(min(abs(mid - low) for low in lows), 3, "where the vine hangs lowest")
        margin = [name for name in perches if name not in above]
        self.assertEqual(len(margin), 2, "and one on the vine climbing the right margin")
        for name in margin:
            self.assertTrue(all(x >= 396 for x, _ in p.layers[name]), "clear of the hare and its notes")
        for draw in (SET.h2, SET.h3):
            q = draw(HEADER, False, True)
            margin = [n for n in q.layers if n.startswith("bd") and all(x >= 396 for x, _ in q.layers[n])]
            self.assertGreaterEqual(len(margin), 2, (draw.__name__, "a bird on the vine in the margin"))

    def test_the_vine_across_the_top_is_tacked_under_the_months_mark(self):
        """The vine is tacked at the top centre and every span out from it, so the month's mark covers a tack
        and the leaves beside it whole and cuts none, on a wide sheet and on a phone; its two ends are the same
        shorter span."""
        for width, span in ((WIDE, VINE_SPAN), (NARROW, 34)):
            xs = A.tacks(5, width - 5, span)
            self.assertIn(width // 2, xs, width)
            gaps = [b - a for a, b in zip(xs, xs[1:])]
            self.assertEqual(gaps[0], gaps[-1], (width, "the ends alike"))
            self.assertTrue(all(g == span for g in gaps[1:-1]), (width, gaps))


class Phones(unittest.TestCase):
    def test_the_monk_writes_on_a_phone_where_the_words_leave_him_room(self):
        """On a phone H1 the monk at his desk and the wyvern stand on the rule when the notes leave the rows
        for them, the candle and the inkhorn otherwise; the vine climbs the right margin with a bird on it,
        and by night the candle's light pools on the vellum."""
        habit, birds = frozenset(RAMP["habit"]), frozenset((RAMP["lapis"][4], RAMP["oxblood"][4]))
        for night in (False, True):
            p = SET.h1_narrow(HEADER, night)
            base = p.layers["base"]
            self.assertTrue(any(c in habit for c in base.values()), (night, "the monk"))
            self.assertIn(RAMP["verdigris"][0], base.values(), (night, "the wyvern"))
            stem = [c for (x, y), c in base.items() if x >= 162 and c in RAMP["verdigris"]]
            self.assertGreater(len(stem), 14, (night, "the vine climbing the right margin"))
            if not night:
                self.assertTrue(any(c in birds and x >= 162 for (x, y), c in base.items()), "a bird on it")
            self.assertEqual(bool(p.lamps), night)
            if night:
                self.assertTrue(any("ellipse" in s for s in p.shapes.get("fb0", [])), "its light pooled")
        most, _ = contents(KEY)["most"]
        p = SET.h1_narrow(most, False)
        self.assertFalse(any(c in habit for c in p.layers["base"].values()), "no room for the monk under all that")
        self.assertIn(RAMP["lapis"][5], p.layers["base"].values(), "the inkhorn stands in his place")

    def test_h2_and_h3_phones_stand_their_heroes(self):
        """A phone's H2 stands the great book open on its lectern under its words, the initial gilt on its page,
        and its H3 the great quill in its inkhorn under its words, with a snail beside its title; each with the
        vine climbing the right margin beside it."""
        p = SET.h2_narrow(HEADER, False)
        rule = next(iter(p.standing))
        last = max(b[3] for b in p.words if b[3] <= rule)
        under = {c for (x, y), c in p.layers["base"].items() if last + 2 <= y < rule}
        self.assertTrue(under & set(RAMP["wood"]), "the lectern")
        self.assertIn(RAMP["lapis"][3], under, "the initial on the book's page")
        for draw in (SET.h2_narrow, SET.h3_narrow):
            p = draw(HEADER, False)
            stem = [c for (x, y), c in p.layers["base"].items() if x >= 162 and c in RAMP["verdigris"]]
            self.assertGreater(len(stem), 30, (draw.__name__, "the vine climbing the right margin"))
        p = SET.h3_narrow(HEADER, False)
        self.assertIn(RAMP["ash"][3], p.layers["base"].values(), "the quill's spine")
        self.assertTrue(any(c in RAMP["wood"] and x >= 150 for (x, y), c in p.layers["base"].items()), "the snail")

    def test_every_phone_header_stands_a_scene_of_the_sets_own_day_and_night(self):
        """Every phone header of every shared content, H1, H2 and H3, day and night, stands a scene: drawn
        again without the hooks that draw it, it loses at least a creature's worth of the margin's own tones,
        the wood, wool and skin of the scriptorium and the verdigris of its beasts."""
        for name, (h, _) in contents(KEY).items():
            for code, draw in (("H1", SET.h1_narrow), ("H2", SET.h2_narrow), ("H3", SET.h3_narrow)):
                for night in (False, True):
                    p = draw(h, night)
                    with without("scene_narrow", "scene_under", "finish"):
                        bare = draw(h, night)
                    scene = [c for k, c in p.layers["base"].items()
                             if c in SPRITE_TONES and bare.layers["base"].get(k) != c]
                    self.assertGreaterEqual(len(scene), 30, (name, code, night))

    def test_a_phone_always_asks_for_rows_under_its_words_for_its_hero(self):
        """A phone's H2 and H3 ask for the same rows under their words whatever their titles and their words, and
        their heroes stand there: drawn without the scene under the words, the drawing loses its hero, and nothing
        of the section's scene stands beside its title."""
        for name, (h, _) in contents(KEY).items():
            for code, draw in (("H2", SET.h2_narrow), ("H3", SET.h3_narrow)):
                rows = []
                real = type(SET).phone_rows
                with mock.patch.object(type(SET), "phone_rows",
                                       lambda self, *a: rows.append(real(self, *a)) or rows[-1]):
                    p = draw(h, False)
                self.assertEqual(set(rows), {UNDER[code]}, (name, code))
                with without("scene_under"):
                    beside = draw(h, False)
                self.assertNotEqual(p.layers["base"], beside.layers["base"], (name, code, "a hero under"))
                if code == "H2":
                    with without("scene_under", "scene_narrow"):
                        bare = draw(h, False)
                    self.assertEqual(beside.layers["base"], bare.layers["base"], (name, code, "nothing beside"))

    def test_a_scene_under_the_words_stands_clear_of_them_lit_by_its_candle_by_night(self):
        """The scene a phone stands under its words keeps two units clear of every word, its candle's light
        pooled clear of them too; by night the candle burns and lights what stands near it, by day it is
        unlit."""
        for name, (h, _) in contents(KEY).items():
            for code, draw in (("H2", SET.h2_narrow), ("H3", SET.h3_narrow)):
                for night in (False, True):
                    p = draw(h, night)
                    with without("scene_under"):
                        bare = draw(h, night)
                    drawn = [k for k, c in p.layers["base"].items() if bare.layers["base"].get(k) != c]
                    if not drawn:
                        continue
                    for (x, y) in drawn:
                        self.assertTrue(p.clear_of_words(x - 2, y - 2, x + 3, y + 3), (name, code, night, x, y))
                    self.assertEqual(bool(p.lamps), night, (name, code))
                    self.assertEqual(any(p.layers["base"][k] in FLAME for k in drawn), night, (name, code, "a flame"))
                    for s in (s for n in p.shapes if n.startswith("fb") for s in p.shapes[n]):
                        cx, cy, rx, ry = (float(re.search(f' {a}="([-.0-9]+)"', s).group(1))
                                          for a in ("cx", "cy", "rx", "ry"))
                        self.assertTrue(p.clear_of_words(cx - rx, cy - ry, cx + rx, cy + ry), (name, code, "its pool"))


class Footers(unittest.TestCase):
    def test_a_footer_stands_on_its_vine_and_ends_in_the_scribes_corner(self):
        """Every footer has its floor, a vine along its foot inside the border wherever the words leave it
        room; and a title block whose cells leave the room, as one without notes does, ends after its way
        back up in the scribe's corner, the inkhorn and its quill on two books by a candle, the candle burning
        by night."""
        bare = contents(KEY)["least"][1].with_(top="Back to Top", license="MIT", updated="2026-09-25")
        foot = next(f for _, (_, f) in contents(KEY).items() if f.get("closing"))
        for night in (False, True):
            for draw in (SET.f1, SET.f2, SET.f1_narrow, SET.f2_narrow):
                p = draw(foot, night)
                y = p.h - A.FRAME - 2
                vine = [x for x in range(p.w) if p.get(x, y) in RAMP["verdigris"]]
                self.assertGreaterEqual(len(vine), 30, (draw.__name__, night, "the vine along the foot"))
            p = SET.f1(bare, night)
            end = max(b[2] for b in p.words)
            corner = {c for (x, y), c in p.layers["base"].items() if x > end + 2}
            self.assertIn(RAMP["lapis"][5], corner, (night, "the ink shining in the inkhorn"))
            self.assertIn(RAMP["oxblood"][3], corner, (night, "the books"))
            self.assertEqual(bool(corner & FLAME), night, (night, "the candle burning by night"))

    def test_a_footer_is_the_books_colophon(self):
        """The twisted cord along the top inside the border, the rubricator's mark before the notes, the
        inkhorn with its quill and a candle at the end of a cell; a header hangs its vine instead."""
        foot = next(f for _, (_, f) in contents(KEY).items() if f.get("closing"))
        for draw in (SET.f1, SET.f2, SET.f1_narrow, SET.f2_narrow):
            for night in (False, True):
                p = draw(foot, night)
                self.assertIn(("pattern", "cr"), p.syms, (draw.__name__, night, "the cord"))
                self.assertTrue(any('href="#CR"' in s for s in p.shapes["near"]), draw.__name__)
                self.assertIn(RAMP["lapis"][5], p.layers["base"].values(), (draw.__name__, "the ink shining"))
                self.assertIn(RAMP["ink"][0], p.layers["base"].values(), (draw.__name__, "the candle's wick"))
        for draw in (SET.f1, SET.f1_narrow):
            p = draw(foot, False)
            self.assertEqual(p.get(5, 15), RAMP["oxblood"][2], (draw.__name__, "the rubricator's mark"))
        p = SET.h1(HEADER, False, True)
        self.assertNotIn(("pattern", "cr"), p.syms)


class Elements(unittest.TestCase):
    def test_every_element_is_the_sets_linted_deterministic_and_the_kits_sizes(self):
        files = elements()
        self.assertEqual(set(files), set(ED.render(ELEMENTS, "standard")))
        again = elements()
        for eid, d in ELEMENTS.items():
            kind = d["kind"]
            for variant in E.variants(kind, d):
                for theme in ("day", "dark"):
                    name = ED.file_name(eid, variant, theme)
                    svg = files[name]
                    minidom.parseString(svg)
                    self.assertEqual(svg, again[name], name)
                    self.assertIn(f"<!--{KIT} v{KIT_VERSION} {KEY} elements {kind} ", svg, name)
                    self.assertEqual(lint(svg, budget=BUDGET[E.KINDS[kind][2]], tokens=SET.tokens), [], name)
                    w = int(re.search(r'width="(\d+)"', svg).group(1))
                    wanted = (404 if kind == "placard" or variant == "half" or
                              (variant == "narrow" and kind in ("roster", "certificate"))
                              else 360 if variant == "narrow" else 830)
                    self.assertEqual(w, wanted, name)

    def test_the_half_page_pair_is_drawn_level(self):
        files = elements()
        heights = {re.search(r'height="(\d+)"', files[f"{eid}-day.svg"]).group(1)
                   for eid in ("contributors", "conformance")}
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

    def test_a_counters_digits_are_rubric_red_on_vellum(self):
        for night in (False, True):
            self.assertGreaterEqual(contrast(SET.counter_ink(night, False), RAMP["vellum"][6]), 4.5, night)
            self.assertEqual(SET.counter_ink(night, False), RAMP["oxblood"][3])

    def test_a_counters_cell_is_a_vellum_tablet_framed_in_gold(self):
        G = RAMP["gold"]
        q = Pix(11, 15)
        A.vellum_tablet(q, 0, 0, False)
        self.assertEqual((q.get(5, 0), q.get(0, 7)), (G[5], G[5]), "lit along the top and the left")
        self.assertEqual((q.get(10, 7), q.get(5, 14)), (G[2], G[2]), "shaded along the right and the foot")
        self.assertEqual((q.get(0, 0), q.get(10, 14)), (G[6], G[3]), "a bead at each corner")
        self.assertIn(q.get(5, 7), RAMP["vellum"])

    def test_portraits_are_painted_busts_in_gold_frames_and_the_bot_an_automaton(self):
        skin, G = frozenset(RAMP["skin0"] + RAMP["skin1"] + RAMP["skin2"]), RAMP["gold"]
        looks = set()
        for i, person in enumerate(ELEMENTS["contributors"]["people"]):
            p = Pix(40, 40)
            SET.avatar(p, 20, 20, i, person, False)
            base = p.layers["base"]
            field = {(x, y): c for (x, y), c in base.items() if 14 <= x <= 26 and 14 <= y <= 26}
            if person.get("initials"):
                self.assertTrue(any(c in skin for c in field.values()), (person["name"], "a face"))
                looks.add(frozenset(field.items()))
            else:
                self.assertFalse(any(c in skin for c in field.values()), "the bot has no skin")
                self.assertIn(RAMP["ash"][3], field.values(), "but shoulders of iron")
            self.assertEqual((p.get(12, 20), p.get(13, 20)), (G[4], G[5]), "the frame, two deep")
            self.assertEqual((p.get(12, 12), p.get(28, 28)), (G[6], G[6]), "a bead at each corner")
        self.assertEqual(len(looks), 3, "each sitter has their own look")
        self.assertEqual(A.seed_of("IMOGEN VALE"), A.seed_of("IMOGEN VALE"))
        self.assertNotEqual(A.seed_of("IMOGEN VALE"), A.seed_of("VALE IMOGEN"))

    def test_a_schematic_card_is_a_painted_panel_and_its_wires_rubric_with_gold_at_the_joins(self):
        G, L, O = RAMP["gold"], RAMP["lapis"], RAMP["oxblood"]
        for night in (False, True):
            p = Pix(140, 60)
            spec = {"title": "The survey", "path": "driftmark.toml", "icon": "file"}
            SET.node(p, night, 10, 10, 106, 28, spec, 0, True)
            self.assertEqual(p.get(10, 10), G[6], "a bead at the corner")
            self.assertEqual((p.get(60, 10), p.get(60, 37)), (G[5], G[3]), "the frame lit along the top, shaded below")
            self.assertEqual(p.get(60, 11), O[3 if not night else 2], "a hairline of oxblood inside it")
            cell = [p.get(x, y) for x in range(12, 20) for y in range(12, 36)]
            self.assertIn(G[6], cell, "the icon in gold leaf")
            self.assertTrue(any(c in (L if not night else O) for c in cell), "on a square of pigment")
            self.assertEqual(SET.wire_ink(night), O[3 if not night else 4])
            q = Pix(60, 60)
            SET.wire(q, night, [(5, 10), (40, 10), (40, 50)])
            self.assertEqual(q.get(40, 10), G[6], "a boss of gold at the join")
            self.assertEqual(q.get(5, 10), G[6], "and where the wire leaves its card")
            self.assertEqual(q.get(20, 10), SET.wire_ink(night))

    def test_the_seals_ribbon_is_silk_of_two_colours_with_gold_ends(self):
        G, L, O = RAMP["gold"], RAMP["lapis"], RAMP["oxblood"]
        for night in (False, True):
            k = -1 if night else 0
            p = Pix(100, 120)
            SET.rosette(p, 50, 40, 23, 31, 16, night)
            SET.tag(p, 30, 90, 40, 9, night)
            self.assertEqual((p.get(50, 91), p.get(50, 96)), (L[3 + k], O[3 + k]), "lapis above, oxblood below")
            self.assertEqual(p.get(50, 94), G[4], "a thread of gold between")
            self.assertEqual((p.get(29, 90), p.get(70, 98)), (G[5], G[3]), "gold ends")
            SET.tag(p, 9, 8, 20, 9, night)
            self.assertEqual(p.get(15, 10), O[3], "any other tag is the rubric block")
        p = SET.placard(E.describe("placard", ELEMENTS["action"]), False)
        perched = [c for (x, y), c in p.layers["base"].items() if 158 <= x <= 167 and 7 <= y <= 13]
        self.assertTrue(any(c in O for c in perched), "a bird perched at the top of the placard")


class Badges(unittest.TestCase):
    def badge(self, style, **kw):
        args = dict(style=style, label="Build", message="Passing", icon="pulse", label_hex=PALETTE["black"],
                    message_hex=PALETTE["blue"], live=False, state=None, reserve=(), rels=["static/b.svg"], stamp=STAMP)
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

    def test_the_swatches_cover_every_hue_a_written_colour_comes_in(self):
        swatches = SET.badge_swatches()
        self.assertIn(nearest(PALETTE["red"], swatches), ("oxblood", "madder"))
        self.assertEqual(nearest(PALETTE["orange"], swatches), "redlead")
        self.assertIn(nearest(PALETTE["yellow"], swatches), ("gold",))
        self.assertEqual(nearest(PALETTE["green"], swatches), "verdigris")
        self.assertIn(nearest(PALETTE["blue"], swatches), ("lapis", "azure"))
        self.assertEqual(nearest(PALETTE["purple"], swatches), "tyrian")
        self.assertEqual(nearest(PALETTE["white"], swatches), "vellum")
        self.assertEqual(nearest(PALETTE["black"], swatches), "ink")
        self.assertEqual(nearest(PALETTE["slate"], swatches), "slate")
        self.assertEqual(nearest(PALETTE["brown"], swatches), "sepia")
        for name, (block, _, _) in swatches.items():
            svg = self.badge("flat", message_hex=block)["static/b.svg"]
            self.assertIn(block, svg, name)

    def test_a_badge_is_a_painted_panel_framed_in_gold_with_its_letters_untouched(self):
        """The set's touch frames the badge in gold inside its shape, rules gold between the blocks and
        diapers the label's block, and leaves every row and column the letters take as the layout painted
        them: a badge drawn without the touch is the same there."""
        for style, s in BADGE_STYLES.items():
            h, corner = s["h"], s["corner"]
            ty = SET._text_y(s)
            cap = 7 if s["font"] == "57" else 5
            for label, message in (("Build", "Passing"), ("Tone", "x"), ("", "Just a message"), ("Only a label", "")):
                with mock.patch.object(type(SET), "badge_top", lambda *a, **k: None):
                    plain = SET.classic_badge(style, label, message, "pulse" if label else None, SET.badge_label(),
                                              SET.badge_states()["green"])
                touched = SET.classic_badge(style, label, message, "pulse" if label else None, SET.badge_label(),
                                            SET.badge_states()["green"])
                w = touched.w
                self.assertEqual((w, touched.h), (plain.w, plain.h))
                # The blocks' boundary, and the room each block's letters have inside its own padding.
                _, _, _, left, right, _ = SET._layout(style, label, message, "pulse" if label else None)
                split = left if left and right else None
                rooms = ([(s["pad"], split - s["pad"]), (split + s["pad"] - 1, w - s["pad"])] if split
                         else [(s["pad"], w - s["pad"])])
                for (x, y), c in touched.layers["base"].items():
                    self.assertTrue(inside(x, y, w, h, corner), (style, label, x, y))
                    if ty <= y < ty + cap and any(a <= x < b for a, b in rooms):
                        self.assertEqual(c, plain.layers["base"].get((x, y)), (style, label, x, y, "the letters' room"))
                self.assertEqual(touched.uses, plain.uses, (style, label, "the letters themselves"))
                # The frame line runs round the edge, in gold.
                for x in range(w):
                    for y in (0, h - 1):
                        if inside(x, y, w, h, corner):
                            self.assertIn(touched.get(x, y), RAMP["gold"], (style, label, x, y))
                for y in range(h):
                    for x in (0, w - 1):
                        if inside(x, y, w, h, corner):
                            self.assertIn(touched.get(x, y), RAMP["gold"], (style, label, x, y))
        self.assertLess(TOP, 3)

    def test_what_the_sets_letters_cannot_draw_is_left_to_the_kit(self):
        self.assertIsNone(self.badge("flat", message="中文"))

    def test_the_live_yellow_is_an_ink_of_its_own_and_its_plate_has_an_edge(self):
        self.assertEqual(SET.badge_states()["yellow"][0], X["yellow"])
        self.assertNotEqual(SET.badge_states()["yellow"][0], SET.badge_gold()[0])
        self.assertEqual(SET.plate_edge(X["yellow"]), RAMP["gold"][2])
        self.assertEqual(SET.plate_edge(RAMP["verdigris"][3]), RAMP["verdigris"][2])


class Links(unittest.TestCase):
    def test_a_link_is_a_ribbon_bookmark_cut_in_a_swallowtail(self):
        G = RAMP["gold"]
        for night in (False, True):
            p = SET.link_button("Issues", 0, night)
            fill = SET.link_colours(night)[0]
            w = p.w
            self.assertIsNone(p.get(w - 1, 7), "the notch is cut out of the ribbon's end")
            self.assertIsNone(p.get(w - 3, 7))
            self.assertIsNone(p.get(w - 1, 3), "the cut takes the ribbon's whole height")
            self.assertEqual(p.get(w - 1, 2), G[5], "the cut is edged in bright gold")
            self.assertEqual(p.get(w - 3, 10), G[5])
            self.assertEqual(p.get(w - 6, 7), G[6], "to the apex")
            self.assertEqual(p.get(w - 7, 7), fill, "the silk stays whole before the notch")
            self.assertEqual(p.get(1, 7), G[5], "the left end is capped in gold")
            self.assertIn(p.get(4, 7), G, "the roundel the icon sits on")
            self.assertIn(p.get(12, 7), G)
            svg = p.svg("Issues", "Link: Issues", still=True)
            self.assertEqual(lint(svg, budget=BUDGET["link"], tokens=SET.tokens), [])
            for i in range(4):
                art, pal = SET.link_icon(i, night, "#000000")
                self.assertTrue(all(len(row) == 7 for row in art) and len(art) == 7, i)
                self.assertTrue(all(contrast(pal[ch], G[4]) >= 2.5 for ch in "gGd"), (i, "dark on the gold"))


class Hand(unittest.TestCase):
    """The collection's hand, which the design keeps to drawn as March's design and kept all year."""

    def test_check_finds_nothing_as_the_months_design_or_kept_all_year(self):
        self.assertEqual(check(HELD), [])
        self.assertEqual(check(SET), [])

    def test_its_words_are_in_the_hands_inks(self):
        for night in (False, True):
            k = SET.ink(night)
            self.assertEqual((k["body"], k["muted"]), (HAND.body[night], HAND.muted[night]), night)

    def test_its_grounds_fall_in_the_hands_bands(self):
        """The cream vellum by day and every band of the dark scriptorium by night."""
        for night, grounds in ((False, [C["paper"]]), (True, NIGHT_SKY)):
            lo, hi, most = HAND.night_ground if night else HAND.day_ground
            for ground in grounds:
                light, chroma, _ = lab(ground)
                self.assertTrue(lo <= light <= hi and chroma <= most, (night, ground, light, chroma))

    def test_every_flame_burns_on_the_hands_flame_ramp(self):
        """The candles' flames, their glows, the light they lay on what stands near them and the pools they
        throw, in every header and footer by night, are tones of the hand's flame; and so is the flame of a
        still candle, which lies on the drawing itself."""
        self.assertEqual(RAMP["flame"], HAND.ramp("flame"))
        burning = 0
        for name, (h, f) in contents(KEY).items():
            for p in (HELD.h1(h, True, True), HELD.h2(h, True, True), HELD.h3(h, True, True), HELD.h1_narrow(h, True),
                      HELD.h2_narrow(h, True), HELD.h3_narrow(h, True), HELD.f1(f, True), HELD.f2(f, True),
                      HELD.f1_narrow(f, True), HELD.f2_narrow(f, True)):
                lit = {c.split(":")[0] for n in p.layers if n.startswith(("fl", "fb")) for c in p.layers[n].values()}
                lit |= {c for n in p.shapes if n.startswith(("fl", "fb"))
                        for c in re.findall(r'fill="(#[0-9A-F]{6})"', "".join(p.shapes[n]))}
                burning += bool(lit)
                self.assertLessEqual(lit, FLAME, name)
        self.assertGreater(burning, 30, "the candles burn in most of them")
        p = Pix(40, 50)
        A.candle(p, 10, 45, h=30, night=True, motion=False)
        A.candle_stub(p, 30, 45, night=True)
        own = set(RAMP["ash"] + RAMP["vellum"] + RAMP["ink"] + RAMP["gold"])
        flame = {c.split(":")[0] for c in p.layers["base"].values()} - own
        self.assertTrue(flame)
        self.assertLessEqual(flame, FLAME)

    def test_its_people_are_painted_in_the_hands_skins(self):
        """The monk's face and hands are on the hand's light skin; each sitter's on one of its three (see the
        portraits' test)."""
        pal = A._pal(A.MONK_PAL, False)
        self.assertLessEqual({pal[ch] for ch in "stur"}, set(HAND.ramp("skin0")))
        sitters = {A.SKIN[(A.seed_of(n) // 7) % len(A.SKIN)] for n in ("IMOGEN VALE", "TOMAS OKAFOR", "WREN CASTELLAN")}
        self.assertLessEqual(sitters, {"skin0", "skin1", "skin2"})

    def test_it_moves_on_the_hands_times(self):
        """In a moving header the title's glint crosses it every twelve seconds, the hand's period; flames
        flicker and gold beads twinkle on the engine's cadences; and the monk's quill, the wyvern's wing, the
        hare's notes and the birds' wings come round in four to eight seconds."""
        h, _ = contents(KEY)["repository"]
        blinks = {num(v[2]) for v in BLINKS.values()}
        for code in ("H1", "H2", "H3"):
            for theme in (DAY, DARK):
                svg = HELD.header(code, h, theme, True, True)
                glints = re.findall(r'<animateTransform attributeName="transform" type="translate" values="0;[^"]+" '
                                    r'keyTimes="0;.4;1" dur="([.\d]+)s"', svg)
                self.assertTrue(glints, (code, theme["name"]))
                self.assertEqual(set(glints), {num(HAND.glint)}, (code, theme["name"]))
                for dur in re.findall(r'<animate [^>]*?dur="([.\d]+)s"', svg):
                    self.assertTrue(dur in blinks or 4 <= float(dur) <= 8, (code, theme["name"], dur))

    def test_every_scene_keeps_clear_of_the_months_mark(self):
        """No scene comes within two units of the box the month's mark takes at the top centre, in any header,
        wide or on a phone, with the mark or without it."""
        T = type(SET)
        for name, (h, _) in contents(KEY).items():
            for held in (HELD, SET):
                for draw, hooks in ((lambda d: d.h1(h, False, False), ("scene",)),
                                    (lambda d: d.h2(h, False, False), ("scene",)),
                                    (lambda d: d.h3(h, False, False), ("scene",)),
                                    (lambda d: d.h1_narrow(h, False), ("scene_narrow",)),
                                    (lambda d: d.h2_narrow(h, False), ("scene_narrow", "scene_under")),
                                    (lambda d: d.h3_narrow(h, False), ("scene_narrow", "scene_under"))):
                    p = draw(held)
                    with contextlib.ExitStack() as stack:
                        for hook in hooks:
                            stack.enter_context(mock.patch.object(T, hook, lambda *a, **k: []))
                        bare = draw(held)
                    n = HAND.mark_size
                    x0, y0 = p.w // 2 - n // 2 - 2, MARK_Y - n // 2 - 2
                    for layer, cells in p.layers.items():
                        for (x, y), c in cells.items():
                            if x0 <= x < x0 + n + 4 and y0 <= y < y0 + n + 4 and not layer.startswith("mark"):
                                self.assertEqual(bare.layers.get(layer, {}).get((x, y)), c, (name, layer, x, y))


class Composition(unittest.TestCase):
    """The composition the collection's hand asks of every design: a section's hero rising four fifths of its
    band, a strip's rising its full height, a phone's standing forty-four rows under its words, and a footer
    ending in the design's mark; measured where the set stands its great book and its great quill."""

    @staticmethod
    def heroes(draw):
        """The drawing `draw()` makes, and the great books and great quills it stands as (what, x0, y0, x1, y1)."""
        boxes, book, quill = [], A.book_on_lectern, A.great_quill

        def booked(p, x, base, w, h, stand, *a, **k):
            boxes.append(("book", x - 2, base - stand - h + 2, x + w + 2, base + 1))
            return book(p, x, base, w, h, stand, *a, **k)

        def quilled(p, x, base, top, *a, **k):
            boxes.append(("quill", x, top, x + 22, base + 1))
            return quill(p, x, base, top, *a, **k)
        with mock.patch.object(A, "book_on_lectern", booked), mock.patch.object(A, "great_quill", quilled):
            p = draw()
        return p, boxes

    ORDINARY = ("kit", "repository", "profile")

    def test_a_sections_hero_rises_four_fifths_of_its_band(self):
        """The great book open on its lectern, at the right of a wide section, rises from its rule at least four
        fifths of the way to the vine across the top, and is 70 units across."""
        for name in self.ORDINARY:
            h, _ = contents(KEY)[name]
            for night in (False, True):
                p, boxes = self.heroes(lambda: HELD.h2(h, night, True))
                (what, x0, y0, x1, y1), = boxes
                self.assertGreaterEqual(y1 - y0, 0.8 * (y1 - 16), (name, night))
                self.assertGreaterEqual(x1 - x0, BOOK["H2"][0] + 4, (name, night))
                self.assertGreaterEqual(x0, 300, (name, night, "on the right"))

    def test_a_strips_hero_rises_its_full_height(self):
        for name in self.ORDINARY:
            h, _ = contents(KEY)[name]
            p, boxes = self.heroes(lambda: HELD.h3(h, False, True))
            (what, x0, y0, x1, y1), = boxes
            self.assertEqual(what, "quill")
            self.assertEqual(y0, QUILL_TOP, (name, "up to the vine across the top"))
            self.assertGreaterEqual(y1 - y0, min(60, y1 - QUILL_TOP), name)

    def test_the_monks_side_of_a_title_page_rises_as_high_as_its_other(self):
        """On a wide H1 the monk's side, his shelf of books over him, rises at least seven tenths of the way
        from the rule to the vine across the top, as the wyvern's side does."""
        for name in self.ORDINARY:
            h, _ = contents(KEY)[name]
            p = HELD.h1(h, False, False)
            with mock.patch.object(type(SET), "scene", lambda *a, **k: []):
                bare = HELD.h1(h, False, False)
            rule = max(y for (x, y), c in p.layers["base"].items() if x < 58 and c in RAMP["wood"]) + 1
            left = [y for (x, y), c in p.layers["base"].items() if x < 58 and bare.layers["base"].get((x, y)) != c]
            self.assertGreaterEqual(rule - min(left), 0.7 * (rule - 16), name)

    def test_a_phones_hero_stands_forty_four_rows_under_its_words(self):
        """For every shared content, by day and by night, a phone's great book on its lectern and its great quill
        in its inkhorn each stand under its words, two units and more below the last of them, and forty-four rows
        tall or more; and a phone's H1 gives its monk the rows a full scene under its words needs."""
        for name, (h, _) in contents(KEY).items():
            for code, want in (("H2", "book"), ("H3", "quill")):
                for night in (False, True):
                    draw = HELD.h2_narrow if code == "H2" else HELD.h3_narrow
                    p, boxes = self.heroes(lambda: draw(h, night))
                    self.assertEqual(len(boxes), 1, (name, code, night))
                    (what, x0, y0, x1, y1), = boxes
                    last = max(b[3] for b in p.words if b[1] < y0)
                    case = (name, code, night)
                    self.assertEqual(what, want, case)
                    self.assertGreaterEqual(y1 - y0, 44, case)
                    self.assertGreaterEqual(y0, last + 2, (case, "under the words"))
        self.assertGreaterEqual(SET.phone_scene_rows, 48)
        self.assertGreaterEqual(QUILL_TALL["phone"] + 1, 44)
        self.assertGreaterEqual(BOOK["phone"][1] + BOOK["phone"][2] - 1, 44)


if __name__ == "__main__":
    unittest.main()
