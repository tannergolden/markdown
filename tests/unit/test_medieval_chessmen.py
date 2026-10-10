# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Chessmen set's own rules, which the checks every set shares cannot know: what the night alone shows (the
dark of the hall, the hearth's warmth, the fire's glow and its sparks, the firelight on the pieces' edges, the
orange edge the hearth lights on every letter and the candle by the toppled king) stays out of the day's files;
every small word keeps 4.5:1 with the light laid round it; a title is cut deep, by day its cut inked solid dark,
its hollow, its cut walls and its bevel placed from the letters set once; the band along a header's top carves the
board's long diagonal, a1 to h8, in sunken cartouches with grooves between them, never a row of dots, and a glint
runs along it only in a wide moving header; every header is the hall, its planks, its crossbeam and its posts, the
woven hanging behind every one of its words; an H1 has the hearth with its fire, cauldron, horn hung by its strap,
dragon's head, shield and purse at its left and the game on its table at its right, the Lewis pieces standing on it
at the size each reads at a glance, every head behind another showing whole, the whole board where the room runs
wide and its near corner running off under the frame where it runs narrow, the knight leaping in a moving header;
by day the shaft of light from the smoke hole falls on the game with its motes, and by night the hearth and the lamp
by the board are the hall's two lights, a pool round each, the pieces' shadows thrown long across the board; an H2
is its showpieces, the king on his throne and the berserker before him, and the whole court across the floor where
the words leave it, and an H3 the queen on her throne the same way, each under the crossbeam, their eyes wide and
staring; every phone header stands a scene of the set's, the showpieces under its words; every scene, the band, the
marks beside a title and the rank inlaid along a rule keep two units from every word, on a phone and across a wide
header; the most a page can say keeps its whole scene and its motion within the budget, a drawing made lighter
keeping every piece where it stood, and ordinary content is drawn at full weight with room to spare; a footer lies
on the board's edge, a rank of the board holding the pieces taken standing and the toppled king lying across it
where a cell leaves room, else the king at the corner of its notes, at the board's own size where a cell has room
for him, clear of every word; a link is a tableman, a small file; a badge carries a rank of the board along its top;
a counter's numerals hold 4.5:1 on their tablemen and are carved over them; the roster's avatars are chessmen
stained in their own colours, never initials; a card is a tablet of ivory with its icon carved in a tableman; the
histogram stacks tablemen; the dial is a quadrant of ivory with a bishop's crozier for its hand; the releases are
pawns on a rank of the board with a queen being crowned at today; the seal is a king's crown of red bone; and a
placard is the stone kist, every word on it at 4.5:1. The set is the medieval collection's February, drawn in the
collection's hand: the hand's check finds nothing, as the month's design or kept all year; its words are in the
hand's two inks and its ivory and wool in the hand's bands; every flame burns on the hand's flame; every motion keeps
the hand's timing; the month's mark has its box clear of the scene and of the band's names; and its phone heroes
stand as tall as the hand's composition asks. The set is a theme, not a holiday on the calendar, so the checks every
registered set shares run here over the set directly, with the same contents and the same entry points."""
from __future__ import annotations

import contextlib
import datetime as dt
import math
import re
import unittest
import xml.dom.minidom as minidom
from unittest import mock

from tests import support
from tests.unit.test_holiday_sets import DASHES, ELEMENTS, HEIGHTS, STAMP, contents

from domain import KIT, KIT_VERSION
from domain.badges import data as BD
from domain.banners.content import Header
from domain.banners.designs import DESIGNS, variants
from domain.canvas import BUDGET, DARK, DAY, colours, lint
from domain.elements import draw as E
from domain.holidays.designs import NARROW, WIDE
from domain.holidays.designs.badges import PLATE, STATES, STYLES as BADGE_STYLES, inside
from domain.holidays.designs.banners import MARK_Y
from domain.collections.hand import MEDIEVAL, CollectionSet, check, lab
from domain.collections.medieval_chessmen import SET
from domain.collections.medieval_chessmen import art as A
from domain.collections.medieval_chessmen.palette import C, NIGHT_SKY, RAMP, X
from domain.holidays.pixel import BLINKS, Pix, contrast
from domain.palette import PALETTE

support.install()
KEY = SET.key
HEADER = Header(tone="standard", holiday=KEY)
BARE = HEADER.with_(title="x", tagline="", description="", motto="", notes=())
IV, RD, FIRE, GILT = RAMP["ivory"], RAMP["stain"], RAMP["fire"], RAMP["gilt"]


def draw_banners() -> list:
    """Every banner file the set draws for the shared contents: (content, code, file name, svg), as the kit would
    ask for them, variant by variant."""
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


# A block laid in a pattern (the board's edge, the band along a header's top): what `sprites` reads to know which
# cells it covers.
RECT = re.compile(r'<rect x="(-?\d+)" y="(-?\d+)" width="(\d+)" height="(\d+)"')


def sprites(draw, *hooks) -> tuple:
    """`draw()`'s drawing, and every pixel of the sprites the set's `hooks` (names of its drawing hooks) put on it,
    gathered as they draw: their pixels on every layer, the cells of the symbols they place, the blocks they lay in
    a pattern and the cells the set keeps in the drawing's `filled` for the shapes it lays."""
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
            laid = {L: len(s) for L, s in p.shapes.items()}
            filled = set(getattr(p, "filled", ()))
            out = hook(*args, **kw)
            for L, c in p.layers.items():
                pixels.update(set(c) - before.get(L, set()))
            for L, uses in p.uses.items():
                for (_, sid, x, y, s) in uses[placed.get(L, 0):]:
                    pixels.update((x + dx * s, y + dy * s) for dx, dy in cells.get(sid, ()))
            for L, shapes in p.shapes.items():
                for x, y, w, h in RECT.findall("".join(shapes[laid.get(L, 0):])):
                    pixels.update((xx, yy) for xx in range(int(x), int(x) + int(w))
                                  for yy in range(int(y), int(y) + int(h)))
            pixels.update(set(getattr(p, "filled", ())) - filled)
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


def served(draw, names=()) -> tuple:
    """`draw()`'s file, the drawing it was made from (the last one finished, where the kit drew it again lighter or
    still to fit its budget), and spies on the set's art functions `names`, holding their calls."""
    finals, real = [], Pix.svg

    def finished(p, *args, **kw):
        finals.append(p)
        return real(p, *args, **kw)
    with contextlib.ExitStack() as stack:
        stack.enter_context(mock.patch.object(Pix, "svg", finished))
        spies = {name: stack.enter_context(mock.patch.object(A, name, wraps=getattr(A, name))) for name in names}
        out = draw()
    return out, finals[-1], spies


def drawn_on(p, spy) -> list:
    """The calls a spied art function made on the sheet `p` itself, not on the scratch drawings a scene tries its
    layouts on."""
    return [c for c in spy.call_args_list if c.args and c.args[0] is p]


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


# ---- the light laid on the ivory, for the words' contrast under it
TAG = re.compile(r'<(/?)(g|ellipse|polygon|rect|use)\b([^>]*?)(/?)>')
ATTR = re.compile(r'([a-z-]+)="([^"]*)"')


def overlays(p: Pix) -> list:
    """Every see-through shape laid on `p`, (z, kind, attributes), in the order they are drawn: the hearth's warmth,
    the fire's glow and whatever else glows, from its layers and its own markup. Solid shapes and patterns are left
    out."""
    found = []
    for markup, z in [("".join(s), p.meta[name][0]) for name, s in p.shapes.items()] + \
            [(m, z) for (z, _, m, _) in p.raws]:
        for close, kind, attrs, _ in TAG.findall(markup):
            a = dict(ATTR.findall(attrs))
            if not close and "fill-opacity" in a and a.get("fill", "").startswith("#"):
                found.append((z, kind, a))
    return sorted(found, key=lambda t: t[0])


