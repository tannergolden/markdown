# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The checks every design of a collection shares, written once and run by each design's own tests over itself.

A collection's design is a theme, not a holiday on the calendar, so the checks every registered set shares
(`test_holiday_sets`) never reach it. A design's module runs these over its own design by mixing `Shared` into a
test case and naming the design and the parts of it the checks watch:

    class Shared(design_checks.Shared, unittest.TestCase):
        SET = SET                       # the design, kept all year
        ART = A                         # its art module
        PIECES = ("terminal", "city")   # the art that draws a scene's pieces, each kept by a drawing made lighter
        FOOTINGS = ("_footed",)         # the hooks that draw its footers' ground and emblem

They hold the design to its hand: `check` over the samples and the most and the least a page can say, as its
month's design (`test_collection_hand` holds every design to it with the kit's own lines, kept all year and with a
sign); its words in the hand's two inks; every light that flickers burning on the hand's flame; its titles' glint passing on the hand's period in a wide moving header and in no other file; and the month's
mark at the top centre of every header only as its month's design, its box kept clear of every scene whether the
mark is drawn or not. They keep every sprite of a scene two units clear of every word, wide and on a phone (an
atmosphere a design names in `ATMOSPHERE` may pass behind its title, but keeps as clear of every other word), and
every footing one unit; stand a scene of the design's under every phone header's words, the H1's in the rows it
keeps under them and the H2's and H3's in the rows they ask for whatever their words say; hold every header to the
budget for every content, at its full weight with room to spare for an ordinary page and with every piece and all
its motion for the most a page can say, as its month's design too; and check the files every set is held to: its
banners and link buttons, its elements and its badges. Every header and footer the checks read is drawn once for
them all. A design's own rules stay in its own module.
"""
from __future__ import annotations

import datetime as dt
import re
import xml.dom.minidom as minidom
from collections import Counter
from unittest import mock

from tests import support
from tests.unit.test_holiday_sets import DASHES, ELEMENTS, HEIGHTS, STAMP, contents

from domain import KIT, KIT_VERSION
from domain import collections
from domain.badges import data as BD
from domain.banners.content import Header
from domain.banners.designs import DESIGNS, variants
from domain.canvas import BUDGET, DARK, DAY, colours, lint
from domain.collections.hand import HANDS, CollectionSet, check
from domain.elements import draw as E
from domain.holidays.designs.badges import PLATE, STATES, STYLES as BADGE_STYLES
from domain.holidays.pixel import Pix, contrast
from domain.palette import PALETTE

support.install()
CODES = ("H1", "H2", "H3")
# The glint a Matrix design's titles take: the terminal's beam passing down them (`collections.rain.scan`).
SCAN = re.compile(r'<g mask="url\(#sc\d+\)"><rect[^>]*><animateTransform[^>]*dur="([\d.]+)s"')


def wide(held, code: str):
    return {"H1": held.h1, "H2": held.h2, "H3": held.h3}[code]


def phone(held, code: str):
    return {"H1": held.h1_narrow, "H2": held.h2_narrow, "H3": held.h3_narrow}[code]


def months_day(held) -> dt.date:
    """A day that makes `held` its collection's design for the month: the first of its month."""
    return dt.date(2026, collections.owner(held.key).month_of(held.key), 1)


