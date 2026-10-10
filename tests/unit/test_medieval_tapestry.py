# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Tapestry set's own rules, which the checks every set shares cannot know: what the night alone shows (the torches
in their brackets with their flames, smoke and wide pools of light, the gold the letters are couched in) stays out of
the day's files; a title is laid in wool, a letter a colour, couched round, each letter kept once a file; the charge
is two knights drawn from one hand set shape, one further back and higher than the other; every header stands on the
lower border; the comet drifts and the horses gallop only in a wide moving header; every phone header has a scene of
the set's, beside its words or under them; every sprite keeps clear of every word on the phones and the wide headers
alike; the most a page can say keeps its whole scene and its motion within the budget, drawn lighter only in its
texture; a footer is never bare, its words sit clear of its frame, it stands on the lower border wherever its words
leave it the rows, and it carries the comet, at a title block's right end over the border's beasts and beside a
scale bar; the elements are stitched (laid columns, a wheel of fortune, whip stitched cards, couched wires,
gonfanons); a running stitch of cream thread lies inside every badge's edge; and a counter's numerals hold 4.5:1 on
their patches. It keeps to the medieval collection's hand as October's design and kept all year: its words in the
hand's inks and its linen in the hand's bands, its torches on the hand's flame, its people on the hand's skins, the
great horseman the knight grown twice and Harold grown twice as he is, the border band pausing whole and even about
the month's mark and no scene near it, its heroes at the composition's measure and the comet on the hand's slow
sweep. The set is a theme, not a holiday on the calendar, so the checks every registered set shares run here over
the set directly, with the same contents and the same entry points."""
from __future__ import annotations

import datetime as dt
import re
import unittest
import xml.dom.minidom as minidom
from unittest import mock

from tests import support
from tests.unit.test_holiday_sets import DASHES, ELEMENTS, HEIGHTS, STAMP, contents

from domain import KIT, KIT_VERSION
from domain.badges import data as BD
from domain.banners.content import Footer, Header
from domain.banners.designs import DESIGNS, variants
from domain.canvas import BUDGET, DARK, DAY, colours, lint
from domain.elements import draw as E
from domain.holidays.designs.badges import PLATE, STATES, STYLES as BADGE_STYLES
from domain.collections.hand import CollectionSet, check, lab
from domain.collections.medieval_tapestry import PHONE_UNDER, SET, art as A
from domain.collections.medieval_tapestry.palette import NIGHT_SKY, RAMP
from domain.holidays.designs.banners import MARK_Y
from domain.holidays.pixel import Pix, contrast
from domain.palette import PALETTE

support.install()
KEY = SET.key
HEADER = Header(tone="standard", holiday=KEY)
FOOTER = Footer(tone="standard", holiday=KEY)
FLAME, GOLD, LINEN, STEEL = RAMP["flame"], RAMP["gold"], RAMP["linen"], RAMP["steel"]
ITS_DAY = dt.date(2026, 10, 1)    # a day in October, which makes the Tapestry the collection's design for the month


def draw_banners() -> list:
    """Every banner file the set draws for the shared contents: (content, code, file name, svg), as the kit
    would ask for them, variant by variant."""
    out = []
    for name, (h, f) in contents(KEY).items():
        for code, design in DESIGNS.items():
            content = h if design.kind == "header" else f
            drawer = SET.header if design.kind == "header" else SET.footer
            for suffix, wide, motion, theme in variants(design):
                out.append((name, code, f"{design.kind}-{suffix}.svg", drawer(code, content, theme, wide, motion)))
            if design.kind == "footer" and design.chip and content.on("links"):
                for i, (label, _) in enumerate(content.links):
                    for theme in (DAY, DARK):
                        out.append((name, code, f"link-{i}-{theme['name']}.svg", SET.link(label, theme, i)))
    return out


DRAWN: list = []


def every_banner() -> list:
    if not DRAWN:
        DRAWN.extend(draw_banners())
    return DRAWN


def sprites(draw, *hooks) -> tuple:
    """`draw()`'s drawing, and every pixel of the sprites the set's `hooks` (names of its drawing hooks) put
    on it, gathered as they draw: their pixels on every layer and the cells of the symbols they place."""
    pixels, cells = set(), {}
    symbol = Pix.symbol

    def kept(self, key, cells_=None, shapes="", mono=False):
        sid = symbol(self, key, cells_, shapes, mono)
        cells.setdefault(sid, set(cells_ or ()))
        return sid

    def watched(hook):
        def drawn(*args, **kw):
            p = next(a for a in args if isinstance(a, Pix))
            before = {L: set(c) for L, c in p.layers.items()}
            placed = {L: len(u) for L, u in p.uses.items()}
            out = hook(*args, **kw)
            for L, c in p.layers.items():
                pixels.update(set(c) - before.get(L, set()))
            for L, uses in p.uses.items():
                for (_, sid, x, y, s) in uses[placed.get(L, 0):]:
                    pixels.update((x + dx * s, y + dy * s) for dx, dy in cells.get(sid, ()))
            return out
        return drawn

    with mock.patch.object(Pix, "symbol", kept), \
            mock.patch.multiple(SET, **{name: watched(getattr(SET, name)) for name in hooks}):
        p = draw()
    return p, pixels


def off_words(p: Pix, pixels, margin=2) -> list:
    """The pixels among `pixels` that lie within `margin` units of a word's box."""
    return sorted(xy for xy in pixels if not p.clear_of_words(xy[0] - margin, xy[1] - margin, xy[0] + margin + 1,
                                                             xy[1] + margin + 1))


def draw_elements() -> dict:
    """Every element file for the shared specimen, by the kit's name, drawn as the kit asks for them."""
    out = {}
    for eid, d in ELEMENTS.items():
        kind = d["kind"]
        spec = E.describe(kind, d)
        kinds = ("wide", "narrow", "half") if kind in ("roster", "certificate") else E.variants(kind, d)
        for variant in kinds:
            for theme in (DAY, DARK):
                out[(eid, kind, variant, theme["name"])] = SET.element(kind, spec, theme, variant)
    return out


def heads():
    """Every header file of the kit's own lines, day and night, wide and on a phone: (code, wide, day, night)."""
    for code in ("H1", "H2", "H3"):
        for wide in (True, False):
            yield code, wide, SET.header(code, HEADER, DAY, wide, wide), SET.header(code, HEADER, DARK, wide, wide)