def _inside(kind, a, x, y) -> bool:
    if kind == "ellipse":
        rx, ry = float(a["rx"]), float(a["ry"])
        return rx > 0 and ry > 0 and ((x - float(a["cx"])) / rx) ** 2 + ((y - float(a["cy"])) / ry) ** 2 <= 1
    if kind == "rect":
        return (float(a.get("x", 0)) <= x < float(a.get("x", 0)) + float(a["width"])
                and float(a.get("y", 0)) <= y < float(a.get("y", 0)) + float(a["height"]))
    return False


def _blend(c, top, a):
    t = [int(top[i:i + 2], 16) for i in (1, 3, 5)]
    return tuple(round(c[i] * (1 - a) + t[i] * a) for i in range(3))


def lettered(draw) -> tuple:
    """`draw()`'s drawing, and the box and colour of every line it set in small letters on it (titles, carved in
    their own paint, are left to the checks on the inks; a header laid out twice keeps the words of the drawing it
    returns)."""
    inks: dict = {}
    text = Pix.text

    def kept(self, x, y, s, c, font="57", scale=1, *args, **kw):
        w = text(self, x, y, s, c, font, scale, *args, **kw)
        if scale == 1 and s.strip():
            inks.setdefault(id(self), []).append((self.words[-1], c))
        return w
    with mock.patch.object(Pix, "text", kept):
        p = draw()
    return p, inks.get(id(p), [])


def worst_words(p: Pix, night: bool, inks: list) -> list:
    """For each small word set on `p` (`inks`, as `lettered` keeps them), the lowest contrast its colour holds over
    its box with every see-through light laid on the ivory under it, and over the word where a light lies over it."""
    shapes = overlays(p)
    base = p.layers["base"]
    worst = []
    for (x0, y0, x1, y1), ink in inks:
        low = 99.0
        for y in range(y0 + 1, y1 - 1):
            for x in range(x0 + 1, x1 - 1, 2):
                under = base.get((x, y)) or SET.bg_at(p, night, y)
                g = tuple(int(under[i:i + 2], 16) for i in (1, 3, 5))
                fg = tuple(int(ink[i:i + 2], 16) for i in (1, 3, 5))
                for (z, kind, a) in shapes:
                    if _inside(kind, a, x + 0.5, y + 0.5):
                        g = _blend(g, a["fill"], float(a["fill-opacity"]))
                        if z > 0:
                            fg = _blend(fg, a["fill"], float(a["fill-opacity"]))
                low = min(low, contrast("#%02X%02X%02X" % fg, "#%02X%02X%02X" % g))
        worst.append(((x0, y0, x1, y1), ink, round(low, 2)))
    return worst


HEADERS = (("H1", lambda h, n: SET.h1(h, n, True)), ("H2", lambda h, n: SET.h2(h, n, True)),
           ("H3", lambda h, n: SET.h3(h, n, True)), ("H1n", lambda h, n: SET.h1_narrow(h, n)),
           ("H2n", lambda h, n: SET.h2_narrow(h, n)), ("H3n", lambda h, n: SET.h3_narrow(h, n)))
FOOTERS = (("F1", SET.f1), ("F2", SET.f2), ("F1n", SET.f1_narrow), ("F2n", SET.f2_narrow))


class Night(unittest.TestCase):
    def test_what_the_night_alone_shows_stays_out_of_the_day(self):
        """The dark of the hall, the orange edge the hearth lights on every letter and the hearth's warmth are the
        night's; by day an H2 and an H3, which have no hearth of their own, carry no firelight at all, and by night
        they take the hearth's warmth and its light on the pieces' edges."""
        for code in ("H1", "H2", "H3"):
            day = SET.header(code, HEADER, DAY, True, True)
            night = SET.header(code, HEADER, DARK, True, True)
            for band in NIGHT_SKY:
                self.assertNotIn(band, day, (code, "the hall's dark"))
            self.assertTrue(any(band in night for band in NIGHT_SKY), code)
            self.assertNotIn(X["ember"], day, (code, "the firelit edge of the letters"))
            self.assertIn(X["ember"], night, code)
            if code != "H1":
                self.assertFalse(set(FIRE) & set(re.findall(r"#[0-9A-F]{6}", day)), (code, "no fire by day"))
                self.assertIn(FIRE[2], night, (code, "the hearth's warmth"))

    def test_by_night_the_hearth_and_the_lamp_by_the_board_are_the_halls_two_lights(self):
        """By night the hall has two lights, the hearth at its left and the soapstone lamp on the table by the
        board, each casting its light on what stands near it and its glow in the air, a pool round each with the dark
        of the hall between them; sparks fly up over the hearth's flames in every frame. The hearth's warmth on the
        wall reaches no further than half the sheet, so the dark between the two shows. By day the hearth burns
        banked low, casting none, nothing flies from it, and the shaft of light from the smoke hole falls on the game
        instead, its motes drifting down it in a moving header."""
        for night in (False, True):
            with mock.patch.object(A, "lamp", wraps=A.lamp) as lamp, \
                    mock.patch.object(A, "fire", wraps=A.fire) as fire, \
                    mock.patch.object(A, "glow", wraps=A.glow) as glow, \
                    mock.patch.object(A, "daylight", wraps=A.daylight) as shaft:
                p = SET.h1(HEADER, night, True)
            self.assertEqual(len(drawn_on(p, lamp)), 2 if night else 0, night)
            (call,) = drawn_on(p, fire)
            top = call.args[2] - len((A.FIRE_NIGHT if night else A.FIRE_DAY)[0])
            for n in ("fire0", "fire1", "fire2"):
                flying = [y for (_, y) in p.layers[n] if y < top - 1]
                self.assertEqual(bool(flying), night, (night, n, "sparks over the flames"))
            glow_ = [n for n in p.meta if n.startswith("fb") and p.shapes[n]]
            self.assertEqual(bool(glow_), night, (night, "the glow round the fire"))
            self.assertEqual(len(drawn_on(p, shaft)), 0 if night else 1, (night, "the shaft of daylight"))
            if night:
                pools = sorted(c.args[1] for c in drawn_on(p, glow) if c.args[3] > 40)
                self.assertTrue(pools[0] < 100 and pools[-1] > 300, (pools, "a pool at either end"))
                warmth = [c for c in drawn_on(p, glow) if c.args[1] < 0]
                self.assertTrue(warmth and all(c.args[3] <= p.w * 0.55 for c in warmth), "the hearth's reach")
        moving = SET.h1(HEADER, False, True)
        self.assertTrue([m for (_, _, m, _) in moving.raws if "animateTransform" in m and X["glint"] in m], "motes")

    def test_the_pieces_shadows_fall_long_by_night_and_their_edges_take_the_hearths_light(self):
        """A piece's shadow by day is short; by night it is thrown long across the squares away from the hearth.
        By night the edge of every piece toward the hearth glows and the ivory just inside it is bright."""
        b = A.Board(100, 80, 16, 50)
        day, night = A.shadow_cells(b, 2, 2, False), A.shadow_cells(b, 2, 2, True)
        self.assertGreater(max(x for x, _ in night), max(x for x, _ in day) + 16, "a square and more longer")
        lit = A.piece_cells(A.KING, "ivory", True)
        left = {}
        for (i, j), c in lit.items():
            left.setdefault(j, (i, c))
            left[j] = min(left[j], (i, c))
        self.assertTrue(all(c == FIRE[2] for _, c in left.values()), "the cut toward the hearth glows")
        self.assertFalse(set(FIRE) & set(A.piece_cells(A.KING, "ivory", False).values()), "no glow by day")

    def test_every_small_word_holds_4_5_with_the_hearths_light_on_the_ivory(self):
        """The hearth's warmth and the fire's glow fall on the ivory round the words as well as on the hall: every
        line set in small letters keeps 4.5:1 over all of it, on every header, phone and footer the shared contents
        draw by night."""
        for name, (h, f) in contents(KEY).items():
            for code, draw in HEADERS:
                p, inks = lettered(lambda: draw(h, True))
                low = [w for w in worst_words(p, True, inks) if w[2] < 4.5]
                self.assertEqual(low[:3], [], (name, code))
            for code, draw in FOOTERS:
                p, inks = lettered(lambda: draw(f, True))
                low = [w for w in worst_words(p, True, inks) if w[2] < 4.5]
                self.assertEqual(low[:3], [], (name, code))