def hooked(held, draw, hooks) -> tuple:
    """`draw()`'s drawing, the pixels each of the design's `hooks` (names of its drawing hooks) puts on it, and the
    boxes of its titles' words: (drawing, {hook: pixels}, boxes). The pixels are gathered as each hook draws, its
    pixels on every layer and the cells of the symbols it places, as {(x, y): the layers they lie on}; a title's
    boxes are the words `title_text` sets."""
    by, cells, titles = {name: {} for name in hooks}, {}, []
    symbol = Pix.symbol

    def kept(self, key, cells_=None, shapes="", mono=False):
        sid = symbol(self, key, cells_, shapes, mono)
        cells.setdefault(sid, set(cells_ or ()))
        return sid

    def watched(name, hook):
        def drawn(*args, **kw):
            p, pixels = next(a for a in args if isinstance(a, Pix)), by[name]
            before = {L: set(c) for L, c in p.layers.items()}
            placed = {L: len(u) for L, u in p.uses.items()}
            out = hook(*args, **kw)
            for L, c in p.layers.items():
                for xy in set(c) - before.get(L, set()):
                    pixels.setdefault(xy, set()).add(L)
            for L, uses in p.uses.items():
                for (_, sid, x, y, s) in uses[placed.get(L, 0):]:
                    for dx, dy in cells.get(sid, ()):
                        pixels.setdefault((x + dx * s, y + dy * s), set()).add(L)
            return out
        return drawn

    def lettered(hook):
        def drawn(p, *args, **kw):
            n = len(p.words)
            out = hook(p, *args, **kw)
            titles.extend(p.words[n:])
            return out
        return drawn

    patched = {name: watched(name, getattr(held, name)) for name in hooks}
    patched["title_text"] = lettered(patched.get("title_text", held.title_text))
    with mock.patch.object(Pix, "symbol", kept), mock.patch.multiple(held, **patched):
        p = draw()
    return p, by, titles


def merged(by: dict, hooks) -> dict:
    """The pixels of `hooks` among those `hooked` gathered by hook, as one {(x, y): layers}."""
    pixels = {}
    for name in hooks:
        for xy, layers in by.get(name, {}).items():
            pixels.setdefault(xy, set()).update(layers)
    return pixels


def sprites(held, draw, *hooks) -> tuple:
    """`draw()`'s drawing, every pixel the design's `hooks` put on it, as {(x, y): the layers they lie on}, and the
    boxes of its titles' words (see `hooked`)."""
    p, by, titles = hooked(held, draw, hooks)
    return p, merged(by, hooks), titles


def near(p: Pix, xy, margin: int, boxes=None) -> bool:
    """Whether the unit at `xy` lies within `margin` units of a word's box: of every word's, or of `boxes`'."""
    x, y = xy
    x0, y0, x1, y1 = x - margin, y - margin, x + margin + 1, y + margin + 1
    if boxes is None:
        return not p.clear_of_words(x0, y0, x1, y1)
    return any(x0 < bx1 and bx0 < x1 and y0 < by1 and by0 < y1 for bx0, by0, bx1, by1 in boxes)


def painted(held, draw, *hooks) -> Counter:
    """How many pixels of each colour the design's `hooks` paint while `draw()` draws, on every layer."""
    cells = {}

    def watched(hook):
        def drawn(*args, **kw):
            p = next(a for a in args if isinstance(a, Pix))
            before = {L: dict(c) for L, c in p.layers.items()}
            out = hook(*args, **kw)
            for L, c in p.layers.items():
                cells.update({(L, xy): col for xy, col in c.items() if before.get(L, {}).get(xy) != col})
            return out
        return drawn
    with mock.patch.multiple(held, **{name: watched(getattr(held, name)) for name in hooks}):
        draw()
    return Counter(cells.values())


def pieces(art, names, draw) -> tuple:
    """`draw()`'s file, and the pieces of the scene in the drawing it was made from (the last drawn, when the kit
    draws a file again lighter): each call of the art functions `names` in module `art`, with its arguments but
    the canvas, in the order drawn."""
    calls = []
    if not names:
        return draw(), []

    def watched(name, fn):
        def drawn(p, *args, **kw):
            calls.append((p, name, args, sorted(kw.items())))
            return fn(p, *args, **kw)
        return drawn
    with mock.patch.multiple(art, **{name: watched(name, getattr(art, name)) for name in names}):
        svg = draw()
    last = calls[-1][0] if calls else None
    return svg, [call[1:] for call in calls if call[0] is last]


def flickering(p: Pix) -> set:
    """Every colour on a drawing's flickering layers: its lights, their glows and the light they lay."""
    layers = [L for L in p.layers if p.meta[L][2] and p.meta[L][2][0] == "flicker"]
    found = {c.split(":")[0] for L in layers for c in p.layers[L].values()}
    return found | {c for L in layers for c in re.findall(r'fill="(#[0-9A-F]{6})"', "".join(p.shapes[L]))}