class Night(unittest.TestCase):
    def test_what_the_night_alone_shows_stays_out_of_the_day(self):
        """The torches, their flames, their smoke and the pools of their light are the night's, and so is the gold
        the letters are couched in; by day the hall is unlit."""
        for code, wide, day, night in heads():
            for colour in (FLAME[6], FLAME[5], f'<g stroke="{GOLD[2]}">'):
                self.assertNotIn(colour, day, (code, wide, colour))
                self.assertIn(colour, night, (code, wide, colour))
            self.assertNotIn("<ellipse", day, (code, wide, "a pool of torchlight"))
            self.assertIn("<ellipse", night, (code, wide, "the pools of torchlight"))
            if wide:
                self.assertNotIn('values="1;.28;1"', day, (code, "no smoke or glint by day"))
                self.assertIn('values="1;.28;1"', night, (code, "the smoke drifts off the flames"))
        for code in ("F1", "F2"):
            for wide in (True, False):
                self.assertNotIn(FLAME[6], SET.footer(code, FOOTER, DAY, wide, False), (code, wide))
        self.assertIn(FLAME[6], SET.footer("F1", FOOTER, DARK, True, False), "a torch at the corner of the notes")
        self.assertIn(STEEL[5], SET.footer("F1", FOOTER, DAY, True, False), "the needle by day")

    def test_the_torches_pool_their_light_wide_and_the_cloth_falls_to_umber(self):
        """A wide sheet's torches pool their light wide on the linen, a phone's narrower; and the night's linen
        falls from the warmth under the torches to umber at its foot."""
        for wide, reach in ((True, 90), (False, 55)):
            svg = SET.header("H1", HEADER, DARK, wide, False)
            widest = max(float(rx) for rx in re.findall(r'<ellipse[^>]* rx="([\d.]+)"', svg))
            self.assertGreaterEqual(widest, reach, wide)
        light = [sum(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in NIGHT_SKY]
        self.assertEqual(light, sorted(light, reverse=True))
        self.assertLess(light[-1], light[0] * 0.7)

    def test_a_gold_thread_runs_along_the_letters_upper_and_left_edges_by_night_only(self):
        """By night every letter is couched in gold and carries a gold thread along the upper edge of each stroke
        and down its left, kept in the letter's own symbol, with a few stitches glinting; by day it has none of
        them. The loose ends of the couching thread lie over the letters by day and by night."""
        for night in (False, True):
            kept = {}
            symbol = Pix.symbol

            def keep(self, key, cells=None, shapes="", mono=False):
                kept[key] = dict(cells or {})
                return symbol(self, key, cells, shapes, mono)
            p = Pix(200, 40)
            A.paper(p, night)
            with mock.patch.object(Pix, "symbol", keep):
                A.title(p, 10, 10, "BANNERS", 3, night, SET.ink(night)["title"])
            gold = kept[("letter", "B", 3, night)]
            self.assertEqual(bool(gold), night, night)
            if night:
                ink = A.inked(0, 0, "B", 3)
                self.assertEqual({xy for xy, c in gold.items() if c == GOLD[5]},
                                 {(x, y) for (x, y) in ink if (x, y - 1) not in ink}, "along every upper edge")
                self.assertEqual({xy for xy, c in gold.items() if c == GOLD[4]},
                                 {(x, y) for (x, y) in ink if (x, y - 1) in ink and (x - 1, y) not in ink},
                                 "and down every left one")
            glints = [c for L in ("tw0", "tw1", "tw2") for c in p.layers.get(L, {}).values()]
            self.assertEqual(GOLD[6] in glints, night, night)
            self.assertTrue(p.layers.get("base~"), "the thread ends are laid over the letters")

    def test_the_torches_light_the_linen_in_a_moving_header_and_hold_still_otherwise(self):
        moving = SET.header("H1", HEADER, DARK, True, True)
        self.assertIn('values="1;.62;.94;.5;1;.8"', moving, "the flames flicker")
        for still in (SET.header("H1", HEADER, DARK, True, False), SET.header("H1", HEADER, DARK, False, False)):
            self.assertNotIn("<animate", still)
            self.assertIn(FLAME[6], still, "the torches still burn")


class Charge(unittest.TestCase):
    def test_the_two_knights_are_one_hand_set_shape_one_further_back_and_higher(self):
        """The charge's knights are drawn from one shape kept once in the file, each in his own layer and his own
        wools; the knight behind rides further back and higher, and the two overlap only at their edges."""
        p = SET.h1(HEADER, False, True)
        fixed, monos = p.syms[("shape", ("knight", "lance", False, False))]
        sid = p.syms[fixed]
        (rear,) = [(x, y) for (_, s, x, y, _) in p.uses["kr"] if s == sid]
        (front,) = [(x, y) for (_, s, x, y, _) in p.uses["kf"] if s == sid]
        self.assertLess(rear[0], front[0], "further back")
        self.assertLessEqual(rear[1], front[1] - 20, "and higher")
        self.assertIn("horse", monos)
        colours = {L: {stroke for (stroke, s, *_) in p.uses[L] if s == p.syms[monos["horse"]]} for L in ("kr", "kf")}
        self.assertNotEqual(colours["kr"], colours["kf"], "each horse in a wool of its own")
        shape = set(A.knight_cells("lance"))
        behind = {(x + rear[0], y + rear[1]) for (x, y) in shape}
        before = {(x + front[0], y + rear[1] + (front[1] - rear[1])) for (x, y) in shape}
        self.assertLess(len(behind & before), len(shape) // 20, "overlapping only at the edges")
        moving = SET.header("H1", HEADER, DAY, True, True)
        self.assertEqual(moving.count('dur=".66s"'), 3, "three moments of the gallop")

    def test_the_horse_stands_on_four_legs_at_every_moment(self):
        """Every moment of the gallop and the stand has its near legs, its far legs and four hooves."""
        for frame in (0, 1, 2, "stand"):
            cells = A.legs_cells(frame)
            roles = set(cells.values())
            self.assertTrue({"horse", "deep", "ink"} <= roles, frame)
        for rows in (*A.GALLOP, A.STAND):
            self.assertGreaterEqual(rows[-1].count("k") + rows[-2].count("k"), 6)

    def test_the_shield_wall_lays_every_shield_over_every_man(self):
        """Three men stand in the wall, every shield laid over every man, their spears behind them."""
        p = SET.h1(HEADER, False, True)
        men = [p.meta[f"wm{i}"][0] for i in range(3)]
        shields = [p.meta[f"ws{i}"][0] for i in range(3)]
        self.assertLess(max(men), min(shields))
        self.assertLess(p.meta["sp"][0], min(men), "the spears behind the men")
        self.assertGreater(len(p.layers["sp"]), 20, "three spears")


class LowerBorder(unittest.TestCase):
    def test_every_header_stands_on_the_lower_border(self):
        """Every header, wide or on a phone, whatever it says, has the lower border's braid over its stats rule."""
        for name, (h, _) in contents(KEY).items():
            for code in ("H1", "H2", "H3"):
                for wide in (True, False):
                    for theme, braid in ((DAY, 'id="brd"'), (DARK, 'id="brn"')):
                        self.assertIn(braid, SET.header(code, h, theme, wide, False), (name, code, wide, theme["name"]))

    def test_the_band_holds_its_beasts_where_the_words_leave_it_room_and_steps_down_where_they_do_not(self):
        p = SET.h1(HEADER, False, True)
        rule = max(y for (x, y), c in p.layers["base"].items() if c == SET.ink(False)["rule"] and x == 200)
        levels = {lv for _, _, lv in A.band_spans(p, 5, 410, rule)}
        self.assertIn(2, levels, "beasts and knots where there is room")
        self.assertIn(1, levels, "the braid alone under the note")
        beasts = {p.syms[k] for k in p.syms if isinstance(k, tuple) and k[0] == "beast"}
        low = [y for (_, s, x, y, _) in p.uses["base"] if s in beasts and y > rule - A.LOW - 2]
        self.assertTrue(low, "the border's beasts walk along the lower band")


class Motion(unittest.TestCase):
    def test_the_comet_drifts_and_the_horses_gallop_only_in_a_wide_moving_header(self):
        moving = SET.header("H1", HEADER, DAY, True, True)
        self.assertIn('clip-path="url(#cmc)"', moving, "the comet crosses behind the band")
        drifts = re.findall(r'<animateTransform attributeName="transform" type="translate" values="([^"]*)"', moving)
        self.assertEqual([[int(v) for v in d.split(";")] for d in drifts], [list(range(16)), list(range(0, 384, 16))],
                         "a pixel at a time, sixteen times over, carried a stride of sixteen at a time")
        self.assertEqual(moving.count('dur=".66s"'), 3, "three moments of the gallop")
        self.assertEqual(moving.count('dur="1.2s"'), 3, "three moments of the wave")
        p = SET.h1(HEADER, False, True)
        self.assertEqual([len(p.uses[f"pennon{k}"]) for k in range(3)], [2, 2, 2], "both knights' pennons in each")
        still = SET.header("H1", HEADER, DAY, True, False)
        self.assertIn('clip-path="url(#cmc)"', still, "the comet rests among the beasts")
        self.assertNotIn("<animate", still)
        narrow = SET.header("H1", HEADER, DAY, False, False)
        self.assertNotIn("cmc", narrow, "no comet on a phone")
        self.assertNotIn("<animate", narrow)

    def test_the_horseman_stands_with_his_banner_waving_beside_a_section(self):
        moving = SET.header("H2", HEADER, DAY, True, True)
        self.assertEqual(moving.count('dur="1.2s"'), 3, "three moments of the banner's wave")
        self.assertNotIn('dur=".66s"', moving, "a standing horse")


def served(code, h, theme, motion, month: bool = False) -> tuple:
    """A wide header's file as the kit serves it (drawn lighter, or held still, only if it must be to fit), and the
    drawing it was made from; with `month`, drawn as the collection's design for the month, with its mark."""
    held = SET.on(ITS_DAY) if month else SET
    made = []
    canvas = held.canvas

    def kept(w, hh):
        made.append(canvas(w, hh))
        return made[-1]
    with mock.patch.object(held, "canvas", kept):
        svg = held.header(code, h, theme, True, motion)
    return svg, made[-1]


def drawn(code, h, theme, motion, lite: bool, month: bool = False) -> tuple:
    """A wide header's file at full weight, or drawn lighter as the kit draws a file over its budget, whatever its
    size, and the drawing it was made from."""
    with mock.patch.object(SET, "_fitted", lambda draw, budget, *then: draw()), mock.patch.object(SET, "_lite", lite):
        return served(code, h, theme, motion, month)


def figures(p: Pix) -> set:
    """Every figure a drawing keeps as a symbol (the knights, the men of the wall and their shields, the border's
    beasts and knots, the comet, the pennons and banners, the letters), however plainly stitched; and every layer
    it draws in but the loose thread ends."""
    keys = {(k[0], k[1][:4] if k[0] == "shape" else k[1:]) for k in p.syms
            if isinstance(k, tuple) and k[0] in ("shape", "beast", "knot", "comet", "pennon", "standard", "letter")}
    return keys | {L for L in p.layers if L != "base~" and (p.layers[L] or p.uses[L] or p.shapes[L])}


class Lighter(unittest.TestCase):
    def test_the_most_a_page_can_say_keeps_its_whole_scene_and_its_motion_within_the_budget(self):
        """The most content's wide H1 and H2, by day and by night, moving and still, drawn as the kit draws them as
        the month's design with its mark and kept all year without it, come out within the budget, at full weight
        or drawn lighter but never held still; the moving ones move; and
        each, and each drawn lighter whether or not it must be, holds every figure and every layer the drawing at
        full weight holds: on H1 the two knights of the charge on their galloping horses with their pennons, the
        shield wall with its spears and the tall tree; the border's beasts and the comet; the title in its wools;
        and by night the torches with their flames, smoke and pools of light, and the gold of the letters. A drawing
        made lighter thins only texture: the slubs, the vine's variety, the turnings of the rod, the laid work of
        the horses and the rings of the mail, and the loose ends of the couching thread."""
        most, _ = contents(KEY)["most"]
        for code, month in ((code, month) for code in ("H1", "H2") for month in (False, True)):
            for theme in (DAY, DARK):
                night = bool(theme["dark"])
                for motion in (True, False):
                    what = (code, theme["name"], motion, month)
                    full, whole = drawn(code, most, theme, motion, False, month)
                    light, thin = drawn(code, most, theme, motion, True, month)
                    svg, p = served(code, most, theme, motion, month)
                    self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"], what)
                    self.assertIn(svg, (full, light), (what, "at full weight or lighter, never held still"))
                    for drawing, made in ((svg, p), (light, thin)):
                        self.assertEqual("<animate" in drawing, motion, what)
                        self.assertEqual(figures(made), figures(whole), what)
                        self.assertIn('clip-path="url(#cmc)"', drawing, (what, "the comet"))
                        beasts = {k[1] for k in made.syms if isinstance(k, tuple) and k[0] == "beast"}
                        self.assertGreaterEqual(len(beasts), 3, (what, "the border's beasts"))
                        self.assertEqual(sum(f'id="pawool2{"n" if night else "d"}{v}"' in drawing for v in range(4)), 4,
                                         (what, "the title in its four wools"))
                        if night:
                            self.assertIn(FLAME[6], drawing, (what, "the torches' flames"))
                            self.assertEqual(drawing.count("<ellipse"), full.count("<ellipse"), (what, "their pools"))
                            self.assertIn(GOLD[5], drawing, (what, "the gold along the letters"))
                        if code == "H1":
                            self.assertTrue(made.uses["kr"] and made.uses["kf"], (what, "two knights in the charge"))
                            self.assertTrue(all(made.uses[f"wm{i}"] and made.uses[f"ws{i}"] for i in range(3)),
                                            (what, "the shield wall"))
                            self.assertGreater(len(made.layers["sp"]), 20, (what, "the wall's spears"))
                            self.assertGreater(len(made.layers["tr"]), 300, (what, "the tall tree"))
                            if motion:
                                self.assertEqual(drawing.count('dur=".66s"'), 3, (what, "the horses gallop"))
                                self.assertEqual(drawing.count('dur="1.2s"'), 3, (what, "the pennons wave"))
                                self.assertEqual(drawing.count("<animateTransform"), 2, (what, "the comet drifts"))
                    self.assertLess(len(light), len(full), (what, "and lighter it is lighter"))


class Phones(unittest.TestCase):
    def test_every_sprite_keeps_two_units_clear_of_every_word_on_a_phone(self):
        """On a phone the knight, the tree, the man of the wall, the bands and the section mark are built to the rows
        the words leave free: no pixel of theirs lies within two units of a word's box, for any of the shared
        contents, by day or by night."""
        drawers = {"H1": SET.h1_narrow, "H2": SET.h2_narrow, "H3": SET.h3_narrow}
        for name, (h, _) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    p, pixels = sprites(lambda: drawer(h, night), "frame", "scene_narrow", "scene_under", "garland",
                                        "section_mark", "rule_decor", "phone_band")
                    hits = off_words(p, pixels)
                    self.assertEqual(hits[:6], [], (name, code, night, len(hits)))

    def test_every_sprite_keeps_two_units_clear_of_every_word_on_a_wide_header_too(self):
        """The charge, the shield wall, the horseman, the hunt, the trees, the bands, the marks beside a title and
        the lower border keep the same two units from every word across a wide header."""
        drawers = {"H1": SET.h1, "H2": SET.h2, "H3": SET.h3}
        for name, (h, _) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    p, pixels = sprites(lambda: drawer(h, night, True), "frame", "scene", "garland", "section_mark",
                                        "strip_mark", "rule_decor")
                    hits = off_words(p, pixels)
                    self.assertEqual(hits[:6], [], (name, code, night, len(hits)))

    def test_every_phone_header_has_a_scene_of_the_sets_by_day_and_by_night(self):
        """Every phone header, H1, H2 and H3, for every shared content, by day and by night, has a scene of the
        set's own: figures its scene hooks stand over the lower border (a knight, a man of the wall, a hound, the
        tree), not the border alone. No phone's title leaves an H2's or an H3's hero its height beside the words, so
        every phone's H2 and H3 asks for rows under its words and the great horseman or the great hunt stands there
        (see `PHONE_UNDER`); an H1's scene stands under its words as it always has."""
        drawers = {"H1": SET.h1_narrow, "H2": SET.h2_narrow, "H3": SET.h3_narrow}
        under = {(name, code) for name in contents(KEY) for code in ("H2", "H3")}
        for name, (h, _) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    with mock.patch.object(A, "lower_band", lambda *a, **k: None):
                        p, pixels = sprites(lambda: drawer(h, night), "scene_narrow", "scene_under")
                    self.assertGreater(len(pixels), 200, (name, code, night))
                    asked = []
                    with mock.patch.object(type(SET), "scene_under",
                                           lambda self, design, p, y0, y1, night: asked.append(y1 - y0)):
                        drawer(h, night)
                    self.assertEqual(bool(asked), (name, code) in under, (name, code, night))
                    self.assertTrue(all(rows >= PHONE_UNDER[code] for rows in asked), (name, code, asked))

    def test_the_scenes_stand_where_the_words_leave_them_room(self):
        """The kit's own lines leave each phone its scene, and its H1 a knight at the gallop; the least a page can
        say leaves the knights their charge; and the most, which leaves its H1's phone the least room, has its
        scene built to the rows it has rather than over a word."""
        h, _ = contents(KEY)["kit"]
        for code in ("H1", "H2", "H3"):
            p, pixels = sprites(lambda: {"H1": SET.h1_narrow, "H2": SET.h2_narrow, "H3": SET.h3_narrow}[code](h, False),
                                "scene_narrow", "scene_under")
            self.assertTrue(pixels, (code, "a scene on the kit's own phone"))
        p = SET.h1_narrow(h, False)
        self.assertIn(("shape", ("knight", "lance", False, False)), p.syms, "a knight on the kit's own phone")
        least, _ = contents(KEY)["least"]
        svg = SET.header("H1", least, DAY, True, True)
        self.assertEqual(svg.count('dur=".66s"'), 3, "the knights gallop")
        most, _ = contents(KEY)["most"]
        p, pixels = sprites(lambda: SET.h1_narrow(most, False), "scene_narrow")
        self.assertEqual(off_words(p, pixels), [])


class Titles(unittest.TestCase):
    def test_a_title_is_laid_in_wool_a_letter_a_colour_and_couched_round(self):
        day = SET.header("H1", HEADER, DAY, True, True)
        for variant in range(4):
            self.assertIn(f'id="pawool4d{variant}"', day, f"the {variant}th wool, laid work at the title's size")
        self.assertIn(f'<g stroke="{RAMP["umber"][1]}">', day, "the couching thread round every letter")
        night = SET.header("H1", HEADER, DARK, True, True)
        self.assertIn('id="pawool4n0"', night)
        self.assertIn(f'<g stroke="{GOLD[2]}">', night, "couched in gold by night")
        self.assertIn(GOLD[5], night, "a gold thread along the upper edges")
        self.assertNotIn("stroke-opacity", day.split("<defs>")[0], "no glow")

    def test_a_letter_is_kept_once_a_file_and_placed_once_a_letter(self):
        """A letter, its couching and by night its gold, is one symbol kept once a file for each letter and size,
        placed once a letter in the wool of its place: so the longest title a page may have, forty of one letter,
        keeps one letter and costs a use a letter, in the four wools by turns."""
        p = Pix(300, 40)
        A.paper(p, False)
        A.title(p, 10, 10, "BANANA", 4, False, SET.ink(False)["title"])
        letters = {sid: key for key, sid in p.syms.items() if isinstance(key, tuple) and key[0] == "letter"}
        self.assertEqual(sorted(key[1] for key in letters.values()), ["A", "B", "N"])
        self.assertEqual(sum(1 for (_, sid, _, _, _) in p.uses["base"] if sid in letters), 6)
        p = Pix(415, 60)
        A.paper(p, True)
        A.title(p, 10, 10, "W" * 40, 2, True, SET.ink(True)["title"])
        letters = {sid: key for key, sid in p.syms.items() if isinstance(key, tuple) and key[0] == "letter"}
        self.assertEqual([key[1] for key in letters.values()], ["W"])
        placed = [u for u in p.uses["base"] if u[1] in letters]
        self.assertEqual(len(placed), 40)
        self.assertEqual({stroke for stroke, *_ in placed}, {f"url(#pawool2n{v})" for v in range(4)}, "four wools")
        self.assertTrue(all(scale == 1 for (*_, scale) in placed), "each placed as it is, its size in the symbol")


class Footers(unittest.TestCase):
    def test_a_footer_is_never_bare(self):
        """A footer hangs from its rod, stands on its hem and the fringe along its foot (on the lower border too
        where its words leave the rows), and has the needle (the torch by night) at the corner of its notes."""
        for code in ("F1", "F2"):
            for wide in (True, False):
                day = SET.footer(code, FOOTER, DAY, wide, False)
                night = SET.footer(code, FOOTER, DARK, wide, False)
                self.assertIn('id="frd3"', day, (code, wide, "the fringe"))
                self.assertIn('id="frn3"', night, (code, wide, "the fringe"))
                self.assertIn('id="hmfd"', day, (code, wide, "the hem along its foot"))
                if code == "F2":
                    self.assertIn('id="brd"', day, (code, wide, "the braid of the lower border"))
                    self.assertIn('id="brn"', night, (code, wide, "the braid of the lower border"))
            if code == "F1":
                self.assertIn(STEEL[5], SET.footer(code, FOOTER, DAY, True, False), "the needle")
                self.assertIn(FLAME[6], SET.footer(code, FOOTER, DARK, True, False), "the torch")

    def test_a_footer_stands_on_the_lower_border_wherever_its_words_leave_the_rows(self):
        """A footer's floor is the lower border sewn on its hem: the braid wherever its words leave it the rows, a
        couched rule over it along every stretch where they leave one more, and the border's beasts walking along
        every long stretch they leave free to the band's full height, closed at each end by an upright; a scrap too
        short to read as a border is left off and the hem shows bare. A title block with no notes raises the full
        band after its cells, and a sheet with a scale bar runs on the braid at least."""
        drawers = {"F1": SET.f1, "F2": SET.f2, "F1 narrow": SET.f1_narrow, "F2 narrow": SET.f2_narrow}
        for name, (_, f) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    what = (name, code, night)
                    p = drawer(f, night)
                    spans = A.foot_spans(p)
                    runs: list = []
                    for a, b, lv in spans:
                        if lv and runs and runs[-1][1] == a:
                            runs[-1][1] = b
                        elif lv:
                            runs.append([a, b])
                        if lv == 3:
                            self.assertGreaterEqual(b - a, A.FOOT_BEASTS, (what, a, b))
                        if lv == 2:
                            self.assertGreaterEqual(b - a, A.FOOT_RULE, (what, a, b))
                    self.assertTrue(all(b - a >= A.FOOT_LEAST for a, b in runs), (what, runs))
                    if code in ("F2", "F2 narrow"):
                        self.assertTrue(any(lv for _, _, lv in spans), (what, "the braid along the scale bar's sheet"))
                    if code == "F1" and not f.get("closing"):
                        self.assertEqual(spans[-1][2], 3, (what, "the full band after the cells"))
                        beasts = {sid for key, sid in p.syms.items() if isinstance(key, tuple) and key[0] == "beast"}
                        self.assertTrue([u for u in p.uses["base"] if u[1] in beasts and u[2] >= spans[-1][0]],
                                        (what, "the border's beasts walk along it"))

    def test_the_comet_is_the_footers_mark(self):
        """Halley's comet, the design's mark: on a title block with no notes the great comet flies over the border's
        beasts at its right end, after the last of its words, with a torch beside it by night; beside the scale bar
        in its cell lies the comet, falling with its tail streaming up behind it on a wide sheet and level on a
        phone's; a title block with notes keeps the needle at their corner, and a phone's, its cells across it, has
        no room for the comet."""
        cells = {("F2", True): (70, 94, (3,)), ("F2", False): (64, 98, (2,))}
        for name, (_, f) in contents(KEY).items():
            for code in ("F1", "F2"):
                for wide in (True, False):
                    for night in (False, True):
                        what = (name, code, wide, night)
                        p = {("F1", True): SET.f1, ("F2", True): SET.f2, ("F1", False): SET.f1_narrow,
                             ("F2", False): SET.f2_narrow}[(code, wide)](f, night)
                        kinds = {sid: key[1] for key, sid in p.syms.items() if isinstance(key, tuple)
                                 and key[0] == "greatcomet"}
                        comets = [(x, y, kinds[sid]) for (_, sid, x, y, _) in p.uses["base"] if sid in kinds]
                        if code == "F1" and not (wide and not f.get("closing")):
                            self.assertEqual(comets, [], what)
                            continue
                        self.assertEqual(len(comets), 1, what)
                        x, y, size = comets[0]
                        w = max(c for c, _ in A.great_comet_cells(size)) + 1
                        h = max(r for _, r in A.great_comet_cells(size)) + 1
                        if code == "F1":
                            self.assertEqual(size, 0, what)
                            self.assertGreaterEqual(x, max(b[2] for b in p.words) + 2, (what, "after the words"))
                            self.assertLess(y + h, p.h - 14, (what, "over the border's beasts"))
                            self.assertEqual(bool(p.lamps), night, (what, "a torch beside it by night"))
                        else:
                            x0, x1, sizes = cells[(code, wide)]
                            self.assertIn(size, sizes, what)
                            self.assertTrue(x0 <= x and x + w <= x1, (what, "beside the bar, in its cell"))

    def test_a_footers_floor_and_comet_keep_two_units_clear_of_every_word(self):
        """The border's beasts and uprights, the comet and the torch by night keep two units from every word of a
        footer, wide and on a phone, for every shared content."""
        drawers = (SET.f1, SET.f2, SET.f1_narrow, SET.f2_narrow)
        for name, (_, f) in contents(KEY).items():
            for drawer in drawers:
                for night in (False, True):
                    p, pixels = sprites(lambda: drawer(f, night), "_footed")
                    self.assertEqual(off_words(p, pixels)[:6], [], (name, drawer.__name__, night))

    def test_a_footers_words_sit_clear_of_its_frame(self):
        """No band of knotwork is laid under a footer's rod, where its words stand: nothing of the frame lies
        between the top hem and the words but the hems down its sides."""
        for code in ("F1", "F2"):
            for wide in (True, False):
                for night in (False, True):
                    p = {("F1", True): SET.f1, ("F2", True): SET.f2, ("F1", False): SET.f1_narrow,
                         ("F2", False): SET.f2_narrow}[(code, wide)](FOOTER, night)
                    rows = [(float(x), float(y), float(w), float(h)) for x, y, w, h in
                            re.findall(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"',
                                       "".join(p.shapes["base"]))]
                    across = [r for r in rows if 4 <= r[1] <= 7 and r[2] > 8]
                    self.assertEqual(across, [], (code, wide, night))


class Elements(unittest.TestCase):
    def test_an_elements_torches_keep_clear_of_its_words(self):
        """By night an element's torches stand on its hems wherever they keep two units from every word, and on
        the wide sheets they find their place."""
        lit = 0
        for eid, d in ELEMENTS.items():
            kind = d["kind"]
            spec = E.describe(kind, d)
            for variant in ("wide", "narrow", "half") if kind in ("roster", "certificate") else E.variants(kind, d):
                p, pixels = sprites(lambda: SET.draw_element(kind, spec, True, variant), "sheet_torches")
                self.assertEqual(off_words(p, pixels)[:6], [], (eid, variant))
                lit += bool(pixels)
        self.assertGreater(lit, 4)

    def test_the_elements_are_stitched(self):
        """The histogram's columns are laid and couched work with gold along their tops, the cards are whip
        stitched round, the wires are couched in mustard across their blue grey thread, the dial is a wheel with
        spokes and a needle with an eye, and the releases are gonfanons hung from the cord."""
        files = draw_elements()
        vitals = files[("vitals", "instruments", "wide", "day")]
        self.assertTrue(re.search(r'id="lw(terr|must|oliv|woad)d"', vitals), "the laid columns")
        self.assertIn(GOLD[5], vitals, "the stitches along the columns' tops")
        flow = files[("how-it-runs", "schematic", "wide", "day")]
        self.assertIn('id="whd"', flow, "the cards' whip stitch")
        self.assertIn(RAMP["mustard"][4], flow, "the couching across the wires")
        spec = E.describe("instruments", ELEMENTS["vitals"])
        p = SET.instruments(spec, False)
        cx, cy, r = p.dial
        spokes = [(x, y) for (x, y), c in p.layers["base"].items() if c in (RAMP["umber"][3], RAMP["terracotta"][3])
                  and 5 <= ((x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2) ** 0.5 < r - 4 and y < cy]
        self.assertGreater(len(spokes), 30, "the wheel's spokes")
        eye = SET.ink(False)["fill"]
        self.assertTrue(any(c == eye and ((x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2) ** 0.5 < 8
                            for (x, y), c in p.layers["base"].items()), "the needle's eye, open")
        spec = E.describe("milestones", ELEMENTS["history"])
        p = SET.milestones(spec, False)
        heads = [(x, y) for (x, y), c in p.layers["base"].items() if c == RAMP["umber"][2] and 72 < y < 80]
        self.assertGreater(len(heads), 8, "the gonfanons' heads sewn under the cord")


class Badges(unittest.TestCase):
    def test_a_running_stitch_lies_inside_every_badges_edge_with_the_letters_clear_of_it(self):
        for style in BADGE_STYLES:
            drawn = [SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                       SET.badge_states()["green"])]
            drawn += [SET.plate_badge(style, "License", "MIT", "scale", mode) for mode in ("day", "night")]
            for p in drawn:
                stitches = {(x, y) for (x, y), c in p.layers["base"].items() if c == LINEN[6] and y == 1}
                self.assertTrue(stitches, style)
                self.assertTrue(all(y >= 2 for _, _, _, y, _ in p.uses["base"]), "the letters sit under the stitch")

    def test_a_counters_numerals_hold_4_5_on_their_patches(self):
        for night in (False, True):
            q = Pix(20, 20)
            SET.counter_cell(q, 2, 2, night)
            face = q.layers["base"][(7, 8)]
            self.assertGreaterEqual(contrast(SET.counter_ink(night, False), face), 4.5, night)
            self.assertGreaterEqual(contrast(SET.counter_ink(night, True), face), 2.0, night)


def mark_box(w: int, margin: int = 2) -> tuple:
    """The box the month's mark takes at the top centre of a header `w` units wide, `margin` units wider all round,
    as (x0, y0, x1, y1), ends excluded."""
    n = SET.hand.mark_size
    x0, y0 = w // 2 - n // 2, MARK_Y - n // 2
    return x0 - margin, y0 - margin, x0 + n + margin, y0 + n + margin


def skin_of(colour: str) -> int:
    """Which of the hand's skins a colour is a tone of, or -1."""
    return next((i for i in range(3) if colour in SET.hand.ramp(f"skin{i}")), -1)


def band_creatures(draw) -> tuple:
    """`draw()`'s drawing, and what the border band across its top sets on it as it draws: each creature, knot and
    span of the vine as (what, from, to), ends excluded, in column order."""
    found = []
    beast, knot, vine = A.beast, A.knot, A.vine

    def beast_(p, name, x, y, night, flip=False, L="base"):
        found.append((p, y, ("beast", x, x + len(A.ARTS[name][0]))))
        return beast(p, name, x, y, night, flip, L)

    def knot_(p, x, y, night, L="base"):
        found.append((p, y, ("knot", x, x + len(A.KNOT[0]))))
        return knot(p, x, y, night, L)

    def vine_(p, x0, x1, y, night, seed=0, L="base"):
        found.append((p, y, ("vine", x0, x1)))
        return vine(p, x0, x1, y, night, seed, L)
    with mock.patch.multiple(A, beast=beast_, knot=knot_, vine=vine_):
        p = draw()
    return p, sorted((c for q, y, c in found if q is p and y <= A.BAND[1]), key=lambda c: c[1:])


def lights(p: Pix) -> set:
    """Every colour a drawing's flames and their light are in: the pixels on its flickering layers, and the pools
    and glows laid round them."""
    on = {c.split(":")[0] for L in p.layers if L.startswith(("fl", "fb")) for c in p.layers[L].values()}
    laid = "".join(s for shapes in p.shapes.values() for s in shapes)
    return on | set(re.findall(r'<ellipse [^>]*fill="(#[0-9A-F]{6})"', laid))


class Hand(unittest.TestCase):
    """The Tapestry drawn in its collection's hand (see `collections.hand`): it keeps to the hand as October's
    design and kept all year; its words are in the hand's inks and its linen in the hand's bands; its torches burn
    on the hand's flame; its people are on the hand's skins in the embroidery's own proportions; the border band
    pauses for the month's mark and no scene comes near it; its heroes stand to the composition's measure; and the
    comet keeps the hand's slow sweep."""

    def test_it_keeps_to_its_hand_as_the_months_design_and_kept_all_year(self):
        self.assertIsInstance(SET, CollectionSet)
        self.assertEqual(SET.collection, "medieval")
        self.assertEqual(SET.on(ITS_DAY).month, 10)
        self.assertEqual(check(SET.on(ITS_DAY)), [])
        self.assertEqual(check(SET), [])

    def test_its_words_are_in_the_hands_inks(self):
        for night in (False, True):
            k = SET.ink(night)
            self.assertEqual((k["body"], k["muted"]), (SET.hand.body[night], SET.hand.muted[night]), night)

    def test_its_linen_lies_in_the_hands_bands_by_day_and_by_torchlight(self):
        """Behind every row of every header's words lies the day's unbleached linen, warm and pale within the
        hand's band, or the night's linen falling to umber within the night's."""
        for night in (False, True):
            lo, hi, most = SET.hand.night_ground if night else SET.hand.day_ground
            for draw in (SET.h1, SET.h2, SET.h3):
                p = draw(HEADER, night, False)
                for colour in {SET.bg_at(p, night, y) for y in range(p.h)}:
                    light, chroma, hue = lab(colour)
                    self.assertTrue(lo <= light <= hi and chroma <= most, (night, colour, light, chroma))
                    self.assertTrue(night or 40 <= hue <= 110, (colour, hue))

    def test_every_torch_burns_on_the_hands_flame(self):
        """The hall's torches on every header, wide and on a phone, the torch at the corner of a footer's notes and
        the torches of an element's sheet burn on the hand's flame: every flame and every pool of light they throw
        is a tone of it, and whatever else a footer or an element shows by night burns on it too."""
        self.assertEqual(FLAME, SET.hand.ramp("flame"))
        made = []
        canvas = SET.canvas

        def kept(*args, **kw):
            made.append(canvas(*args, **kw))
            return made[-1]

        def drawing(draw) -> Pix:
            made.clear()
            with mock.patch.object(SET, "canvas", kept):
                draw()
            return made[-1]
        lit = [drawing(lambda: SET.header(code, HEADER, DARK, wide, wide)) for code in ("H1", "H2", "H3")
               for wide in (True, False)]
        lit.append(drawing(lambda: SET.footer("F1", FOOTER, DARK, True, False)))
        sheets = [drawing(lambda: SET.footer("F2", FOOTER, DARK, True, False))]
        sheets += [drawing(lambda: SET.element(d["kind"], E.describe(d["kind"], d), DARK,
                                               E.variants(d["kind"], d)[0])) for d in ELEMENTS.values()]
        for p in lit:
            self.assertTrue(lights(p), "a torch burns on every header and by the footer's notes by night")
        self.assertTrue(any(lights(p) for p in sheets), "and on the elements' sheets")
        for p in lit + sheets:
            self.assertLessEqual(lights(p), set(FLAME))

    def test_every_face_and_hand_is_on_the_hands_skins(self):
        """The knights of the charge, the great horseman, Harold, the men of the wall and the contributors of a
        roster have their faces and hands stitched on the hand's skins, never on the linen, and among them all
        three skins are worn."""
        for night in (False, True):
            self.assertFalse({"face", "hand"} & set(A.knight_fixed(night)) | {"face"} & set(A.man_fixed(night)))
        worn = []
        wear = A.wear

        def watched(p, keys, wools, x, y, L="base"):
            worn.extend(skin_of(wools[role]) for role in ("face", "hand") if role in wools)
            return wear(p, keys, wools, x, y, L)
        with mock.patch.object(A, "wear", watched):
            for night in (False, True):
                for draw in (SET.h1, SET.h2, SET.h3):
                    draw(HEADER, night, False)
                for draw in (SET.h1_narrow, SET.h2_narrow, SET.h3_narrow):
                    draw(HEADER, night)
        self.assertNotIn(-1, worn)
        self.assertEqual(set(worn), {0, 1, 2})
        for night in (False, True):
            faces = []
            for i in range(3):
                q = Pix(20, 20)
                A.figure(q, 10, 10, i, night)
                faces.append({skin_of(c) for c in q.layers["base"].values()} - {-1})
            self.assertEqual(faces, [{0}, {1}, {2}], night)

    def test_the_great_horseman_is_the_knight_grown_twice_in_the_embroiderys_proportions(self):
        """The hero of a section's header is a knight of the charge grown to twice his size by Scale2x: twice as
        wide and twice as tall within two threads, about four times the wool in every part, and his couching still
        a single thread wide, so he keeps the embroidery's proportions; his frame is 72 wide."""
        def frame(cells):
            return {xy: r for xy, r in cells.items() if r not in ("wood", "point", "hand")}
        small = frame({**A.knight_cells("lance"), **A.legs_cells("stand", "lance")})
        great = frame({**A.great_knight_cells(), **A.great_legs_cells()})
        for axis in (0, 1):
            span = [max(c[axis] for c in cells) - min(c[axis] for c in cells) + 1 for cells in (small, great)]
            self.assertLessEqual(abs(span[1] - 2 * span[0]), 2, (axis, span))
        wool = [sum(r not in ("ink", "leather") for r in cells.values()) for cells in (small, great)]
        self.assertTrue(3.5 <= wool[1] / wool[0] <= 5, wool)
        faces = [sum(r == "face" for r in cells.values()) for cells in (small, great)]
        self.assertTrue(3.5 <= faces[1] / faces[0] <= 5, faces)
        self.assertEqual(A.GREAT_W, 2 * 36)
        self.assertLessEqual(max(x for x, _ in great) - min(x for x, _ in great) + 1, A.GREAT_W)

    def test_the_border_pauses_for_the_mark_its_creatures_whole_and_even_about_it(self):
        """Where a header carries the month's mark, the border band's creatures, knots and vine stop short of the
        mark's box and two units round it, every one whole, and stand again in the mirror of their places beyond it,
        so the border stands even about the mark; only the twin rules run on behind it, and so for a sign the page
        chose. Kept all year without the mark, the band runs on unbroken across the top centre. So in every header,
        wide and on a phone, for every shared content, by day and by night."""
        for name, (h, _) in contents(KEY).items():
            for code in ("h1", "h2", "h3"):
                for wide in (True, False):
                    for night in (False, True):
                        what = (name, code, wide, night)

                        def draw(held):
                            return getattr(held, code)(h, night, False) if wide else \
                                getattr(held, f"{code}_narrow")(h, night)
                        p, marked = band_creatures(lambda: draw(SET.on(ITS_DAY)))
                        a, _, b, _ = mark_box(p.w)
                        self.assertEqual([c for c in marked if c[1] < b and c[2] > a], [], what)
                        left = {c for c in marked if c[2] <= a}
                        right = {c for c in marked if c[1] >= b}
                        self.assertTrue(any(c[0] != "vine" for c in left), what)
                        self.assertEqual({(kind, a + b - x1, a + b - x0) for kind, x0, x1 in left}, right, what)
                        p, kept = band_creatures(lambda: draw(SET))
                        self.assertTrue(any(x0 <= p.w // 2 < x1 for _, x0, x1 in kept), what)
                        self.assertTrue(all(c[1] - d[2] <= 1 for d, c in zip(kept, kept[1:])), what)
                        # Kept all year with a sign the page chose, the band pauses for its mark as well.
                        p, signed = band_creatures(lambda: draw(SET.signed("leo")))
                        self.assertEqual(signed, marked, what)

    def test_no_scene_comes_near_the_marks_box_with_the_mark_or_without_it(self):
        """The box the month's mark takes, and two units round it, holds nothing of a scene in any header, wide or
        on a phone, for any shared content, by day or by night, as October's design and kept all year."""
        for month in (True, False):
            for name, (h, _) in contents(KEY).items():
                for code in ("h1", "h2", "h3"):
                    for wide in (True, False):
                        for night in (False, True):
                            def draw():
                                held = SET.on(ITS_DAY) if month else SET
                                return getattr(held, code)(h, night, True) if wide else \
                                    getattr(held, f"{code}_narrow")(h, night)
                            p, pixels = sprites(draw, *(("scene",) if wide else ("scene_narrow", "scene_under")))
                            x0, y0, x1, y1 = mark_box(p.w)
                            inside = [xy for xy in pixels if x0 <= xy[0] < x1 and y0 <= xy[1] < y1]
                            self.assertEqual(inside, [], (month, name, code, wide, night))

    def test_its_heroes_stand_to_the_compositions_measure(self):
        """A section's header stands the great horseman on its right, rising at least four fifths of the band from
        the border band to his ground; a sheet's charge and its shield wall under the tall tree each rise at least
        seven tenths of it, wherever the words leave their side free; a strip's hero, Harold grown twice under the
        tall tree, rises its full height from the lower border to the upper; and a phone's H2 and H3 stand the great
        horseman and Harold under their words, the hunt the full rows it asks for less the lower border it stands on
        and never under 44. So for the kit's own lines, the samples and the least a page can say; the most a page
        can say leaves its strip a column at the right, where Harold under the tree rises at least 60 rows."""
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                what = (name, night)
                p, pixels = sprites(lambda: SET.h3(h, night, True), "scene")
                top, foot = min(y for _, y in pixels), max(y for _, y in pixels)
                self.assertIn(("shape", ("harold", night)), p.syms, what)
                if name == "most":
                    self.assertGreaterEqual(foot - top + 1, 60, what)
                else:
                    self.assertGreaterEqual(foot - top + 1, 0.94 * (foot - A.BAND[1]), what)
                with mock.patch.object(A, "lower_band", lambda *a, **k: None):
                    p, pixels = sprites(lambda: SET.h3_narrow(h, night), "scene_under")
                ys = [y for _, y in pixels]
                self.assertGreaterEqual(max(ys) - min(ys) + 1, max(44, PHONE_UNDER["H3"] - 7), what)
                self.assertIn(("shape", ("harold", night)), p.syms, what)
                self.assertGreater(len(p.layers["tr"]), 300, (what, "the tall tree"))
                if name == "most":
                    continue
                p, pixels = sprites(lambda: SET.h2(h, night, True), "scene")
                top, foot = min(y for _, y in pixels), max(y for _, y in pixels)
                self.assertGreaterEqual(foot - top + 1, 0.8 * (foot - A.BAND[1]), what)
                self.assertIn(("shape", ("great", night)), p.syms, what)
                p, pixels = sprites(lambda: SET.h1(h, night, True), "scene")
                for side in (range(0, 200), range(200, 415)):
                    ys = [y for x, y in pixels if x in side]
                    top, foot = min(ys), max(ys)
                    self.assertGreaterEqual(foot - top + 1, 0.7 * (foot - A.BAND[1]), (what, side))
                self.assertTrue(p.uses["kr"] and p.uses["kf"], (what, "both knights of the charge"))
                with mock.patch.object(A, "lower_band", lambda *a, **k: None):
                    p, pixels = sprites(lambda: SET.h2_narrow(h, night), "scene_under")
                ys = [y for _, y in pixels]
                self.assertGreaterEqual(max(ys) - min(ys) + 1, 40, what)
                self.assertIn(("shape", ("great", night)), p.syms, what)

    def test_harold_is_grown_twice_as_the_great_horseman_is(self):
        """A strip's hero is Harold on foot with his hawk on his fist, his rows grown to twice their size by Scale2x
        as the great horseman's are: twice as wide and twice as tall within two threads, about four times the wool,
        couched round a thread wide that lies against him everywhere, his eye and his hawk's set as an eye is, a dark
        stitch with a white one behind it, his garters wound round his hose, and his shoes on the row of his frame he
        stands on."""
        small = A.compose([(A.HAROLD, A.HAROLD_ROLES, (0, 0), True)])
        great = A.great_harold_cells()
        for axis in (0, 1):
            span = [max(c[axis] for c in cells) - min(c[axis] for c in cells) + 1 for cells in (small, great)]
            self.assertLessEqual(abs(span[1] - 2 * span[0]), 2, (axis, span))
        wool = [sum(r not in ("ink",) for r in cells.values()) for cells in (small, great)]
        self.assertTrue(3.5 <= wool[1] / wool[0] <= 5, wool)
        inked = {xy for xy, r in great.items() if r == "ink"}
        self.assertTrue(all(any((x + dx, y + dy) in great and great[(x + dx, y + dy)] != "ink"
                                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) for (x, y) in inked), "couched round")
        for (x, y), r in great.items():
            if r == "eye":
                self.assertEqual(great[(x + 1, y)], "white", (x, y))
        self.assertEqual(sum(r == "eye" for r in great.values()), 2, "his eye and his hawk's")
        self.assertIn("garter", great.values())
        self.assertEqual(max(y for (_, y), r in great.items() if r == "shoe"), A.HAROLD_FOOT)
        self.assertEqual(set(A.great_harold_cells(True)), set(great), "drawn plain, the same figure")

    def test_the_tall_tree_grows_by_twisting_its_trunk_on(self):
        """The tall tree grows to the rows a scene gives it by twisting its trunk on for more rows or fewer, from 38
        rows to `TALLEST`: its crown, its boughs and its roots keep their shape, and its two strands cross every four
        rows as they do at its own height."""
        self.assertEqual(A.tall_rows(), A.TALL)
        twist = A.TALL[A.TRUNK[0]:A.TRUNK[0] + 4]
        for height in range(38, A.TALLEST + 1):
            rows = A.tall_rows(height)
            self.assertEqual(len(rows), height)
            self.assertEqual(rows[:A.TRUNK[0]], A.TALL[:A.TRUNK[0]], height)
            self.assertEqual(rows[height - (len(A.TALL) - A.TRUNK[1]):], A.TALL[A.TRUNK[1]:], height)
            trunk = rows[A.TRUNK[0]:height - (len(A.TALL) - A.TRUNK[1])]
            self.assertEqual(trunk[-1], A.TALL[A.TRUNK[1] - 1], height)
            self.assertTrue(all(twist.index(b) == (twist.index(a) + 1) % 4 for a, b in zip(trunk, trunk[1:])),
                            height)

    def test_the_comet_keeps_the_hands_slow_sweep(self):
        """The comet crosses the band, is gone a while and crosses again once in a slow sweep of 24 to 48 seconds,
        as the hand's ambient sweeps do; the horses' gallop and the pennons' wave are the motion of what they are,
        not idles, and keep their own quick beats."""
        for h in (HEADER, contents(KEY)["least"][0], contents(KEY)["most"][0]):
            moving = SET.header("H1", h, DAY, True, True)
            drifts = re.findall(r'type="translate" values="([^"]*)" dur="([\d.]+)s"', moving)
            sweep = float(drifts[-1][1])
            self.assertTrue(24 <= sweep <= 48, sweep)


class SharedBanners(unittest.TestCase):
    """The checks every registered set passes, over this set."""

    def test_every_file_is_the_sets_well_formed_linted_and_deterministic(self):
        drawn = {(n, c, fn): svg for n, c, fn, svg in every_banner()}
        for (name, code, fn), svg in drawn.items():
            minidom.parseString(svg)
            self.assertIn(f"<!--{KIT} v{KIT_VERSION} {KEY} ", svg, (name, fn))
            self.assertNotIn("<text", svg)
            for ch in DASHES:
                self.assertNotIn(ch, svg)
            cap = BUDGET["link"] if fn.startswith("link-") else BUDGET[DESIGNS[code].kind]
            self.assertEqual(lint(svg, budget=cap, tokens=SET.tokens), [], (name, code, fn))
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

    def test_text_colours_hold_4_5_on_the_paper_and_every_row_of_the_night(self):
        for night in (False, True):
            k = SET.ink(night)
            p = Pix(415, 200)
            grounds = {SET.bg_at(p, night, y) for y in range(p.h)}
            for role in ("title", "body", "muted", "accent"):
                for ground in grounds:
                    self.assertGreaterEqual(contrast(k[role], ground), 4.5, (night, role, ground))
            self.assertGreaterEqual(contrast(k["tag_ink"], k["tag"]), 4.5, (night, "tag"))

    def test_ordinary_content_fits_at_full_weight_and_the_most_fits_lighter(self):
        """Ordinary content is served at full weight, a wide header moving, with at least 1.5 KB of headroom under
        the budget, as the month's design with its mark and kept all year without it; a lighter drawing keeps its
        motion while it fits, and motion is the last thing to go."""
        for name in ("kit", "repository", "profile", "least"):
            h, f = contents(KEY)[name]
            for code in ("H1", "H2", "H3"):
                for theme in (DAY, DARK):
                    for wide in (True, False):
                        for month in (False, True):
                            with mock.patch.object(SET, "_fitted", lambda draw, budget, *then: draw()):
                                svg = (SET.on(ITS_DAY) if month else SET).header(code, h, theme, wide, wide)
                            what = (name, code, theme["name"], wide, month)
                            self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"] - 1500, what)
                            self.assertEqual((SET.on(ITS_DAY) if month else SET).header(code, h, theme, wide, wide),
                                             svg, what)
                            self.assertEqual("<animate" in svg, wide, what)
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

    def test_a_character_the_sets_letters_lack_hands_a_badge_back(self):
        self.assertFalse(SET.can_letter("flat", "中文"))


class SharedElements(unittest.TestCase):
    def test_every_element_is_the_sets_linted_deterministic_and_the_kits_size(self):
        files = draw_elements()
        again = draw_elements()
        for (eid, kind, variant, theme), svg in files.items():
            minidom.parseString(svg)
            self.assertEqual(svg, again[(eid, kind, variant, theme)], (eid, variant, theme))
            self.assertIn(f"<!--{KIT} v{KIT_VERSION} {KEY} elements {kind} ", svg, (eid, variant, theme))
            self.assertEqual(lint(svg, budget=BUDGET[E.KINDS[kind][2]], tokens=SET.tokens), [],
                             (eid, variant, theme))
            w = int(re.search(r'width="(\d+)"', svg).group(1))
            half = kind == "placard" or variant == "half" or (variant == "narrow" and kind in ("roster", "certificate"))
            self.assertEqual(w, 404 if half else 360 if variant == "narrow" else 830, (eid, variant, theme))

    def test_the_half_page_pair_is_drawn_level(self):
        pair = {eid: (d["kind"], E.describe(d["kind"], d)) for eid, d in ELEMENTS.items()
                if d["kind"] in ("roster", "certificate")}
        level = max(SET.element_height(kind, spec) for kind, spec in pair.values())
        heights = {re.search(r'height="(\d+)"', SET.element(kind, spec, DAY, "half", level)).group(1)
                   for kind, spec in pair.values()}
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

    def test_the_roster_draws_figures_never_initials(self):
        spec = E.describe("roster", ELEMENTS["contributors"])
        p = SET.roster(spec, False)
        letters = {sid for (stroke, sid, x, y, s) in p.uses["base"] if 36 <= y < 54 and 8 <= x < 27}
        glyphs = {sid for key, sid in p.syms.items() if isinstance(key, tuple) and key[0] == "glyph"}
        self.assertFalse(letters & glyphs, "no letters where the first avatar stands")
        figure = {c for (x, y), c in p.layers["base"].items() if 36 <= y < 54 and 8 <= x < 27}
        self.assertIn(RAMP["terracotta"][4], figure, "the first contributor's tunic")


class SharedBadges(unittest.TestCase):
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

    def test_the_swatches_cover_every_family_a_written_colour_comes_in(self):
        swatches = SET.badge_swatches()
        self.assertGreaterEqual(len(swatches), 10)
        for name, (block, _, _) in swatches.items():
            self.assertIn(block, self.badge("flat", message_hex=block)["static/b.svg"], name)
        for family in ("red", "orange", "yellow", "green", "blue", "purple", "white", "black", "slate", "brown"):
            self.assertTrue(self.badge("flat", message_hex=PALETTE[family]), family)

    def test_what_the_sets_letters_cannot_draw_is_left_to_the_kit(self):
        self.assertIsNone(self.badge("flat", message="中文"))


if __name__ == "__main__":
    unittest.main()