class Titles(unittest.TestCase):
    def test_a_title_is_cut_in_the_ivory_solid_by_day(self):
        """A title's letters are set once as a group, and every treatment places that group again. By day each letter
        is a cut filled with a dark stain, heavy and solid, the stain a dark honey brown deepening to old oak at its
        foot, every shade of it at 7:1 or more on the ivory, in a thin yellowed hollow, the polished lip catching the
        light along its lower right edge. By night the letters stand raised in polished cream over the hall's dark
        hollow, and the hearth lights the left edge of every stroke."""
        for night, rings in ((False, (RAMP["honey"][5], X["glint"])),
                             (True, (RAMP["oak"][2], RAMP["oak"][1], RAMP["hall"][0]))):
            p = SET.h1(HEADER, night, True)
            markup = "".join(m for (_, _, m, _) in p.raws)
            group = re.search(r'<use href="#(ct\d+)"', markup).group(1)
            self.assertTrue(any(d.startswith(f'<g id="{group}" transform="translate(') for d in p.defs), night)
            for ring in rings:
                self.assertIn(f'<g stroke="{ring}"><use href="#{group}"', markup, (night, ring))
            self.assertIn('stroke="url(#', markup, (night, "the face's own paint"))
            self.assertEqual(f'<use href="#{group}" x="-1" stroke="{X["ember"]}"/>' in markup, night, "firelit")
        stain = {A.FACE.fill(r, 0, scale, False) for scale in (1, 2, 3) for r in range(7 * scale)}
        self.assertEqual(stain, {RAMP["honey"][1], RAMP["honey"][0], RAMP["oak"][1]})
        for c in stain:
            self.assertGreaterEqual(contrast(c, SET.bg_at(Pix(10, 10), False, 0)), 7, c)
        lit = {A.FACE.fill(r, 0, 2, True) for r in range(14)}
        self.assertLessEqual(lit, set(IV), "the night's letters of polished ivory")

    def test_the_band_carves_the_boards_diagonal_never_a_row_of_dots(self):
        """The band along a header's top names the board's long diagonal, a1 to h8, raised in sunken cartouches,
        with two grooves cut across the band between each two; its glint runs along it only in a wide moving
        header."""
        p = SET.h1(HEADER, False, True)
        base = p.layers["base"]
        lit = [(x, y, sid) for (stroke, sid, x, y, _) in p.uses["base"] if stroke == IV[6] and y == 3]
        self.assertEqual(len(lit), 16, "eight squares, a letter and a figure each")
        hollows = {c for (x, y), c in base.items() if y == 5 and c in (RAMP["honey"][3], RAMP["honey"][2])}
        self.assertTrue(hollows, "the cartouches' yellowed hollows")
        grooves = [x for x in range(p.w) if all(base.get((x, y)) == IV[1] for y in range(3, 9))
                   and all(base.get((x + 1, y)) == IV[6] for y in range(3, 9))]
        self.assertEqual(len(grooves), 14, "two grooves between each two of the eight")
        dots = [x for x in range(8, p.w - 8) if base.get((x, 6)) and not base.get((x, 4)) and not base.get((x, 8))
                and not base.get((x - 1, 6)) and not base.get((x + 1, 6))]
        self.assertEqual(dots, [], "nothing set alone in the band")
        self.assertIn('<clipPath id="bg', SET.header("H1", HEADER, DAY, True, True), "the glint")
        for still in (SET.header("H1", HEADER, DAY, True, False), SET.header("H1", HEADER, DAY, False, False)):
            self.assertNotIn('<clipPath id="bg', still)


    def test_a_rank_of_the_board_is_inlaid_along_a_rule_never_a_row_of_dots(self):
        """Along a rule a rank of the board lies inlaid in strips: squares of ivory and of red bone by turns, whole
        squares from end to end, set in a dark cut along the top and the ends of each strip; it stops two units
        short of a word that comes down near the rule."""
        for night in (False, True):
            p = Pix(120, 30)
            p.text(60, 17, "WORDS", SET.ink(night)["body"])
            SET.rule_decor(p, 5, 115, 26, 0, night)
            cut = sorted(x for (x, y), c in p.layers["base"].items() if y == 22 and c == IV[1])
            strips = []
            for x in cut:
                if strips and x == strips[-1][-1] + 1:
                    strips[-1].append(x)
                else:
                    strips.append([x])
            self.assertEqual(len(strips), 2, (night, "a strip either side of the word"))
            for strip in strips:
                a, b = strip[0], strip[-1]
                self.assertEqual({p.get(a, 24), p.get(b, 24)}, {IV[1]}, (night, "cut at its ends"))
                squares = [p.get(x, 23) for x in range(a + 1, b)]
                self.assertEqual(len(squares) % 4, 0, (night, "whole squares"))
                self.assertTrue(set(squares) & set(RD) and set(squares) & set(IV), (night, "ivory and red"))
            self.assertEqual(off_words(p, {xy for xy in p.layers["base"] if xy[1] > 20}), [], night)