class Shared:
    """The checks every design of a collection shares; mix into a `unittest.TestCase` and set `SET`."""

    SET = None            # the design, kept all year: `collections.drawn_by(key)`
    ART = None            # its art module, whose `PIECES` a drawing made lighter keeps
    PIECES: tuple = ()    # the names of the art functions that draw a scene's pieces
    FOOTINGS: tuple = ()  # the names of the hooks that draw its footers' footing and emblem, wide and on a phone
    ATMOSPHERE: tuple = ()  # layers of an atmosphere that may pass behind a title, as `("aurora",)`
    GLINT = SCAN          # how its titles' glint is written, its period the first group
    SCENES = ("scene", "scene_narrow", "scene_under", "garland", "section_mark", "strip_mark", "rule_decor")
    _drawn: dict = {}     # what each design draws, drawn once for every check that reads it

    # ------------------------------------------------------------------------------------------ helpers
    @property
    def key(self) -> str:
        return self.SET.key

    def contents(self) -> dict:
        return contents(self.key)

    def off_words(self, p: Pix, pixels: dict, titles: list, margin: int = 2) -> list:
        """The pixels among `pixels` within `margin` units of a word: an atmosphere's (on `ATMOSPHERE` layers
        alone) may lie behind a title, but keeps as clear of every other word."""
        others = [b for b in p.words if b not in titles]
        out = []
        for xy, layers in pixels.items():
            airy = bool(self.ATMOSPHERE) and all(L.rstrip("0123456789+~") in self.ATMOSPHERE for L in layers)
            if near(p, xy, margin, others if airy else None):
                out.append(xy)
        return sorted(out)

    def drawn(self, what, draw):
        """`draw()`, drawn once for the design and kept for every check that reads it."""
        if (self.key, what) not in Shared._drawn:
            Shared._drawn[(self.key, what)] = draw()
        return Shared._drawn[(self.key, what)]

    def banners(self) -> list:
        """Every banner and link file the design draws for the shared contents, as the kit asks for them, drawn
        once: (content, code, file name, svg)."""
        return self.drawn("banners", self.draw_banners)

    def headers(self, marked: bool) -> dict:
        """Every header the design draws for the shared contents, wide and moving and on a phone, by day and by
        night, kept all year or, `marked`, as its month's design, drawn once with the pixels each of its scenes'
        hooks and its stars lay (see `hooked`): {(content, code, wide, night): (drawing, {hook: pixels}, boxes)}."""
        def draw():
            S, hooks, out = self.SET.on(months_day(self.SET)) if marked else self.SET, (*self.SCENES, "stars"), {}
            for name, (h, _) in self.contents().items():
                for code in CODES:
                    for night in (False, True):
                        out[(name, code, True, night)] = hooked(S, lambda: wide(S, code)(h, night, True), hooks)
                        out[(name, code, False, night)] = hooked(S, lambda: phone(S, code)(h, night), hooks)
            return out
        return self.drawn(("headers", marked), draw)

    def footers(self) -> dict:
        """Every footer the design draws for the shared contents, F1 and F2, wide and on a phone, by day and by
        night, drawn once with the pixels its `FOOTINGS` lay: {(content, footer, night): (drawing, {hook: pixels},
        boxes)}."""
        def draw():
            S, out = self.SET, {}
            for name, (_, f) in self.contents().items():
                for footer in (S.f1, S.f2, S.f1_narrow, S.f2_narrow):
                    for night in (False, True):
                        out[(name, footer.__name__, night)] = hooked(S, lambda: footer(f, night), self.FOOTINGS)
            return out
        return self.drawn("footers", draw)

    def draw_banners(self, names=None) -> list:
        S, out = self.SET, []
        for name, (h, f) in self.contents().items():
            if names and name not in names:
                continue
            for code, design in DESIGNS.items():
                content = h if design.kind == "header" else f
                drawer = S.header if design.kind == "header" else S.footer
                for suffix, wide_, motion, theme in variants(design):
                    out.append((name, code, f"{design.kind}-{suffix}.svg", drawer(code, content, theme, wide_, motion)))
                if design.kind == "footer" and design.chip and content.on("links"):
                    for i, (label, _) in enumerate(content.links):
                        for theme in (DAY, DARK):
                            out.append((name, code, f"link-{i}-{theme['name']}.svg", S.link(label, theme, i)))
        return out

    def draw_elements(self, themes=(DAY, DARK)) -> dict:
        out = {}
        for eid, d in ELEMENTS.items():
            kind = d["kind"]
            spec = E.describe(kind, d)
            kinds = ("wide", "narrow", "half") if kind in ("roster", "certificate") else E.variants(kind, d)
            for variant in kinds:
                for theme in themes:
                    out[(eid, kind, variant, theme["name"])] = self.SET.element(kind, spec, theme, variant)
        return out

    # ------------------------------------------------------------------------------------------ the hand
    def test_it_keeps_to_its_hand_as_its_months_design_whatever_a_page_says(self):
        """`check` finds nothing that breaks the hand in the design drawn as its month's design, with the samples
        and the most and the least a page can say; `test_collection_hand` holds it to its hand with the kit's own
        lines, kept all year and carrying another month's sign."""
        S = self.SET
        c = collections.owner(S.key)
        self.assertIsInstance(S, CollectionSet)
        self.assertEqual((S.collection, S.month), (c.key, c.month_of(S.key)))
        self.assertIs(S.hand, HANDS[c.key])
        self.assertEqual(check(S, [(name, h) for name, (h, _) in self.contents().items() if name != "kit"]), [])

    def test_it_takes_the_name_of_none_of_the_shared_layouts_own_methods_but_its_last_pass(self):
        """A design's own helpers never take the name of one of the shared layouts' own, or the layouts would call the
        design's in its place: a trophy, a game or a footer drawn with the wrong arguments. Only the last pass,
        `_finish`, is a design's to take over."""
        def private(cls):
            return {name for name in vars(cls) if name.startswith("_") and not name.startswith("__")}

        shared = set().union(*(private(cls) for cls in CollectionSet.__mro__))
        self.assertEqual(sorted(private(type(self.SET)) & shared - {"_finish"}), [])

    def test_its_words_are_in_the_hands_inks(self):
        for night in (False, True):
            k = self.SET.ink(night)
            self.assertEqual((k["body"], k["muted"]), (self.SET.hand.body[night], self.SET.hand.muted[night]), night)

    def test_every_light_that_flickers_burns_on_the_hands_flame(self):
        """Whatever flickers by night, in every header wide and on a phone and in every footer, for every shared
        content, is the hand's one flame: its lights, their glows and the light they lay."""
        flame = set(self.SET.hand.ramp("flame"))
        for what, (p, _, _) in (*self.headers(False).items(), *self.footers().items()):
            if what[-1]:
                self.assertLessEqual(flickering(p), flame, what)

    def test_its_titles_glint_on_the_hands_period_only_in_a_wide_moving_header(self):
        S = self.SET
        h = Header(tone="standard", holiday=S.key)
        for code in CODES:
            for theme in (DAY, DARK):
                moving = S.header(code, h, theme, True, True)
                periods = {float(d) for d in self.GLINT.findall(moving)}
                self.assertEqual(periods, {S.hand.glint}, (code, theme["name"]))
                for still in (S.header(code, h, theme, True, False), S.header(code, h, theme, False, False)):
                    self.assertFalse(self.GLINT.findall(still), (code, theme["name"]))

    def test_the_months_mark_hangs_at_the_top_centre_only_as_its_months_design(self):
        month, kept = self.headers(True), self.headers(False)
        for what in month:
            if what[0] in ("kit", "least"):
                self.assertTrue(any(L.startswith("mark") for L in month[what][0].layers), what)
                self.assertFalse(any(L.startswith("mark") for L in kept[what][0].layers), what)

    def test_the_months_marks_box_is_kept_clear_of_every_scene(self):
        """The box the month's mark takes, and two units round it, holds nothing of a header's scene, wide or on a
        phone, by day or by night, for every shared content, whether or not the mark is drawn: only a band hung
        across the top (`garland`) may run on through it unbroken, and only when no mark is there to part round."""
        for marked in (True, False):
            hooks = [h for h in (*self.SCENES, "stars") if marked or h != "garland"]
            for what, (p, by, _) in self.headers(marked).items():
                x0, y0, x1, y1 = self.SET.mark_box(p)
                hits = sorted(xy for xy in merged(by, hooks) if x0 <= xy[0] < x1 and y0 <= xy[1] < y1)
                self.assertEqual(hits[:6], [], (what, marked))

    # ------------------------------------------------------------------------------------------ the words
    def test_every_sprite_keeps_two_units_clear_of_every_word_wide_and_on_a_phone(self):
        """The scenes, the garland, the marks beside a title and what lies on the rules are built to the room the
        words leave: no pixel of theirs lies within two units of a word's box, wide or on a phone, for any of the
        shared contents, by day or by night."""
        for what, (p, by, titles) in self.headers(False).items():
            hits = self.off_words(p, merged(by, self.SCENES), titles)
            self.assertEqual(hits[:6], [], (what, len(hits)))

    def test_every_footer_stands_on_its_footing_one_unit_clear_of_every_word(self):
        """Every footer, F1 and F2, wide and on a phone, by day and by night, for every shared content, stands on the
        design's footing, never bare, and nothing of it comes within a unit of a word."""
        self.assertTrue(self.FOOTINGS, "a design names the hooks that draw its footers' footing")
        for what, (p, by, titles) in self.footers().items():
            pixels = merged(by, self.FOOTINGS)
            self.assertGreaterEqual(len(pixels), p.w // 2, what)
            hits = self.off_words(p, pixels, titles, margin=1)
            self.assertEqual(hits[:6], [], (what, len(hits)))

    # ------------------------------------------------------------------------------------------ phones
    def test_every_phone_header_stands_a_scene_of_the_designs_whatever_its_words_say(self):
        """A phone's H1 stands its scene in the rows it keeps under its words, and a phone's H2 and H3 stand theirs
        in the rows they ask for under theirs, the same rows whatever the title, never beside the words: for every
        shared content, by day and by night, a scene of a few hundred units and more, never a speck."""
        S = self.SET
        for code in ("H2", "H3"):
            rows = S.phone_rows(code, 0)
            self.assertGreater(rows, 0, code)
            self.assertEqual(rows, S.phone_rows(code, 400), code)
        for what, (_, by, _) in self.headers(False).items():
            if not what[2]:
                beside, under = by["scene_narrow"], by["scene_under"]
                scene, other = (beside, under) if what[1] == "H1" else (under, beside)
                self.assertGreaterEqual(len(scene), 300, what)
                self.assertFalse(other, what)

    # ------------------------------------------------------------------------------------------ the budget
    def test_the_most_a_page_can_say_keeps_its_whole_scene_and_its_motion_within_the_budget(self):
        """The most a page can say, every header wide, by day and by night, moving and still, comes out within the
        budget; a moving one moves just as it would at full weight; and each holds every piece of the scene its full
        weight holds, drawn the same."""
        S = self.SET
        most, _ = self.contents()["most"]
        for code in CODES:
            for theme in (DAY, DARK):
                for motion in (True, False):
                    what = (code, theme["name"], motion)
                    svg, drawn = pieces(self.ART, self.PIECES, lambda: S.header(code, most, theme, True, motion))
                    with mock.patch.dict(BUDGET, {"header": 10**9}):
                        full, whole = pieces(self.ART, self.PIECES,
                                             lambda: S.header(code, most, theme, True, motion))
                    self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"], what)
                    self.assertEqual(drawn, whole, what)
                    self.assertEqual(svg.count("<animate"), full.count("<animate"), what)
                    self.assertEqual("<animate" in svg, motion, what)

    def test_an_ordinary_page_is_drawn_at_full_weight_with_room_to_spare(self):
        """Every header of the kit's own lines, of the samples and of the least a page can say, wide or on a phone,
        moving or still, by day and by night, is drawn at its full weight, with its motion, at least 1,500 bytes
        under the budget: drawn with no budget at all it comes out that far under, so within the kit's it is never
        drawn lighter."""
        S, cap = self.SET, BUDGET["header"]
        for name in ("kit", "repository", "profile", "least"):
            h, _ = self.contents()[name]
            for code in CODES:
                for theme in (DAY, DARK):
                    for wide_, motion in ((True, True), (True, False), (False, False)):
                        what = (name, code, theme["name"], wide_, motion)
                        with mock.patch.dict(BUDGET, {"header": 10**9}):
                            svg = S.header(code, h, theme, wide_, motion)
                        self.assertLessEqual(len(svg.encode("utf-8")), cap - 1500, what)
                        self.assertEqual("<animate" in svg, wide_ and motion, what)

    def test_as_its_months_design_its_files_keep_their_room_and_their_motion(self):
        """Drawn as its month's design, with the mark, every header of an ordinary page is drawn at full weight with
        its motion at least 1,500 bytes under the budget, and the most a page can say, drawn lighter where it must be,
        still comes within the budget with all its motion."""
        held, cap = self.SET.on(months_day(self.SET)), BUDGET["header"]
        for name in ("kit", "repository", "profile", "least"):
            h, _ = self.contents()[name]
            for code in CODES:
                for theme in (DAY, DARK):
                    for wide_, motion in ((True, True), (False, False)):
                        with mock.patch.dict(BUDGET, {"header": 10**9}):
                            svg = held.header(code, h, theme, wide_, motion)
                        what = (name, code, theme["name"], wide_)
                        self.assertLessEqual(len(svg.encode("utf-8")), cap - 1500, what)
                        self.assertEqual("<animate" in svg, motion, what)
        most, _ = self.contents()["most"]
        for code in CODES:
            for theme in (DAY, DARK):
                svg = held.header(code, most, theme, True, True)
                with mock.patch.dict(BUDGET, {"header": 10**9}):
                    full = held.header(code, most, theme, True, True)
                self.assertLessEqual(len(svg.encode("utf-8")), cap, (code, theme["name"]))
                self.assertEqual(svg.count("<animate"), full.count("<animate"), (code, theme["name"]))

    def test_a_drawing_made_lighter_keeps_every_piece_and_all_its_motion(self):
        """Made lighter to fit a budget a byte short of its full weight, a header keeps every piece of its scene,
        drawn the same, and all its motion: only texture no one misses at 1x is thinned."""
        S = self.SET
        h, _ = self.contents()["repository"]
        for code in CODES:
            for theme in (DAY, DARK):
                full, whole = pieces(self.ART, self.PIECES, lambda: S.header(code, h, theme, True, True))
                with mock.patch.dict(BUDGET, {"header": len(full.encode("utf-8")) - 1}):
                    lighter, drawn = pieces(self.ART, self.PIECES, lambda: S.header(code, h, theme, True, True))
                self.assertLess(len(lighter), len(full), (code, theme["name"]))
                self.assertEqual(drawn, whole, (code, theme["name"]))
                self.assertEqual(lighter.count("<animate"), full.count("<animate"), (code, theme["name"]))
        self.assertFalse(S._lite, "the design is left drawing lighter")

    # ------------------------------------------------------------------------------------------ the files
    def test_every_file_is_the_designs_well_formed_linted_and_deterministic(self):
        drawn = {(n, c, fn): svg for n, c, fn, svg in self.banners()}
        for (name, code, fn), svg in drawn.items():
            minidom.parseString(svg)
            self.assertIn(f"<!--{KIT} v{KIT_VERSION} {self.key} ", svg, (name, fn))
            self.assertNotIn("<text", svg)
            for ch in DASHES:
                self.assertNotIn(ch, svg)
            cap = BUDGET["link"] if fn.startswith("link-") else BUDGET[DESIGNS[code].kind]
            self.assertEqual(lint(svg, budget=cap, tokens=self.SET.tokens), [], (name, code, fn))
        # Drawn again, the repository's files and those of the most a page can say come out the same, byte for byte.
        for name, code, fn, svg in self.draw_banners(("repository", "most")):
            self.assertEqual(svg, drawn[(name, code, fn)], (name, fn))

    def test_files_are_the_kits_sizes(self):
        for name, code, fn, svg in self.banners():
            w = int(re.search(r'width="(\d+)"', svg).group(1))
            if fn.startswith("link-"):
                self.assertLess(w, 300, fn)
            else:
                self.assertEqual(w, 360 if "narrow" in fn else 830, (name, fn))

    def test_only_a_wide_moving_header_moves(self):
        for name, code, fn, svg in self.banners():
            if "still" in fn or "narrow" in fn or fn.startswith(("footer", "link")):
                self.assertNotIn("<animate", svg, (name, fn))
        h, _ = self.contents()["repository"]
        for code in CODES:
            self.assertIn("<animate", self.SET.header(code, h, DAY, True, True), code)

    def test_text_colours_hold_4_5_on_the_paper_and_every_row_of_the_night(self):
        S = self.SET
        for night in (False, True):
            k = S.ink(night)
            p = Pix(415, 200)
            grounds = {S.bg_at(p, night, y) for y in range(p.h)}
            for role in ("title", "body", "muted", "accent"):
                for ground in grounds:
                    self.assertGreaterEqual(contrast(k[role], ground), 4.5, (night, role, ground))
            self.assertGreaterEqual(contrast(k["tag_ink"], k["tag"]), 4.5, (night, "tag"))

    def test_a_file_too_heavy_is_drawn_lighter_then_still_and_stays_the_designs(self):
        S = self.SET
        h, _ = self.contents()["repository"]
        full = S.header("H2", h, DARK, True, True)
        self.assertIn("<animate", full)
        with mock.patch.dict(BUDGET, {"header": len(full.encode("utf-8")) - 1}):
            lighter = S.header("H2", h, DARK, True, True)
        self.assertLess(len(lighter), len(full))
        self.assertIn("<animate", lighter, "a lighter drawing keeps its motion while it fits")
        self.assertIn(f"{self.key} H2 dark-->", lighter)
        with mock.patch.dict(BUDGET, {"header": 1000}):
            last = S.header("H2", h, DARK, True, True)
        self.assertNotIn("<animate", last, "motion is the last thing to go")
        self.assertFalse(S._lite, "the design is left drawing lighter")

    def test_a_character_its_letters_lack_hands_a_badge_back(self):
        self.assertFalse(self.SET.can_letter("flat", "中文"))

    def test_every_element_is_the_designs_linted_deterministic_and_the_kits_size(self):
        files = self.draw_elements()
        for drawn, svg in self.draw_elements((DAY,)).items():
            self.assertEqual(svg, files[drawn], drawn)          # drawn again, the same, byte for byte
        for (eid, kind, variant, theme), svg in files.items():
            minidom.parseString(svg)
            self.assertIn(f"<!--{KIT} v{KIT_VERSION} {self.key} elements {kind} ", svg, (eid, variant, theme))
            self.assertEqual(lint(svg, budget=BUDGET[E.KINDS[kind][2]], tokens=self.SET.tokens), [],
                             (eid, variant, theme))
            w = int(re.search(r'width="(\d+)"', svg).group(1))
            half = kind == "placard" or variant == "half" or (variant == "narrow" and kind in ("roster", "certificate"))
            self.assertEqual(w, 404 if half else 360 if variant == "narrow" else 830, (eid, variant, theme))

    def test_the_half_page_pair_is_drawn_level(self):
        S = self.SET
        pair = {eid: (d["kind"], E.describe(d["kind"], d)) for eid, d in ELEMENTS.items()
                if d["kind"] in ("roster", "certificate")}
        level = max(S.element_height(kind, spec) for kind, spec in pair.values())
        heights = {re.search(r'height="(\d+)"', S.element(kind, spec, DAY, "half", level)).group(1)
                   for kind, spec in pair.values()}
        self.assertEqual(len(heights), 1)

    def test_odd_data_is_drawn_whole(self):
        S = self.SET
        bare = {"kind": "roster", "subject": "x/y", "people": [
            {"name": "A PERSON WITH A NAME FAR LONGER THAN A COLUMN", "handle": "@" + "h" * 30, "initials": "AP",
             "n": 3, "first": "1 JAN 2020", "last": "31 DEC 2026"}]}
        svg = S.element("roster", E.describe("roster", bare), DAY, "wide")
        self.assertEqual(lint(svg, budget=BUDGET["sheet"], tokens=S.tokens), [])
        cert = dict(ELEMENTS["conformance"], name="an-extraordinarily-long-name",
                    ring_bottom="V12 · VERIFIED 31 DECEMBER 2026 AT LENGTH")
        for variant in ("wide", "half"):
            svg = S.element("certificate", E.describe("certificate", cert), DARK, variant)
            self.assertEqual(lint(svg, budget=BUDGET["sheet"], tokens=S.tokens), [], variant)

    def badge(self, style, **kw):
        args = dict(style=style, label="Build", message="Passing", icon="pulse", label_hex=PALETTE["black"],
                    message_hex=PALETTE["blue"], live=False, state=None, reserve=(), rels=["static/b.svg"], stamp=STAMP)
        args.update(kw)
        return self.SET.badge(**args)

    def badge_file(self, svg, px_height, what):
        self.assertEqual(BD.lint(svg), [], what)
        self.assertEqual(colours(svg, self.SET.tokens), [], what)
        minidom.parseString(svg)
        self.assertEqual(int(re.search(r'height="(\d+)"', svg).group(1)), px_height, what)

    def test_every_badge_style_classic_plate_and_live_is_the_kits_height_and_files(self):
        for style in BADGE_STYLES:
            one = self.badge(style)
            self.assertEqual(list(one), ["static/b.svg"])
            self.badge_file(one["static/b.svg"], HEIGHTS[style], style)
            two = self.badge(PLATE + style, rels=["static/b.svg", "static/b-dark.svg"])
            self.assertEqual(list(two), ["static/b.svg", "static/b-dark.svg"])
            self.assertNotEqual(*two.values())
            for rel, svg in two.items():
                self.badge_file(svg, HEIGHTS[style], (style, rel))
            for state in STATES:
                for form in (style, PLATE + style):
                    live = self.badge(form, live=True, state=state, label_hex=PALETTE["gold"],
                                      message_hex=PALETTE[state], rels=["dynamic/b.svg"])
                    self.assertEqual(list(live), ["dynamic/b.svg"])
                    self.badge_file(live["dynamic/b.svg"], HEIGHTS[style], (form, state))

    def test_a_live_plate_keeps_its_width_whatever_it_says(self):
        widths = set()
        for state, message in (("green", "Passing"), ("red", "Failing"), ("slate", "No Data")):
            svg = self.badge(PLATE + "flat", live=True, state=state, message=message,
                             reserve=("Passing", "Failing", "No Data"), rels=["dynamic/b.svg"])["dynamic/b.svg"]
            widths.add(re.search(r'width="(\d+)"', svg).group(1))
        self.assertEqual(len(widths), 1)

    def test_every_badges_letters_hold_4_5_on_their_block(self):
        S = self.SET
        pairs = [("label", *S.badge_label()), ("gold", *S.badge_gold())]
        pairs += [(f"state {s}", *S.badge_states()[s]) for s in STATES]
        pairs += [(f"swatch {n}", bg, ink) for n, (bg, ink, _) in S.badge_swatches().items()]
        for mode in ("day", "night"):
            k = S.plate_colours(mode)
            pairs += [(f"{mode} block", k["block"], k["letters"]), (f"{mode} paper", k["paper"], k["ink"]),
                      (f"{mode} dot", k["dot"], k["ink"])]
        k = S.plate_colours("live")
        pairs += [("live paper", k["paper"], k["ink"]), ("live dot", k["dot"], k["ink"])]
        for what, ground, ink in pairs:
            self.assertGreaterEqual(contrast(ink, ground), 4.5, what)

    def test_the_swatches_cover_every_family_a_written_colour_comes_in(self):
        swatches = self.SET.badge_swatches()
        self.assertGreaterEqual(len(swatches), 10)
        for name, (block, _, _) in swatches.items():
            self.assertIn(block, self.badge("flat", message_hex=block)["static/b.svg"], name)

    def test_what_its_letters_cannot_draw_is_left_to_the_kit(self):
        self.assertIsNone(self.badge("flat", message="中文"))