class Scenes(unittest.TestCase):
    def test_an_h1_is_the_hall_the_hearth_at_its_left_and_the_game_at_its_right(self):
        """An H1 is the hall: its wall of planks under the crossbeam, its posts at either end and the woven hanging
        behind its words; at its left the hearth with its fire, the cauldron over it, the horn hung in its sling on
        the hall's post, the post carved with a dragon's head, a round shield on the wall and the gaming purse
        spilling its tablemen, with a bench on the floor where the words leave it room; at its right the game on its
        table with the soapstone lamp at the board's corner, the whole board where the room runs wide and its near
        corner running off under the frame where the words come nearer."""
        names = ("hearth", "staged_game", "gaming_table", "fire", "cauldron", "horn", "post", "purse",
                 "dragon_head", "round_shield", "bench", "oil_lamp", "crossbeam", "hanging", "wall_posts",
                 "hall_wall")
        for h, layout in ((BARE, "wide"), (HEADER, "corner")):
            for theme in (DAY, DARK):
                _, p, spies = served(lambda: SET.header("H1", h, theme, True, True), names)
                for name in names:
                    self.assertTrue(drawn_on(p, spies[name]), (name, layout, theme["name"]))
                (game,) = drawn_on(p, spies["staged_game"])
                self.assertEqual(game.args[5], layout)
        _, p, spies = served(lambda: SET.header("H1", BARE, DAY, True, True), ("purse",))
        self.assertTrue(drawn_on(p, spies["purse"])[0].kwargs.get("spill"), "its tablemen spilled")

    def test_the_game_is_staged_at_the_size_each_lewis_piece_reads(self):
        """However it is staged, the game shows the Lewis pieces at the size where each reads at a glance, 24 to 30
        rows tall but the slab pawn: the king with his sword across his knees and the queen with her hand to her
        cheek besides the knight on his pony, and where the whole board shows, the berserker biting his shield, the
        bishop with his crozier and a pawn too, ivory and red. A piece standing behind another shows its head and
        its crown whole over it, the knight at either end of his leap too. The whole board and its table stand inside
        the frame on the floor; where only its near corner shows, board and table run off under the frame."""
        for layout, stage in A.STAGES.items():
            kinds = {kind for kind, *_ in stage["pieces"]}
            self.assertLessEqual({"king_m", "queen_m"}, kinds, layout)
            self.assertEqual({side for _, side, *_ in stage["pieces"]}, {"ivory", "red"}, layout)
            if layout == "wide":
                self.assertLessEqual({"bishop_m", "pawn_m", "berserker_m"}, kinds, layout)
            for kind in kinds | {"knight_m"}:
                self.assertTrue(24 <= len(A.PIECES[kind]) <= 30 or kind == "pawn_m", kind)
            right, g = (A.NARROW_RIGHT, 160) if layout == "phone" else (409, 100)
            p = Pix(right + 6, g + 20)
            x0 = 350 if layout == "corner" else None
            with mock.patch.object(A, "piece", wraps=A.piece) as piece, \
                    mock.patch.object(A, "knight_move", wraps=A.knight_move) as knight, \
                    mock.patch.object(A, "board_squares", wraps=A.board_squares) as squares, \
                    mock.patch.object(A, "gaming_table", wraps=A.gaming_table) as table:
                span = A.staged_game(p, right, g, False, False, layout, x0=x0)
            boxes = []
            for c in piece.call_args_list:
                rows = A.PIECES[c.args[1]]
                boxes.append((c.args[1], round(c.args[3] - len(rows[0]) / 2), c.args[4] - len(rows), len(rows[0]),
                              len(rows)))
            (move,) = knight.call_args_list
            board, rows = move.args[1], A.PIECES[move.kwargs["kind"]]
            for square in move.args[2:4]:
                x, y = board.at(*square)
                boxes.append(("knight", round(x - len(rows[0]) / 2), y - len(rows), len(rows[0]), len(rows)))
            for i, (k, x, y, w, h) in enumerate(boxes):
                for (k2, x2, y2, w2, h2) in boxes[i + 1:]:
                    if k == k2 == "knight" or min(x + w, x2 + w2) - max(x, x2) <= 1:
                        continue
                    (far, near) = ((y, y2), (y2, y)) if y + h <= y2 + h2 else ((y2, y), (y, y2))
                    self.assertLessEqual(far[0] + 9, far[1], (layout, k, k2, "the head behind shows whole"))
            (sq,) = squares.call_args_list
            (tb,) = table.call_args_list
            if layout == "corner":
                self.assertEqual(sq.args[3], p.w - A.EDGE, "the board runs off under the frame")
                self.assertGreaterEqual(tb.args[2], p.w - A.EDGE, "and its table")
            else:
                self.assertTrue(5 <= span[0] and span[1] <= right + 2, (layout, span, "inside the frame"))
            drawn = [x for x, y in p.layers["base"] if y == g - 1]
            self.assertTrue(drawn and min(drawn) >= span[0], (layout, "the table's feet on the floor"))

    def test_the_knight_lifts_off_his_square_and_leaps_only_in_a_moving_header(self):
        """In a moving H1 the knight lifts, leaps in an arc and lands on the square his move takes him to, rests
        and comes back, a frame each, his shadow on the board under him in every frame; a still drawing keeps him
        on his first square."""
        moving = SET.h1(HEADER, False, True)
        frames = sorted(n for n in moving.meta if re.fullmatch(r"kn\d", n))
        self.assertEqual(len(frames), 7)
        self.assertTrue(all(moving.meta[n][2][0] == "seq" for n in frames))
        tops = [min(y for (_, _, _, y, _) in moving.uses[n]) for n in frames]
        self.assertLess(min(tops), tops[0] - 6, "he leaps")
        self.assertTrue(all(len(moving.uses[n]) == 2 for n in frames), "the knight and his shadow in each")
        still = SET.h1(HEADER, False, False)
        self.assertFalse([n for n in still.meta if re.fullmatch(r"kn\d", n)])

    def test_an_h2_is_the_court_and_an_h3_the_queen_as_wide_as_the_words_leave_them(self):
        """A section's header stands its showpieces, the king on his throne and the berserker before him, as tall as
        the floor under the crossbeam lets them stand, and the whole court across the floor where the words leave it
        all; a strip's stands the queen on her throne the same way, at her full size where the strip is deep enough
        and her smaller one where it is not. Every piece of the court stands on its board, under the crossbeam."""
        for code, art, layouts in (("H2", "court", ((BARE, "spread", {"king_xl", "berserker_xl"}),
                                                     (HEADER, "wide", {"king_xl", "berserker_xl"}))),
                                   ("H3", "queen_seat", ((BARE, "wide_l", {"queen_l"}),
                                                         (HEADER, "wide", {"queen_xl"})))):
            for h, layout, big in layouts:
                _, p, spies = served(lambda: SET.header(code, h, DAY, True, True), (art, "great"))
                (scene,) = drawn_on(p, spies[art])
                self.assertEqual(scene.args[4], layout, (code, layout))
                kinds = [c.args[1] for c in drawn_on(p, spies["great"])]
                self.assertLessEqual(big, set(kinds), (code, layout))
                if layout == "spread":
                    self.assertGreaterEqual(len(kinds), 6, (code, "the court across the floor"))
        for table in (A.COURTS, A.SEATS):
            for layout, (files, ranks, pieces) in table.items():
                self.assertTrue(all(0 <= f <= files and 0 <= r <= ranks for _, _, f, r in pieces), layout)
        for name, (h, _) in contents(KEY).items():
            for code, art in (("H2", "court"), ("H3", "queen_seat")):
                _, p, spies = served(lambda: SET.header(code, h, DAY, True, True), (art, "great"))
                self.assertTrue(drawn_on(p, spies[art]), (name, code))
                rows = {c.args[1]: A.PIECES[c.args[1]] for c in drawn_on(p, spies["great"])}
                tops = [c.args[3].at(c.args[4], c.args[5])[1] - len(rows[c.args[1]])
                        + next(j for j, r in enumerate(rows[c.args[1]]) if r.strip("."))
                        for c in drawn_on(p, spies["great"])]
                self.assertGreaterEqual(min(tops), A.CEIL, (name, code, "under the crossbeam"))

    def test_the_great_pieces_are_the_lewis_chessmen(self):
        """Every piece is drawn whole, every row as wide as the first: the showpieces of the king on his throne with
        his sword across his knees, the queen with her hand to her cheek and the berserker biting his shield, each
        more than half as tall again as the great pieces at their smaller size, which stand taller than the pieces
        on the board."""
        for kind, rows in A.PIECES.items():
            self.assertTrue(all(len(r) == len(rows[0]) for r in rows), kind)
        for kind in ("king_l", "queen_l", "berserker_l"):
            self.assertGreater(len(A.PIECES[kind]), len(A.PIECES["king"]) + 15, kind)
        for kind in ("king_xl", "berserker_xl"):
            self.assertGreater(len(A.PIECES[kind]), len(A.PIECES[kind.replace("xl", "l")]) * 1.5, kind)
        self.assertGreater(len(A.PIECES["queen_xl"]), len(A.PIECES["queen_l"]), "the queen")
        for kind in ("king_xl", "queen_xl", "berserker_xl"):
            rows = A.PIECES[kind]
            self.assertGreaterEqual(sum(r.count("w") for r in rows), 4, (kind, "the whites of staring eyes"))
            self.assertGreaterEqual(sum(r.count("e") for r in rows), 4, (kind, "their pupils"))


class Phones(unittest.TestCase):
    def test_every_sprite_keeps_two_units_clear_of_every_word_on_a_phone(self):
        """On a phone the hall, the king and the queen beside or under the words, the band, the section mark and
        the rank inlaid along the rule are built to the rows the words leave free: no pixel of theirs lies within two
        units of a word's box, for any of the shared contents, by day or by night."""
        drawers = {"H1": SET.h1_narrow, "H2": SET.h2_narrow, "H3": SET.h3_narrow}
        for name, (h, _) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    p, pixels = sprites(lambda: drawer(h, night), "scene_narrow", "scene_under", "garland",
                                        "section_mark", "rule_decor")
                    hits = off_words(p, pixels)
                    self.assertEqual(hits[:6], [], (name, code, night, len(hits)))

    def test_every_sprite_keeps_two_units_clear_of_every_word_on_a_wide_header_too(self):
        """The scenes, the band, the marks beside a title and the rank along the rule keep the same two units from
        every word across a wide header."""
        drawers = {"H1": SET.h1, "H2": SET.h2, "H3": SET.h3}
        for name, (h, _) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    p, pixels = sprites(lambda: drawer(h, night, True), "scene", "garland", "section_mark",
                                        "strip_mark", "rule_decor")
                    hits = off_words(p, pixels)
                    self.assertEqual(hits[:6], [], (name, code, night, len(hits)))

    def test_every_phone_header_of_every_shared_content_stands_a_scene(self):
        """Every phone header of every shared content, by day and by night, drawn as the kit draws it, stands a scene
        of the set's on the drawing its file is made from: the hall on an H1, the king on an H2 and the queen on an
        H3, under the words."""
        pieces = {"H1": ("phone_hall",), "H2": ("phone_court",), "H3": ("phone_queen",)}
        names = sorted({n for ns in pieces.values() for n in ns})
        for name, (h, _) in contents(KEY).items():
            for code, wanted in pieces.items():
                for theme in (DAY, DARK):
                    _, p, spies = served(lambda: SET.header(code, h, theme, False, False), names)
                    self.assertTrue([n for n in wanted if drawn_on(p, spies[n])], (name, code, theme["name"]))

    def test_a_phones_showpieces_stand_under_its_words_at_their_full_size(self):
        """On a phone a section's header stands the showpieces of the king and the berserker in rows of their own under
        its words, and a strip's the queen, at their full size and clear of every word, whatever the header says: a
        hero on a phone stands forty rows tall or more, and beside the words it would reach into the crossbeam."""
        for code, art, big in (("H2", "phone_court", {"king_xl", "berserker_xl"}), ("H3", "phone_queen", {"queen_xl"})):
            draw = getattr(SET, code.lower() + "_narrow")
            for name in ("profile", "least"):
                h, _ = contents(KEY)[name]
                for night in (False, True):
                    with mock.patch.object(SET, "scene_under", wraps=SET.scene_under) as under, \
                            mock.patch.object(A, art, wraps=getattr(A, art)) as drawn, \
                            mock.patch.object(A, "great", wraps=A.great) as great:
                        p, pixels = sprites(lambda: draw(h, night), "scene_under")
                    where = (code, name, night)
                    self.assertTrue(under.called and drawn.called, where)
                    kinds = {c.args[1] for c in great.call_args_list if c.args[0] is p}
                    self.assertLessEqual(big, kinds, where)
                    self.assertGreaterEqual(max(len(A.PIECES[k]) for k in kinds), 40, (where, "a hero's height"))
                    self.assertEqual(off_words(p, pixels), [], where)


class Hall(unittest.TestCase):
    def test_every_header_is_the_halls_wall_its_words_on_the_woven_hanging(self):
        """Every header, wide and on a phone, of every shared content, by day and by night, is the hall: its wall of
        upright planks down to the floor, the crossbeam under the band, the hall's posts at its ends clear of every
        word, and the woven hanging hung from the beam behind every one of its words, its field the calm twill
        they sit on and keep 4.5:1 against."""
        for name, (h, _) in contents(KEY).items():
            for code in ("H1", "H2", "H3"):
                for theme in (DAY, DARK):
                    for wide in (True, False):
                        where = (name, code, theme["name"], wide)
                        _, p, spies = served(lambda: SET.header(code, h, theme, wide, False),
                                             ("hall_wall", "crossbeam", "hanging", "wall_posts"))
                        for spy in spies.values():
                            self.assertTrue(drawn_on(p, spy), where)
                        x0, y0, x1, y1 = p.hanging
                        for (a, b, c, d) in p.words:
                            if b > A.BAND_FOOT and d < p.hall:
                                self.assertTrue(x0 <= a and c <= x1 and y0 <= b and d <= y1, (where, (a, b, c, d)))
                        night = theme is DARK
                        for ink in ("body", "muted", "accent", "title"):
                            self.assertGreaterEqual(contrast(SET.ink(night)[ink], SET.bg_at(p, night, y0 + 6)), 4.5,
                                                    (where, ink))
                        posts = set(p.layers.get("far", {}))
                        self.assertEqual(off_words(p, posts), [], (where, "the posts"))


class Longest(unittest.TestCase):
    PIECES = ("hearth", "staged_game", "gaming_table", "knight_move", "fire", "smoke", "stones", "post", "horn",
              "dragon_head", "round_shield", "bench", "cauldron", "purse", "piece", "court", "queen_seat", "dais",
              "great", "notation", "glint", "frame", "carved_title", "rank_inlay", "hearthlight", "lamp", "oil_lamp",
              "daylight", "sunlit", "crossbeam", "hanging", "wall_posts", "hall_wall")

    def test_the_longest_page_keeps_its_whole_scene_and_its_motion_within_the_budget(self):
        """Every field at its longest, each wide header by day and by night, drawn as the kit draws it, as the
        month's design with its mark and kept all year, comes within the budget and still moves, and the drawing it
        is made from has every piece the drawing at full weight has, each where it stood: the hall's planks, its
        crossbeam, its posts and the hanging behind the words; the hearth with its fire, its smoke, its kerbs, its
        post and the dragon's head on it, its horn, its shield, its cauldron and its purse; the game on its table
        with every piece, the knight's leap and the lamp at the board's corner; by day the shaft of light on the game
        and its motes, by night the hearth's warmth and the two lights; the court, the band and its glint, the frame
        and the carved title. A drawing made lighter thins only the texture between them: the grain of the planks,
        the pegs of the crossbeam, the flecks and the half tones of the stones and the embers, the shading of the
        squares, the bands round the post, the links of the pot's chain, a few of the smoke's wisps, the outermost
        ring of each glow and the hearth's light along the title's letters."""
        most, _ = contents(KEY)["most"]

        def pieces(spies, p):
            return sorted(re.sub(r"'(ct|p|e)\d+'", "'#'", repr((n, c.args[1:], sorted(c.kwargs.items()))))
                          for n, spy in spies.items() for c in drawn_on(p, spy))
        lighter = []
        for kept, design in (("pinned", SET), ("held", SET.on(dt.date(2026, 2, 14)))):
            for code, named in (("H1", {"hearth", "staged_game", "knight_move", "fire", "oil_lamp", "hanging"}),
                                ("H2", {"court", "great", "hanging", "wall_posts"}), ("H3", {"queen_seat", "great"})):
                for theme in (DAY, DARK):
                    svg, p, spies = served(lambda: design.header(code, most, theme, True, True), self.PIECES)
                    with mock.patch.dict(BUDGET, {"header": 10 ** 9}):
                        _, whole, full = served(lambda: design.header(code, most, theme, True, True), self.PIECES)
                    where = (kept, code, theme["name"])
                    if p.lite:
                        lighter.append(where)
                    self.assertFalse(whole.lite, where)
                    self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"], where)
                    self.assertIn("<animate", svg, where)
                    self.assertEqual(pieces(spies, p), pieces(full, whole), where)
                    self.assertLessEqual(named, {n for n, spy in spies.items() if drawn_on(p, spy)}, where)
        self.assertIn(("held", "H1", "dark"), lighter, "the most a page can say is drawn lighter by night")


class Footers(unittest.TestCase):
    def test_every_footer_lies_on_the_boards_edge_with_the_pieces_taken_beside_it(self):
        """Every footer lies on the board's edge, rising into a rank of the board's squares wherever its cells leave
        it room, with the pieces taken in the game laid on their sides along it; an F1's notes have the toppled king
        of checkmate at their corner, a candle burning behind him by night only, on a phone as on a wide sheet."""
        f = contents(KEY)["kit"][1]
        for code in ("F1", "F2"):
            for wide in (True, False):
                with mock.patch.object(A, "edge_band", wraps=A.edge_band) as edge, \
                        mock.patch.object(A, "laid", wraps=A.laid) as laid:
                    SET.footer(code, f, DAY, wide, False)
                self.assertEqual(edge.call_count, 1, (code, wide))
                self.assertGreaterEqual(laid.call_count, 1, (code, wide, "a piece taken"))
        for wide in (True, False):
            with mock.patch.object(A, "toppled", wraps=A.toppled) as king, \
                    mock.patch.object(A, "candle", wraps=A.candle) as candle:
                day = SET.footer("F1", f, DAY, wide, False)
                self.assertEqual((king.call_count, candle.call_count), (1, 0), (wide, "the king, no candle by day"))
                night = SET.footer("F1", f, DARK, wide, False)
                self.assertEqual((king.call_count, candle.call_count), (2, 1), (wide, "the candle by night"))
            self.assertIn(FIRE[6], night, (wide, "its flame"))
            self.assertNotIn(FIRE[6], day, wide)

    def test_the_toppled_king_lies_at_the_boards_size_where_a_cell_has_room_for_him(self):
        """Where the notes' cell leaves him room, as the kit's notes do on a wide sheet and on a phone, the toppled
        king lies at the size the pieces stand on the board, by day and by night; where it leaves less, the smaller
        king."""
        f = contents(KEY)["kit"][1]
        for wide in (True, False):
            for theme in (DAY, DARK):
                with mock.patch.object(A, "toppled", wraps=A.toppled) as king:
                    SET.footer("F1", f, theme, wide, False)
                (call,) = king.call_args_list
                self.assertTrue(call.kwargs.get("big"), (wide, theme["name"]))
        self.assertGreater(len(A.KING), len(A.KING_S), "the larger king")

    def test_where_a_cell_leaves_room_a_rank_of_the_board_holds_the_pieces_taken(self):
        """Where a footer's cells leave a long stretch of its foot clear, as the page's own title block does after
        Back to Top, a rank of the board lies along the foot there, the pieces taken in the game standing on it in a
        row, ivory and red, and the toppled king lying across its end, his candle lit beside him by night only."""
        f = contents(KEY)["repository"][1]
        for theme in (DAY, DARK):
            with mock.patch.object(A, "footer_rank", wraps=A.footer_rank) as rank, \
                    mock.patch.object(A, "piece", wraps=A.piece) as piece, \
                    mock.patch.object(A, "toppled", wraps=A.toppled) as king, \
                    mock.patch.object(A, "candle", wraps=A.candle) as candle:
                SET.footer("F1", f, theme, True, False)
            (call,) = rank.call_args_list
            self.assertGreaterEqual(call.args[2] - call.args[1], A.RANK_MIN)
            standing = [c for c in piece.call_args_list if c.args[0] is call.args[0]]
            self.assertGreaterEqual(len(standing), 3, "the pieces taken, standing")
            self.assertEqual({c.args[2] for c in standing}, {"ivory", "red"})
            self.assertTrue(all(18 <= len(A.PIECES[c.args[1]]) or c.args[1] == "pawn" for c in standing))
            self.assertEqual(len(king.call_args_list), 1)
            self.assertEqual(len(candle.call_args_list), 1 if theme is DARK else 0)

    def test_the_edge_the_king_and_the_pieces_taken_keep_clear_of_every_word(self):
        """The board's edge rises only where the cells leave it room, and the king and the pieces taken lie only
        where the notes and the cells leave them, a clear row kept from every word in every footer the shared
        contents ask for."""
        for name, (_, f) in contents(KEY).items():
            for code, draw in FOOTERS:
                for night in (False, True):
                    p, pixels = sprites(lambda: draw(f, night), "_footed")
                    self.assertEqual(off_words(p, pixels, margin=1)[:6], [], (name, code, night))

    def test_a_link_is_a_tableman_and_a_small_file(self):
        """A link is a tableman, ivory and stained red by turns, its icon carved in it, on a tag of ivory its label
        is lettered on: a small file."""
        for i, label in enumerate(("Issues", "Pull Requests", "Releases", "Actions")):
            for theme in (DAY, DARK):
                svg = SET.link(label, theme, i)
                self.assertLess(len(svg.encode("utf-8")), 2500, (label, theme["name"]))
                self.assertIn((IV if i % 2 == 0 else RD)[0], svg, (label, "the tableman's rim"))
        icons = {tuple(A.link_icon(i, False)[0]) for i in range(4)}
        self.assertEqual(len(icons), 4, "a crown, a knight, a mitre and a pawn")


class Elements(unittest.TestCase):
    def test_an_avatar_is_one_of_the_chessmen_stained_in_its_colour_never_initials(self):
        """A contributor is the head and shoulders of one of the chessmen, a king, a queen, a bishop and a warder by
        turns, each stained in their own colour; a bot is a plain pawn. No letter is set."""
        for night in (False, True):
            seen = set()
            for i in range(5):
                p = Pix(40, 40)
                SET.avatar(p, 20, 20, i, {"initials": "IV", "name": "Imogen Vale"}, night)
                self.assertEqual(p.words, [], "no letters")
                drawn = set(p.layers["base"].values())
                stain = RAMP[A.STAINS[i]]
                self.assertTrue(set(stain[1:]) & drawn, (i, "stained in its colour"))
                self.assertIn(IV[6], drawn, (i, "the whites of its eyes"))
                seen.add(frozenset(drawn))
            self.assertEqual(len(seen), 5)
            q = Pix(40, 40)
            SET.avatar(q, 20, 20, 3, {"name": "Dependabot"}, night)
            self.assertLessEqual(set(q.layers["base"].values()), set(IV), "a bot's pawn of ivory")

    def test_a_counters_numerals_hold_4_5_on_their_tablemen_and_are_carved_over_them(self):
        """Every numeral holds 4.5:1 on its tableman, a leading nought fainter; and the tableman lies on a layer
        under the drawing's own, so a numeral is carved over it whatever its colour."""
        for night in (False, True):
            q = Pix(20, 20)
            SET.counter_cell(q, 2, 2, night)
            self.assertFalse(q.layers["base"], night)
            face = {q.layers["far"][(2 + x, 2 + y)] for x in range(3, 8) for y in range(5, 12)}
            self.assertEqual(len(face), 1, (night, "the numeral's whole field on the tableman's face"))
            self.assertGreaterEqual(contrast(SET.counter_ink(night, False), face.pop()), 4.5, night)
            self.assertGreaterEqual(contrast(SET.counter_ink(night, True), q.layers["far"][(7, 10)]), 1.5, night)

    def test_the_histogram_stacks_tablemen_every_fifth_stained_red(self):
        for night in (False, True):
            p = Pix(40, 60)
            SET.hist_bar(p, 10, 50, 8, 30, night)
            reds = sorted({y for (x, y), c in p.layers["base"].items() if c in RD[1:]})
            self.assertEqual(reds, [20, 21, 22, 35, 36, 37], (night, "the fifth man and the tenth red"))
            seams = [y for y in range(20, 50) if p.get(13, y) == IV[1]]
            self.assertEqual(len(seams), 8, (night, "ten men, a seam under each of ivory"))

    def test_a_card_is_a_tablet_of_ivory_with_its_icon_carved_in_a_tableman(self):
        """A schematic's card is a tablet of ivory: its icon carved again in a tableman at its left, of red bone and
        of ivory by turns, and along its lid, where it has one, a rank of the board inlaid."""
        for night in (False, True):
            k = -1 if night else 0
            for seed, lid in ((0, True), (1, False)):
                p = Pix(120, 40)
                x, y, w, h = 4, 4, 106, 28
                SET.node(p, night, x, y, w, h, {"title": "Probes", "path": "crates/probe", "icon": "grid"},
                         seed=seed, lid=lid)
                disc = {p.get(xx, yy) for xx in range(x + 3, x + 13) for yy in range(y + 9, y + 19)}
                self.assertTrue(set(RD if seed % 2 == 0 else IV) & disc, (night, seed))
                self.assertNotIn(SET.ink(night)["body"], disc, (night, seed, "the icon carved again"))
                band = {p.get(xx, y + 1) for xx in range(x + 16, x + w - 12)}
                self.assertEqual(band == {IV[6 + k], RD[4 + k]}, lid, (night, seed, "the rank along its lid"))

    def test_a_wire_is_a_thong_of_leather(self):
        p = Pix(60, 40)
        SET.wire(p, False, [(4, 10), (40, 10), (40, 30)])
        self.assertLessEqual({RAMP["leather"][5], RAMP["leather"][3]}, set(p.layers["base"].values()))

    def test_the_dial_is_a_quadrant_of_ivory_its_hand_a_bishops_crozier(self):
        """The dial is a quadrant of ivory cut with a groove; its hand is a bishop's crozier, its staff lit along its
        upper side, its crook curling at its head, and none of the layout's plain hand is left; it turns on a boss of
        ivory."""
        for night in (False, True):
            k = -1 if night else 0
            p = Pix(120, 60)
            SET.dial(p, {"value": 7, "span": 30, "sub": "v1"}, 60, 44, 30, night)
            SET.finish(p, night)
            drawn = set(p.layers["base"].values())
            self.assertNotIn(SET.ink(night)["accent"], drawn, (night, "the plain hand redrawn"))
            self.assertTrue({IV[6 + k], RAMP["honey"][3 + k]} <= drawn, (night, "the crozier's staff"))
            head = [xy for xy, c in p.layers["base"].items() if c in (IV[6 + k], RAMP["honey"][3 + k])
                    and math.hypot(xy[0] + 0.5 - 60, xy[1] + 0.5 - 44) > 12]
            self.assertGreaterEqual(len(head), 12, (night, "its crook at the far end"))

    def test_the_releases_are_pawns_on_a_rank_of_the_board_and_a_queen_is_crowned_at_today(self):
        """The time line is a rank of the board, squares of ivory and red bone, up to today; a pawn stands on it at
        each release, a red one for a big release; and at today's end a queen is crowned with a crown of gilt, in the
        key the crown alone."""
        spec = E.describe("milestones", ELEMENTS["history"])
        for theme in (DAY, DARK):
            with mock.patch.object(A, "queen_crowned", wraps=A.queen_crowned) as queen, \
                    mock.patch.object(A, "release_piece", wraps=A.release_piece) as pawn:
                svg = SET.element("milestones", spec, theme, "wide")
            self.assertEqual(queen.call_count, 1, theme["name"])
            kinds = {c.args[3] for c in pawn.call_args_list}
            self.assertTrue({"major", "big", "minor", "next"} <= kinds, theme["name"])
            self.assertIn(GILT[6], svg, "the crown's glint")

    def test_the_seal_is_a_kings_crown_of_red_bone(self):
        """The seal's rosette is a king's crown of bone stained red carved round it: a band all about the seal and
        the crown's points rising only from its upper half."""
        for night in (False, True):
            p = Pix(100, 100)
            SET.rosette(p, 50, 50, 23, 31, 16, night)
            cells = {xy for xy, c in p.layers["base"].items() if c in RD[1:]}
            beyond = [(x, y) for x, y in cells if math.hypot(x + 0.5 - 50, y + 0.5 - 50) > 27]
            self.assertTrue(beyond, night)
            self.assertTrue(all(y < 51 for _, y in beyond), (night, "the points rise from the upper half"))
            self.assertTrue([1 for x, y in cells if y > 70], (night, "the band all round"))
        svg = SET.element("certificate", E.describe("certificate", ELEMENTS["conformance"]), DAY, "wide")
        self.assertIn(RD[2], svg, "the ribbon of red tablet weaving")

    def test_a_placard_is_the_stone_kist_every_word_on_it_at_4_5(self):
        for theme in (DAY, DARK):
            night = theme is DARK
            svg = SET.element("placard", E.describe("placard", ELEMENTS["action"]), theme, "wide")
            face = (X["kist_night"], X["kist_fleck_n"]) if night else (X["kist"], X["kist_fleck"])
            for c in face:
                self.assertIn(c, svg, (theme["name"], "the kist's front slab"))
                for role in ("body", "muted"):
                    self.assertGreaterEqual(contrast(SET.ink(night)[role], c), 4.5, (theme["name"], role))
            self.assertIn(RAMP["stone"][5 if not night else 4], svg, "its lid")


class Badges(unittest.TestCase):
    def test_a_rank_of_the_board_lies_along_every_badges_top_with_the_letters_under_it(self):
        for style in BADGE_STYLES:
            drawn = [(SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                        SET.badge_states()["green"]), 0)]
            drawn += [(SET.plate_badge(style, "License", "MIT", "scale", mode), -1 if mode == "night" else 0)
                      for mode in ("day", "night")]
            for p, k in drawn:
                for y, want in ((0, {IV[6 + k], RD[5 + k]}), (1, {IV[3 + k], RD[2 + k]})):
                    row = {p.get(x, y) for x in range(p.w) if inside(x, y, p.w, p.h, BADGE_STYLES[style]["corner"])}
                    self.assertEqual(row, want, (style, y))
                self.assertTrue(all(y >= 2 for _, _, _, y, _ in p.uses["base"]), "the letters sit under it")


class Hand(unittest.TestCase):
    """The set is the medieval collection's February, drawn in the collection's hand."""

    def test_it_keeps_to_its_hand_as_the_months_design_and_kept_all_year(self):
        self.assertIsInstance(SET, CollectionSet)
        self.assertEqual(SET.collection, "medieval")
        self.assertEqual(check(SET), [])
        self.assertEqual(check(SET.on(dt.date(2026, 2, 14))), [])

    def test_its_words_are_in_the_hands_two_inks(self):
        for night in (False, True):
            k = SET.ink(night)
            self.assertEqual((k["body"], k["muted"]), (MEDIEVAL.body[night], MEDIEVAL.muted[night]), night)

    def test_the_ivory_and_the_wool_its_words_sit_on_fall_in_the_hands_bands(self):
        """By day the polished ivory of every sheet, a card's face, and the wool of the hanging, its field and the
        twill across it; by night the hall's dark and the wool in it."""
        lo, hi, most = MEDIEVAL.day_ground
        for c in (C["paper"], C["fill"], RAMP["wool"][4], RAMP["wool"][5]):
            light, chroma, _ = lab(c)
            self.assertTrue(lo <= light <= hi and chroma <= most, (c, light, chroma))
        lo, hi, most = MEDIEVAL.night_ground
        for c in (*NIGHT_SKY, RAMP["hall"][3], RAMP["hall"][4]):
            light, chroma, _ = lab(c)
            self.assertTrue(lo <= light <= hi and chroma <= most, (c, light, chroma))

    def test_every_flame_burns_on_the_hands_flame(self):
        """The hearth's fire and its sparks, the soapstone lamp's flame and the candle by the toppled king are all
        tones of the hand's flame ramp, by day and by night."""
        flame = MEDIEVAL.ramp("flame")
        self.assertEqual(RAMP["fire"], flame)
        for night in (False, True):
            p = SET.h1(HEADER, night, True)
            burning = {c for name in ("fire0", "fire1", "fire2") for c in p.layers[name].values()}
            self.assertTrue(burning and burning <= set(flame), (night, burning - set(flame)))
        f = contents(KEY)["kit"][1]
        _, p, spies = served(lambda: SET.footer("F1", f, DARK, True, False), ("candle",))
        (call,) = drawn_on(p, spies["candle"])
        x, foot = call.args[1], call.args[2]
        top = foot - len(A.CANDLE)
        lit = {p.get(x + i, top + j) for j, row in enumerate(A.CANDLE) for i, ch in enumerate(row) if ch in "fF"}
        self.assertTrue(lit and lit <= set(flame), lit)

    def test_its_motion_keeps_the_hands_timing(self):
        """The band's glint passes on the hand's period; the hearth's fire and the lamp leap on the engine's flicker;
        the knight's move, a figure's, and the smoke's rise loop in 4 to 8 seconds; the motes drift down the shaft in
        a slow sweep of 24 to 48 seconds. Every duration in a moving header is one of these, or one of the engine's
        own cadences."""
        engine = {BLINKS[k][2] for k in BLINKS}
        self.assertEqual(A.BURN, BLINKS["flicker"][2])
        self.assertTrue(24 <= A.MOTES <= 48)
        for theme in (DAY, DARK):
            svg = SET.on(dt.date(2026, 2, 14)).header("H1", HEADER, theme, True, True)
            durations = {float(d) for d in re.findall(r'dur="([\d.]+)s"', svg)}
            self.assertIn(MEDIEVAL.glint, durations, theme["name"])
            for d in durations:
                self.assertTrue(d in engine or d == MEDIEVAL.glint or 4 <= d <= 8 or 24 <= d <= 48, (theme["name"], d))

    def test_the_marks_box_is_clear_of_the_scene_and_cuts_no_name_in_the_band(self):
        """The box the month's mark takes at the top centre, and two units round it, is clear of the scene in every
        header the shared contents draw, wide and on a phone, by day and by night; the scene is the same whether the
        mark is drawn or not. No name in the band reaches into it: on a phone, where the band is short, the names part
        into two runs of four either side of it."""
        n = MEDIEVAL.mark_size
        for w in (WIDE, NARROW):
            x0 = w // 2 - n // 2
            for a, b, names in A.runs(0, w, w):
                for c0, c1 in A.carved(a, b, names)[0]:
                    self.assertTrue(c1 <= x0 - 2 or c0 >= x0 + n + 2, (w, names, c0, c1))
        self.assertEqual([len(names) for _, _, names in A.runs(0, NARROW, NARROW)], [4, 4])
        self.assertEqual(len(A.runs(0, WIDE, WIDE)), 1, "one run across a wide header")
        hooks = ("scene", "scene_narrow", "scene_under", "section_mark", "strip_mark", "rule_decor")
        for name, (h, _) in contents(KEY).items():
            for code in ("H1", "H2", "H3"):
                for night in (False, True):
                    for wide in (True, False):
                        if wide:
                            draw = {"H1": SET.h1, "H2": SET.h2, "H3": SET.h3}[code]
                            p, pixels = sprites(lambda: draw(h, night, True), *hooks)
                        else:
                            draw = {"H1": SET.h1_narrow, "H2": SET.h2_narrow, "H3": SET.h3_narrow}[code]
                            p, pixels = sprites(lambda: draw(h, night), *hooks)
                        x0, y0 = p.w // 2 - n // 2, MARK_Y - n // 2
                        inside_ = [xy for xy in pixels if x0 - 2 <= xy[0] < x0 + n + 2 and y0 - 2 <= xy[1] < y0 + n + 2]
                        self.assertEqual(inside_[:4], [], (name, code, night, wide))

    def test_its_scenes_stand_as_the_hands_composition_asks(self):
        """A phone's hall stands across the phone in at least 48 rows under its words, and a phone's showpieces, the
        hero of a section and of a strip, stand at least 40 rows tall."""
        self.assertGreaterEqual(SET.HALL_ROWS, 48)
        for kinds in (("king_xl", "berserker_xl"), ("queen_xl",)):
            self.assertGreaterEqual(max(len(A.PIECES[k]) for k in kinds), 40, kinds)
        least, _ = contents(KEY)["least"]
        for night in (False, True):
            with mock.patch.object(A, "phone_hall", wraps=A.phone_hall) as hall:
                p = SET.h1_narrow(least, night)
            (call,) = [c for c in hall.call_args_list if c.args[0] is p]
            self.assertGreaterEqual(call.args[3], 48, night)


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

    def test_ordinary_content_is_drawn_at_full_weight_with_room_to_spare(self):
        """The kit's own lines, the samples and the least a page can say, drawn as the month's design with the
        month's mark, come out as the kit draws them at full weight, with their motion, at least 1,500 bytes under
        their budgets; only the most a page can say is drawn lighter."""
        held = SET.on(dt.date(2026, 2, 14))
        for name, (h, f) in contents(KEY).items():
            if name == "most":
                continue
            for theme in (DAY, DARK):
                for code in ("H1", "H2", "H3"):
                    for wide, motion in ((True, True), (True, False), (False, False)):
                        what = (name, code, theme["name"], wide, motion)
                        svg, p, _ = served(lambda: held.header(code, h, theme, wide, motion))
                        self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"] - 1500, what)
                        self.assertFalse(p.lite, what)
                        self.assertEqual("<animate" in svg, wide and motion, what)
                for code in ("F1", "F2"):
                    for wide in (True, False):
                        svg, p, _ = served(lambda: held.footer(code, f, theme, wide, False))
                        self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["footer"] - 1500, (name, code, wide))
                        self.assertFalse(p.lite, (name, code, wide))

    def test_text_colours_hold_4_5_on_the_paper_and_every_row_of_the_night(self):
        """Every text colour holds 4.5:1 on the ivory and on every band of the night, and on the warmest the hearth's
        wash makes of the brightest of them; a tag's letters on the tag, a link's on its tag and the ribbon's on its
        weave."""
        warm = 1 - math.prod(1 - a for a in A.HEARTH_WASH)
        for night in (False, True):
            k = SET.ink(night)
            p = Pix(415, 200)
            grounds = {SET.bg_at(p, night, y) for y in range(p.h)}
            if night:
                top = max(NIGHT_SKY, key=lambda c: int(c[1:], 16))
                grounds.add("#%02X%02X%02X" % _blend(tuple(int(top[i:i + 2], 16) for i in (1, 3, 5)), FIRE[2], warm))
            for role in ("title", "body", "muted", "accent"):
                for ground in grounds:
                    self.assertGreaterEqual(contrast(k[role], ground), 4.5, (night, role, ground))
            self.assertGreaterEqual(contrast(k["tag_ink"], k["tag"]), 4.5, (night, "tag"))
            face, _, ink, _ = SET.link_colours(night)
            self.assertGreaterEqual(contrast(ink, face), 4.5, (night, "a link's letters on its tag"))

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
            for ch in DASHES:
                self.assertNotIn(ch, svg)
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
            self.assertIsNotNone(self.badge("flat", message_hex=PALETTE[family]), family)

    def test_what_the_sets_letters_cannot_draw_is_left_to_the_kit(self):
        self.assertIsNone(self.badge("flat", message="中文"))


if __name__ == "__main__":
    unittest.main()
