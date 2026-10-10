# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Alchemist set's own rules, which the checks every set shares cannot know: what the night alone shows
(the flasks' pools of green and violet on the wall, the furnace's fire and the orange it throws up the
athanor, the gold flask's light on the alchemist's beard, the moon's cold shaft, the crucible's flame, the
molten gold, the lantern and the candles burning, the sparks over the retort, the stars through the window and
the bubbles rising in the vessels) stays out of the day's files, and what the day alone shows (the shaft of
sun through the window and the dust drifting in it, the glints on the glass) out of the night's; every small
word keeps 4.5:1 with the night's lights laid on the wall round it; a title runs from lead at its left to gold
at its right, and a glint sweeps across it only in a wide moving header; the top shelf's vessels are a tile of
glassware, never a string of lights; the alchemist stands at a workbench that fills the lower part of his
column; drawn lighter, as the most a page can say is, a header keeps its whole laboratory, its lights, its
title's rim or glow and all its motion within the budget, thinning only texture, and ordinary content is drawn
at full weight with room to spare; a section's still stands its slot's height beside the table of the seven
metals, and a strip's great armillary sphere rises the strip's full height beside the hourglass and a candle;
every phone header stands a scene of the laboratory, a phone's H1 keeping the alchemist at his full size where
forty rows are left, and its H2 and H3 standing the still and the great sphere under their words whatever they
say; every scene, the vessels, the marks and the
bench along the rule keep two units from every word, on a phone and a wide header alike, and so do the
footers' crucible, their goods and what hangs over them; a footer stands on its bottom shelf, never bare, the
crucible at the corner of its notes at full size; a link is a small corked phial; a brass rim lies along every
badge's top row; the histogram's bars are graduated cylinders of clear glass, the busiest stoppered; a
schematic's cards are apothecary labels in frames of brass, joined by glass tubing; a counter's numerals hold
4.5:1 on their labels and are set over their jars; and the roster's avatars are alchemists, never initials.
The set is a theme, not a holiday on the calendar, so the checks every registered set shares run here over the
set directly, with the same contents and the same entry points."""
from __future__ import annotations

import contextlib
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
from domain.holidays.designs.badges import PLATE, STATES, STYLES as BADGE_STYLES, TOP, nearest
from domain.collections import zodiac
from domain.collections.hand import MEDIEVAL, check, lab
from domain.collections.medieval_alchemist import SET
from domain.collections.medieval_alchemist import art as A
from domain.collections.medieval_alchemist.palette import C, RAMP, X
from domain.holidays.designs.banners import MARK_Y
from domain.holidays.pixel import BLINKS, Pix, contrast
from domain.palette import PALETTE

support.install()
KEY = SET.key
HEADER = Header(tone="standard", holiday=KEY)
# The set drawn as the collection's design for September, its month, with the month's mark at the top centre.
HELD = SET.on(dt.date(2026, 9, 1))
# A profile's header, its motto and a note under its tagline, which leaves a phone's alchemist some forty rows.
PROFILE = Header(tone="standard", holiday=KEY, title="Tanner Golden",
                 tagline=("Infrastructure for AI research. Reproducibility, supply-chain hygiene, and CI that fails "
                          "for the right reasons."),
                 motto="Built to be rebuilt.", notes=("All times in EST.",), description="",
                 figures=(("ACCOUNT", "@tannergolden"), ("REPOSITORIES", "9"), ("CONTRIBUTIONS", "1,054"),
                          ("LANGUAGE", "Python"), ("MEMBER SINCE", "2016"), ("SITE", "tannergolden.com")))
LEAD, GOLD, GREEN, VIOLET, FIRE, BRASS = (RAMP[n] for n in ("lead", "gold", "green", "violet", "fire", "brass"))


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


# A block laid in a pattern (the bench along a rule, the row of vessels): what `sprites` reads to know which cells
# it covers, from a rectangle or from a run of a path that draws one.
RECT = re.compile(r'<rect x="(\d+)" y="(\d+)" width="(\d+)" height="(\d+)"')
RUN = re.compile(r'M(\d+) (\d+)h(\d+)v(\d+)h-\d+z')


def blocks(markup: str) -> list:
    """The blocks (x, y, width, height) the shapes in `markup` lay in a pattern: each rectangle, and each run of a
    path filled with one."""
    out = [tuple(map(int, b)) for b in RECT.findall(markup)]
    for d in re.findall(r'<path d="([^"]+)" fill="url\(#', markup):
        out += [tuple(map(int, b)) for b in RUN.findall(d)]
    return out


def sprites(draw, *hooks, held=None) -> tuple:
    """`draw()`'s drawing, and every pixel of the sprites the set's `hooks` (names of its drawing hooks) put on
    it, gathered as they draw: their pixels on every layer, the cells of the symbols they place, and the cells
    of the blocks they lay in a pattern. `held` is the set that draws: the one kept all year unless it is the
    one drawn as September's design."""
    held = SET if held is None else held
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
            out = hook(*args, **kw)
            for L, c in p.layers.items():
                pixels.update(set(c) - before.get(L, set()))
            for L, uses in p.uses.items():
                for (_, sid, x, y, s) in uses[placed.get(L, 0):]:
                    pixels.update((x + dx * s, y + dy * s) for dx, dy in cells.get(sid, ()))
            for L, shapes in p.shapes.items():
                for x, y, w, h in blocks("".join(shapes[laid.get(L, 0):])):
                    pixels.update((xx, yy) for xx in range(x, x + w) for yy in range(y, y + h))
            return out
        return drawn

    with mock.patch.object(Pix, "symbol", kept), \
            mock.patch.multiple(held, **{name: watched(getattr(held, name)) for name in hooks}):
        p = draw()
    return p, pixels


def off_words(p: Pix, pixels, margin=2) -> list:
    """The pixels among `pixels` that lie within `margin` units of a word's box."""
    return sorted(xy for xy in pixels if not p.clear_of_words(xy[0] - margin, xy[1] - margin, xy[0] + margin + 1,
                                                             xy[1] + margin + 1))


# The see-through light laid on a drawing: its pools, glows and shafts, and the box or shape that clips them.
TAG = re.compile(r'<(/?)(g|ellipse|polygon|rect|use)\b([^>]*?)(/?)>')
ATTR = re.compile(r'([a-z-]+)="([^"]*)"')
# Where a pool of light is placed from its rings: its heart and its reach across and down.
PLACED = re.compile(r"translate\(([-\d.]+) ([-\d.]+)\) scale\(([-\d.]+) ([-\d.]+)\)$")


def _see_through(markup: str, z, clips: dict, rings: dict, found: list):
    """The see-through shapes in `markup`, each with the fill and the clip it takes from the groups round it; a
    pool of light placed from its rings (`rings`, by symbol, each ring's reach and opacity) as each of them."""
    stack = [{}]
    for close, kind, attrs, empty in TAG.findall(markup):
        if close:
            if kind == "g" and len(stack) > 1:
                stack.pop()
            continue
        a = dict(ATTR.findall(attrs))
        if kind == "g":
            held = dict(stack[-1])
            if "fill" in a:
                held["fill"] = a["fill"]
            m = re.match(r"url\(#([^)]+)\)", a.get("clip-path", ""))
            if m:
                held["clip"] = clips.get(m.group(1))
            if not empty:
                stack.append(held)
            continue
        fill = a.get("fill", stack[-1].get("fill", ""))
        if kind == "use":
            m = PLACED.match(a.get("transform", ""))
            for reach, opacity in rings.get(a.get("href", "")[1:], ()) if m else ():
                cx, cy, rx, ry = (float(v) for v in m.groups())
                found.append((z, "ellipse", {"cx": cx, "cy": cy, "rx": rx * reach, "ry": ry * reach, "fill": fill,
                                             "fill-opacity": opacity}, stack[-1].get("clip")))
        elif "fill-opacity" in a and fill.startswith("#"):
            found.append((z, kind, dict(a, fill=fill), stack[-1].get("clip")))


def overlays(p: Pix) -> list:
    """Every see-through shape laid on `p`, (z, kind, attributes, clip), in the order they are drawn: the pools,
    glows and shafts of its layers and of its own markup, with the fill and the clip of the groups they are
    laid in, a pool placed from the rings kept once a file as each of its rings. Solid shapes and patterns are
    left out."""
    clips, rings = {}, {}
    for d in p.defs:
        m = re.match(r'<clipPath id="([^"]+)"><(rect|polygon) ([^>]*)/></clipPath>', d)
        if m:
            clips[m.group(1)] = (m.group(2), dict(ATTR.findall(m.group(3))))
        m = re.match(r'<g id="([^"]+)">((?:<circle [^>]*/>)+)</g>$', d)
        if m:
            rings[m.group(1)] = [(float(r), float(a)) for r, a in
                                 re.findall(r'<circle r="([^"]+)" fill-opacity="([^"]+)"/>', m.group(2))]
    found: list = []
    for name, shapes in p.shapes.items():
        _see_through("".join(shapes), p.meta[name][0], clips, rings, found)
    for (z, _, moving, _) in p.raws:
        _see_through(moving, z, clips, rings, found)
    return sorted(found, key=lambda t: t[0])


def _inside(kind, a, x, y) -> bool:
    if kind == "ellipse":
        rx, ry = float(a["rx"]), float(a["ry"])
        return rx > 0 and ry > 0 and ((x - float(a["cx"])) / rx) ** 2 + ((y - float(a["cy"])) / ry) ** 2 <= 1
    if kind == "rect":
        return (float(a["x"]) <= x < float(a["x"]) + float(a["width"])
                and float(a["y"]) <= y < float(a["y"]) + float(a["height"]))
    pts = [float(v) for v in a["points"].split()]
    poly = list(zip(pts[::2], pts[1::2]))
    inside = False
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside


def _blend(c, top, a):
    t = [int(top[i:i + 2], 16) for i in (1, 3, 5)]
    return tuple(round(c[i] * (1 - a) + t[i] * a) for i in range(3))


def worst_words(p: Pix, night: bool, inks: list) -> list:
    """For each small word set on `p` (`inks`, as `lettered` keeps them), the lowest contrast its colour holds
    over its box with every see-through light laid on the wall under it and on the word over it."""
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
                for (z, kind, a, clip) in shapes:
                    if clip and not _inside(clip[0], clip[1], x + 0.5, y + 0.5):
                        continue
                    if _inside(kind, a, x + 0.5, y + 0.5):
                        g = _blend(g, a["fill"], float(a["fill-opacity"]))
                        if z > 0:
                            fg = _blend(fg, a["fill"], float(a["fill-opacity"]))
                low = min(low, contrast("#%02X%02X%02X" % fg, "#%02X%02X%02X" % g))
        worst.append(((x0, y0, x1, y1), ink, round(low, 2)))
    return worst


def lettered(draw) -> tuple:
    """`draw()`'s drawing, and the box and colour of every line it set in small letters (titles, set large in
    their own paints, are left to the checks on the inks)."""
    inks = []
    text = Pix.text

    def kept(self, x, y, s, c, font="57", scale=1, *args, **kw):
        w = text(self, x, y, s, c, font, scale, *args, **kw)
        if scale == 1 and s.strip():
            inks.append((self.words[-1], c))
        return w
    with mock.patch.object(Pix, "text", kept):
        p = draw()
    return p, inks


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


def layers_named(p: Pix, prefix: str) -> list:
    return [L for L in p.layers if L.startswith(prefix) and (p.layers[L] or p.shapes[L])]


# What lies see-through on the wall and is no light: the shade under a shelf, and the old stains of what boiled
# over on the bench.
DARKS = {X["shade_ink"], GREEN[2], RAMP["blue"][2]}


def lights(p: Pix) -> set:
    """The lights on `p`: the colours of everything see-through laid on it but its shade and its stains (its
    pools, glows and shafts, as shapes or as pixels however faint), and of its flames."""
    flames = {c for L in layers_named(p, "fl") + layers_named(p, "fb") for c in p.layers[L].values()}
    faint = {c for L in p.layers for c in p.layers[L].values() if ":" in c}
    return ({a["fill"] for (_, _, a, _) in overlays(p)} | {c[:7] for c in flames | faint}) - DARKS


def motions(p: Pix) -> tuple:
    """What moves on `p`: each layer that moves and has something on it, by its name and how it moves, and how
    many pieces of its own markup move."""
    moving = {(L, p.meta[L][2][0]) for L in p.layers if p.meta[L][2] and (p.layers[L] or p.shapes[L] or p.uses[L])}
    return moving, sum("<animate" in m for (_, _, m, _) in p.raws)


def drawn_pieces(draw, names=(), held=None) -> tuple:
    """`draw()`'s result, every canvas the set made for it in turn, and for each canvas (by its id) which of the
    set's art named in `names` was drawn on it. `held` is the set that draws: the one kept all year unless it is
    the one drawn as September's design."""
    held = SET if held is None else held
    made, pieces = [], {}
    canvas = held.canvas

    def kept(*args, **kw):
        p = canvas(*args, **kw)
        made.append(p)
        pieces[id(p)] = set()
        return p

    def watched(name, art):
        def drawn(*args, **kw):
            p = next((a for a in args if isinstance(a, Pix)), None)
            if p is not None and id(p) in pieces:
                pieces[id(p)].add(name)
            return art(*args, **kw)
        return drawn
    with contextlib.ExitStack() as stack:
        stack.enter_context(mock.patch.object(held, "canvas", kept))
        for name in names:
            stack.enter_context(mock.patch.object(A, name, watched(name, getattr(A, name))))
        out = draw()
    return out, made, pieces


def title_letters(p: Pix) -> tuple:
    """A title set on `p`, read from its markup: the step of the change each of its letters stands at, from its
    left to its right, as the groups its letters are kept in say, and the step of the paint each group takes."""
    letters = []
    for d in p.defs:
        m = re.match(r'<g id="t\d+l(\d)" transform="[^"]*">(.*)</g>$', d)
        if m:
            letters += [(int(x or 0), int(m.group(1))) for x in re.findall(r'<use href="#q\d+"(?: x="(\d+)")?/>',
                                                                           m.group(2))]
    markup = "".join(m for (_, _, m, _) in p.raws)
    paints = {int(g): int(t) for g, t in re.findall(r'<use href="#t\d+l(\d)" stroke="url\(#patm(\d)', markup)}
    return [level for _, level in sorted(letters)], paints


class Night(unittest.TestCase):
    def test_what_the_night_alone_shows_stays_out_of_the_day_and_the_days_sun_out_of_the_night(self):
        """The fire in the furnace and its light, the flasks' glow on the wall, the sparks and the stars through
        the window are the night's; the sun through the window and the dust in it are the day's."""
        for code in ("H1", "H2", "H3"):
            day = SET.header(code, HEADER, DAY, True, True)
            night = SET.header(code, HEADER, DARK, True, True)
            self.assertNotIn(FIRE[6], day, (code, "the furnace's fire or a candle burning"))
            self.assertNotIn(f'fill="{GREEN[5]}"', day, (code, "the flasks' green on the wall"))
            self.assertNotIn(f'fill="{VIOLET[5]}"', day, (code, "the violet"))
            self.assertIn(f'<g fill="{VIOLET[5]}">', night, (code, "the violet pool on the wall"))
            self.assertNotIn(X["sun"], night, (code, "the sun"))
            self.assertIn(FIRE[6], night, (code, "the furnace burns, or a candle"))
        day, night = (SET.header("H1", HEADER, theme, True, True) for theme in (DAY, DARK))
        self.assertIn(X["sun"], day, "the sun comes down through the round window")
        self.assertIn(f'<g fill="{GREEN[5]}">', night, "the green flask lights the wall")
        self.assertIn(RAMP["sky"][1], night, "the night sky through the window")
        self.assertNotIn(RAMP["sky"][1], day, "and by day the sky's light instead")
        self.assertIn(X["star"], night, "stars through it")

    def test_the_lights_of_the_night_fall_on_what_stands_near_them(self):
        """By night the furnace's fire flickers and lays its light on the bench and the wall, the flasks' light
        holds steady on what stands near them, and the sparks rise from the retort frame by frame; by day the
        spirit lamp's small flame under the retort is the only flame, on the hand's flame and a tone short of its
        brightest, with no glow round it and no light laid on anything."""
        night = SET.h1(HEADER, True, True)
        self.assertTrue(layers_named(night, "fb"), "the fire's glow flickers")
        self.assertTrue(night.shapes.get("pool"), "the gold flask's shine over his hand, his face and his beard")
        sparks = {c for L in ("t0", "t1", "t2", "t3") for c in night.layers.get(L, {}).values()}
        self.assertIn(VIOLET[6], sparks, "a spark of violet over the retort")
        day = SET.h1(HEADER, False, True)
        flames = {c for L in layers_named(day, "fl") for c in day.layers[L].values()}
        self.assertTrue(flames, "the spirit lamp burns by day too")
        self.assertLessEqual(flames, set(MEDIEVAL.ramp("flame")) - {FIRE[6]}, "and only its small flame")
        self.assertFalse(layers_named(day, "fb"), "no glow flickers round it by day")
        self.assertFalse(day.shapes.get("pool"), "no light laid by day")

    def test_the_sun_comes_down_its_shaft_with_dust_and_the_moon_down_a_cold_one(self):
        """By day the round window lets a shaft of sun down across the wall to the bench, the dust drifting down
        through it in a moving header and resting in a still one; by night a fainter, colder shaft of moonlight
        comes down it, with no dust in it."""
        def drifting(p):
            return any(m.startswith('<g clip-path="url(#sb') and "animateTransform" in m for (_, _, m, _) in p.raws)
        moving = SET.h1(HEADER, False, True)
        self.assertIn(f'fill="{X["sun"]}"', "".join(moving.shapes["beam"]), "the shaft of sun")
        self.assertTrue(drifting(moving), "the dust drifting down it")
        self.assertFalse(drifting(SET.h1(HEADER, False, False)), "and resting in a still file")
        night = SET.h1(HEADER, True, True)
        beams = "".join(night.shapes["beam"])
        self.assertIn(f'fill="{RAMP["sky"][6]}"', beams, "the moon's shaft")
        self.assertNotIn(X["sun"], beams)
        self.assertFalse(drifting(night), "no dust by moonlight")

    def test_the_gold_flask_lights_his_beard_and_the_furnace_its_front(self):
        """By night the flask of gold he holds up lays its own gold on his beard round it, and the furnace's
        mouth throws its orange up the athanor's front, kept above the floor; by day his beard is white and the
        furnace is cold."""
        for night in (False, True):
            with mock.patch.object(A, "alchemist", wraps=A.alchemist) as him:
                p = SET.h1(HEADER, night, True)
            (_, x, y, _), _ = him.call_args
            beard = {p.get(x + i, y + j) for j, row in enumerate(A.ALCHEMIST) for i, ch in enumerate(row) if ch == "b"}
            self.assertEqual(bool(beard & set(GOLD)), night, "the gold's light on his beard")
            washes = [m for (_, _, m, _) in p.raws if m.startswith('<g clip-path="url(#fw')]
            self.assertEqual(bool(washes), night, "the fire's light up the furnace")
            for m in washes:
                self.assertIn(f'fill="{FIRE[4]}"', m)

    def test_every_small_word_holds_4_5_with_the_nights_lights_on_the_wall(self):
        """The pools of the flasks and the furnace, the glows and the moon's shaft fall on the wall round the
        words as well as on the scenes: every line set in small letters keeps 4.5:1 over all of it, on every
        header, phone and footer the shared contents draw by night."""
        drawers = [("H1", lambda h: SET.h1(h, True, True)), ("H2", lambda h: SET.h2(h, True, True)),
                   ("H3", lambda h: SET.h3(h, True, True)), ("H1n", lambda h: SET.h1_narrow(h, True)),
                   ("H2n", lambda h: SET.h2_narrow(h, True)), ("H3n", lambda h: SET.h3_narrow(h, True))]
        for name, (h, f) in contents(KEY).items():
            for code, draw in drawers + [("F1", lambda _: SET.f1(f, True)), ("F2", lambda _: SET.f2(f, True)),
                                         ("F1n", lambda _: SET.f1_narrow(f, True)),
                                         ("F2n", lambda _: SET.f2_narrow(f, True))]:
                p, inks = lettered(lambda: draw(h))
                low = [w for w in worst_words(p, True, inks) if w[2] < 4.5]
                self.assertEqual(low[:3], [], (name, code))

    def test_the_crucible_holds_lead_by_day_and_molten_gold_by_night(self):
        f = contents(KEY)["kit"][1]
        for wide in (True, False):
            day = SET.footer("F1", f, DAY, wide, False)
            night = SET.footer("F1", f, DARK, wide, False)
            self.assertNotIn(FIRE[6], day, (wide, "the lamp is out by day"))
            self.assertIn(FIRE[6], night, (wide, "and lit by night"))
            self.assertIn(GOLD[5], night, (wide, "the gold molten in it"))


class Titles(unittest.TestCase):
    def test_a_title_runs_from_lead_at_its_left_to_gold_at_its_right(self):
        """Every letter is painted in the transmutation's paint for how far along the line it stands: the first
        all lead, the last all gold, and those between turned in a fine grain, more gold the further right."""
        for night in (False, True):
            p = Pix(300, 40)
            A.transmuted_title(p, 4, 4, "TRANSMUTED", night, 4)
            levels, paints = title_letters(p)
            self.assertEqual(len(levels), len("TRANSMUTED"), "every letter kept once")
            self.assertEqual(levels[0], 0, "the first letter all lead")
            self.assertEqual(levels[-1], 4, "the last all gold")
            self.assertEqual(levels, sorted(levels), "more gold the further along")
            self.assertTrue(set(levels) & {1, 2, 3}, "and the change spreading through the letters between")
            self.assertEqual(paints, {level: level for level in levels}, "each step in its own paint")
        lead = A._metal_fill(0)
        gold = A._metal_fill(4)
        self.assertTrue(all(lead(r, c, 4, False) in LEAD for r in range(28) for c in range(24)))
        self.assertTrue(all(gold(r, c, 4, False) in GOLD for r in range(28) for c in range(24)))
        half = {A._metal_fill(2)(r, c, 4, False) for r in range(28) for c in range(24)}
        self.assertTrue(half & set(LEAD) and half & set(GOLD), "half lead, half gold, in a grain")

    def test_by_day_the_letters_sit_in_a_dark_rim_and_by_night_the_gold_glows(self):
        """By day the letters of each step are placed again in a dark rim along their upper left and their lower
        right, lead's for the lead and oak's for the gold; by night rings of gold glow round the gold letters,
        behind the wall's lights, and no rim is drawn."""
        p = Pix(300, 40)
        A.transmuted_title(p, 4, 4, "GOLD", False, 4)
        rims = dict(re.findall(r'<g stroke="(#[0-9A-F]{6})">((?:<use href="#t\d+l\d"[^>]*/>)+)</g>',
                               "".join(m for (_, _, m, _) in p.raws)))
        self.assertIn(LEAD[0], rims, "the lead's dark rim")
        self.assertIn(RAMP["oak"][0], rims, "the gold's dark rim")
        q = Pix(300, 40)
        A.transmuted_title(q, 4, 4, "GOLD", True, 4)
        glows = [m for (z, _, m, _) in q.raws if z < 0]
        self.assertTrue(any(m.startswith(f'<g stroke="{GOLD[4]}" stroke-opacity=') for m in glows),
                        "the gold glows by night")
        self.assertNotIn(f'<g stroke="{LEAD[0]}">', "".join(m for (_, _, m, _) in q.raws), "no rim by night")

    def test_a_glint_sweeps_across_the_title_only_in_a_wide_moving_header(self):
        moving = SET.header("H1", HEADER, DAY, True, True)
        self.assertRegex(moving, r'<mask id="tg\d+"', "the glint is seen only on the letters")
        self.assertIn('values="0 0;', moving, "and sweeps across them")
        for still in (SET.header("H1", HEADER, DAY, True, False), SET.header("H1", HEADER, DAY, False, False)):
            self.assertNotIn("<mask", still)
            self.assertNotIn("<animate", still)

    def test_the_title_reads_as_neither_hot_iron_nor_the_holiday_gold(self):
        """Lead and gold, cool to warm: no ember red or white heat in a title's paint, and lead at its start."""
        for night in (False, True):
            p = Pix(300, 40)
            A.transmuted_title(p, 4, 4, "ALCHEMY", night, 4)
            painted = {A._metal_fill(level)(r, c, 4, night) for level in range(5) for r in range(28)
                       for c in range(24)}
            self.assertLessEqual(painted, set(LEAD) | set(GOLD))
            self.assertNotIn("#FFFFFF", painted)


class Shelf(unittest.TestCase):
    def test_the_top_shelf_holds_a_tile_of_glass_vessels_never_a_string_of_lights(self):
        """The garland is one tile of a dozen vessels drawn from their own art, repeated along the shelf and cut
        at a gap between two; by day glints on their glass twinkle, by night bubbles rise in them frame by
        frame."""
        for night in (False, True):
            p = Pix(415, 40)
            A.vessels(p, 7, 408, night)
            rects = [s for s in p.shapes["base"] if 'fill="url(#vs)"' in s]
            self.assertEqual(len(rects), 1, "the row is one tile laid along the shelf")
            self.assertEqual(len(blocks(rects[0])), 2, "in two runs, either side of the top centre")
            tile = next(d for d in p.defs if d.startswith('<pattern id="vs"'))
            self.assertGreater(len(set(re.findall(r'stroke="(#[0-9A-F]{6})"', tile))), 12, "glass, cork, elixirs")
            frames = layers_named(p, "t")
            if night:
                self.assertEqual(len(frames), A.FRAMES, "bubbles rising, frame by frame")
                self.assertFalse(layers_named(p, "tw"))
            else:
                self.assertTrue(layers_named(p, "tw"), "the glints twinkle")
                self.assertFalse([L for L in frames if not L.startswith("tw")])
        width = A._shelf_tile()[1]
        self.assertGreater(width, 100, "a dozen vessels, not a dot every few pixels")

    def test_no_vessel_is_cut_by_the_months_mark(self):
        """The vessels stand in two runs, one either side of the top centre a header keeps for the month's mark,
        the shelf running on bare behind it: every run begins and ends at a gap between two vessels, so no vessel
        stands cut at the mark's edge or at an upright, the runs stand evenly about the top centre and a vessel
        or two short of each upright, wide and on a phone, whole or drawn lighter."""
        for w in (415, 180):
            for n in (len(A.SHELF_ROW), A.LITE_TILE):
                keep = A.top_centre(w)
                x0, x1 = A.POST + 2, w - A.POST - 2
                start, runs = A.shelf_runs(x0, x1, keep, n)
                placed, tw = A._shelf_tile(n)
                ends = {start + m * tw + vx + edge for m in range(-1, w // tw + 2) for name, vx, _ in placed
                        for edge in (0, len(A.VESSELS[name][0][0]))}
                self.assertEqual(len(runs), 2, (w, n))
                (la, lb), (ra, rb) = runs
                self.assertTrue(x0 <= la < lb <= keep[0] and keep[1] <= ra < rb <= x1, (w, n, runs, keep))
                self.assertLessEqual({la, lb, ra, rb}, ends, (w, n, "each run ends at a vessel's edge"))
                self.assertLessEqual(abs((keep[0] - lb) - (ra - keep[1])), 1, (w, n, "evenly about the mark"))
                self.assertLess(max(la - x0, x1 - rb), 13, (w, n, "close to the uprights"))
        for held in (HELD, SET):
            for wide in (True, False):
                for night in (False, True):
                    p = held.h1(HEADER, night, True) if wide else held.h1_narrow(HEADER, night)
                    keep = A.top_centre(p.w)
                    row = next(sh for sh in p.shapes["base"] if 'fill="url(#vs)"' in sh)
                    for (x, _, bw, _) in blocks(row):
                        self.assertTrue(x + bw <= keep[0] or x >= keep[1], (held.day, wide, night, x, bw))


class Phones(unittest.TestCase):
    def test_every_sprite_keeps_two_units_clear_of_every_word_on_a_phone(self):
        """On a phone the alchemist, the still, the hourglass, the vessels, the section mark and the bench along
        the rule are built to the rows the words leave free, beside them or under them: no pixel of theirs lies
        within two units of a word's box, for any of the shared contents, by day or by night."""
        drawers = {"H1": SET.h1_narrow, "H2": SET.h2_narrow, "H3": SET.h3_narrow}
        for name, (h, _) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    p, pixels = sprites(lambda: drawer(h, night), "scene_narrow", "scene_under", "garland",
                                        "section_mark", "rule_decor")
                    hits = off_words(p, pixels)
                    self.assertEqual(hits[:6], [], (name, code, night, len(hits)))

    def test_every_sprite_keeps_two_units_clear_of_every_word_on_a_wide_header_too(self):
        """The scenes, the vessels, the marks beside a title and the bench along the rule keep the same two units
        from every word across a wide header."""
        drawers = {"H1": SET.h1, "H2": SET.h2, "H3": SET.h3}
        for name, (h, _) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    p, pixels = sprites(lambda: drawer(h, night, True), "scene", "garland", "section_mark",
                                        "strip_mark", "rule_decor")
                    hits = off_words(p, pixels)
                    self.assertEqual(hits[:6], [], (name, code, night, len(hits)))

    def test_the_footers_crucible_and_its_books_and_jars_keep_clear_of_every_word(self):
        """The footers' crucible, their goods and what hangs over them keep the same two units from every word
        (the bottom shelf, laid as deep as the words leave, is checked with the footers)."""
        drawers = {"F1": (SET.f1, SET.f1_narrow), "F2": (SET.f2, SET.f2_narrow)}
        closings = ("", "Short.", "A closing phrase long enough to run the width of the notes and wrap twice over.")
        for closing in closings:
            f = Footer(tone="standard", holiday=KEY, closing=closing)
            for code, pair in drawers.items():
                for drawer in pair:
                    for night in (False, True):
                        with mock.patch.object(A, "foot_shelf"):
                            p, pixels = sprites(lambda: drawer(f, night), "_stocked", "bar")
                        self.assertTrue(pixels, (closing, code, night, "never bare"))
                        self.assertEqual(off_words(p, pixels)[:6], [], (closing, code, night))

    def test_the_scenes_stand_where_the_words_leave_them_room(self):
        """The kit's own lines leave each phone its scene, the athanor standing on an H1 and an H2; the least a page
        can say leaves the alchemist room to stand at the left of a phone; and the most a page can say is drawn
        round, never over."""
        h, _ = contents(KEY)["kit"]
        for code in ("H1", "H2"):
            svg = SET.header(code, h, DAY, False, False)
            self.assertIn(RAMP["clay"][4], svg, (code, "the athanor"))
        least, _ = contents(KEY)["least"]
        p, pixels = sprites(lambda: SET.h1_narrow(least, False), "scene_narrow")
        self.assertIn(RAMP["red"][4], {p.get(*xy) for xy in pixels}, "the alchemist's crimson cap")
        most, _ = contents(KEY)["most"]
        p, pixels = sprites(lambda: SET.h1_narrow(most, False), "scene_narrow")
        self.assertEqual(off_words(p, pixels), [])

    def test_every_phone_header_stands_a_scene_of_the_laboratory(self):
        """Every phone header of every shared content, by day and by night, stands a scene the set draws itself, a
        couple of hundred pixels at the least: an H1 in the rows it keeps under its words, and an H2 and an H3 in
        the rows they ask for under theirs, whatever the words say, never beside them."""
        drawers = {"H1": SET.h1_narrow, "H2": SET.h2_narrow, "H3": SET.h3_narrow}
        for name, (h, _) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    what = (name, code, night)
                    _, beside = sprites(lambda: drawer(h, night), "scene_narrow")
                    _, under = sprites(lambda: drawer(h, night), "scene_under")
                    self.assertGreaterEqual(len(beside | under), 200, what)
                    self.assertEqual((bool(beside), bool(under)), (code == "H1", code != "H1"), what)
            for code in ("H2", "H3"):
                self.assertEqual(SET.phone_rows(code, 0), SET.phone_rows(code, 400), (name, code, "whatever the title"))

    def test_a_phones_section_stands_the_still_beside_the_table_of_metals_under_its_words(self):
        """Whatever its words, a section's phone header stands its laboratory under them across the phone: the
        still, its alembic on a tall athanor, rising at least 44 rows over the bench beside the table of the seven
        metals, the green flask under the table, and the retort and a skull on its books at its right under a
        shelf of books and jars; by night the furnace and the candle burn and the violet lights the wall. Nothing
        of it comes within two units of a word."""
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                what = (name, night)
                with mock.patch.object(A, "chart", wraps=A.chart) as chart, \
                        mock.patch.object(A, "athanor", wraps=A.athanor) as athanor, \
                        mock.patch.object(A, "alembic", wraps=A.alembic) as alembic, \
                        mock.patch.object(A, "retort", wraps=A.retort) as retort, \
                        mock.patch.object(A, "skull", wraps=A.skull) as skull, \
                        mock.patch.object(A, "spines", wraps=A.spines) as spines:
                    p, pixels = sprites(lambda: SET.h2_narrow(h, night), "scene_under")
                self.assertTrue(chart.called and alembic.called and retort.called and skull.called and spines.called,
                                what)
                (_, x, foot, w, _, _), _ = athanor.call_args
                still = [y for (px, y) in pixels if x <= px < x + w]
                self.assertGreaterEqual(foot - min(still), 44, (what, "the still's height"))
                xs = [px for px, _ in pixels]
                self.assertLessEqual(min(xs), 6, what)
                self.assertGreaterEqual(max(xs), 173, what)
                self.assertEqual(off_words(p, pixels), [], what)
                burning = FIRE[6] in set(p.layers["base"].values()) | lights(p)
                self.assertEqual((VIOLET[5] in lights(p), burning), (night, night), (what, "lit by night"))

    def test_a_phones_strip_stands_the_great_sphere_under_its_words(self):
        """Whatever its words, a strip's phone header stands its laboratory under them across the phone: the great
        armillary sphere on its turned stand in the middle, rising at least 44 rows over the bench, the great
        hourglass on its books and a candle in its candlestick at its left, the green flask, a skull and the violet
        jar at its right, and shelves of jars and herbs drying on the wall either side of it; by night the candle
        burns and the violet lights the wall. Nothing of it comes within two units of a word."""
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                what = (name, night)
                with mock.patch.object(A, "great_armillary", wraps=A.great_armillary) as sphere, \
                        mock.patch.object(A, "great_glass", wraps=A.great_glass) as glass, \
                        mock.patch.object(A, "candlestick", wraps=A.candlestick) as stick, \
                        mock.patch.object(A, "herbs", wraps=A.herbs) as herbs, \
                        mock.patch.object(A, "wall_shelf", wraps=A.wall_shelf) as shelves:
                    p, pixels = sprites(lambda: SET.h3_narrow(h, night), "scene_under")
                self.assertTrue(glass.called and stick.called and herbs.called, what)
                self.assertEqual(shelves.call_count, 2, (what, "a shelf either side"))
                (_, cx, top, foot, r, _), _ = sphere.call_args
                self.assertGreaterEqual(r, A.GREAT_R, what)
                column = [y for (px, y) in pixels if px == cx and y < foot]
                self.assertEqual((min(column), max(column) + 1), (top, foot), (what, "from its axis to its foot"))
                self.assertGreaterEqual(foot - top, 44, (what, "the sphere's height"))
                xs = [px for px, _ in pixels]
                self.assertLessEqual(min(xs), 6, what)
                self.assertGreaterEqual(max(xs), 173, what)
                self.assertEqual(off_words(p, pixels), [], what)
                burning = FIRE[6] in set(p.layers["base"].values()) | lights(p)
                self.assertEqual((VIOLET[5] in lights(p), burning), (night, night), (what, "lit by night"))


class Laboratory(unittest.TestCase):
    def test_the_alchemist_stands_at_his_workbench_and_fills_his_column(self):
        """On a wide header the alchemist stands behind a workbench that fills the lower part of the left column,
        the mortar, the book and the green flask on it; he is the 48 columns of his sprite, over two fifths of the
        room tall, his cap clear of the crocodile over him."""
        for name in ("kit", "repository", "profile", "least"):
            h, _ = contents(KEY)[name]
            with mock.patch.object(A, "workbench", wraps=A.workbench) as bench, \
                    mock.patch.object(A, "alchemist", wraps=A.alchemist) as him, \
                    mock.patch.object(A, "mortar", wraps=A.mortar) as mortar:
                SET.h1(h, False, True)
            (p, x0, x1, top, foot, night), _ = bench.call_args
            self.assertGreaterEqual(foot - top, 18, (name, "the bench"))
            (_, x, sy, _), _ = him.call_args
            self.assertGreaterEqual(top - sy, 38, (name, "him over it"))
            self.assertGreaterEqual(sy, A.CROC_TOP + len(A.CROCODILE), (name, "under the crocodile"))
            self.assertTrue(mortar.called, name)
        self.assertEqual(len(A.ALCHEMIST[0]), 48)

    def test_drawn_lighter_the_bench_keeps_its_things_and_the_crocodile_over_it(self):
        """A header drawn lighter keeps its bench whole, the mortar on it and the carboy under it beside the skull
        on its books, so the cabinet under it is never an empty box, and the crocodile still hangs over it all:
        lighter thins texture, never a thing."""
        h, _ = contents(KEY)["repository"]
        for lite in (False, True):
            SET._lite = lite
            try:
                with mock.patch.object(A, "carboy", wraps=A.carboy) as carboy, \
                        mock.patch.object(A, "mortar", wraps=A.mortar) as mortar, \
                        mock.patch.object(A, "skull", wraps=A.skull) as skull, \
                        mock.patch.object(A, "crocodile", wraps=A.crocodile) as croc:
                    SET.h1(h, True, False)
            finally:
                SET._lite = False
            self.assertTrue(carboy.called and mortar.called and skull.called and croc.called, lite)

    def test_a_sections_still_stands_the_slots_height_beside_the_table_of_metals(self):
        """A section's great alembic stands on an athanor as tall as its slot allows, beside the table of the
        seven metals, 39 by 38 and its signs inked large, a lantern hung on its chain between them and herbs
        drying from the top shelf, books and jars on a shelf of their own; by night the lantern burns."""
        h, _ = contents(KEY)["kit"]
        for night in (False, True):
            with mock.patch.object(A, "athanor", wraps=A.athanor) as athanor, \
                    mock.patch.object(A, "chart", wraps=A.chart) as chart, \
                    mock.patch.object(A, "lantern", wraps=A.lantern) as lantern, \
                    mock.patch.object(A, "herbs", wraps=A.herbs) as herbs, \
                    mock.patch.object(A, "spines", wraps=A.spines) as spines:
                p = SET.h2(h, night, True)
            self.assertGreaterEqual(athanor.call_args[0][4], 50, "the athanor the slot's height")
            self.assertTrue(chart.called and lantern.called and herbs.called and spines.called)
            flames = {c for L in layers_named(p, "fl") for c in p.layers[L].values()}
            self.assertEqual(FIRE[6] in flames, night, "the lantern's candle burns by night")
        self.assertEqual((A.CHART_W, A.CHART_H), (39, 38))
        self.assertGreaterEqual(min(len(sign) for sign in A.METALS.values()), 9, "each sign a line of writing tall")

    def test_a_strips_great_sphere_rises_the_strips_full_height_beside_the_hourglass_and_a_candle(self):
        """A strip's great armillary sphere stands on its turned stand of brass on the bench and rises the strip's
        full height, the tip of its axis a row clear of the top shelf, sixty rows at the most where the strip is
        taller still;
        beside it the great hourglass stands on its books and a candle in its brass candlestick, burning by night
        and dark by day, for every shared content."""
        shelf = A.SHELF + A.BOARD
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "great_armillary", wraps=A.great_armillary) as sphere, \
                        mock.patch.object(A, "great_glass", wraps=A.great_glass) as glass, \
                        mock.patch.object(A, "candlestick", wraps=A.candlestick) as stick:
                    svg = SET.header("H3", h, DARK if night else DAY, True, True)
                (_, _, top, foot, r, _), _ = sphere.call_args
                self.assertEqual(r, A.GREAT_R, name)
                self.assertEqual(foot - top, min(foot - shelf - 1, A.GREAT_MOST), (name, "the strip's full height"))
                self.assertGreaterEqual(foot - top, 54, name)
                self.assertTrue(glass.called and stick.called, name)
                self.assertEqual(FIRE[6] in svg, night, (name, "the candle lit by night"))

    def test_a_profiles_phone_keeps_the_alchemist_at_his_size_where_forty_rows_are_left(self):
        """A profile's phone, whose words leave the alchemist's corner some forty rows, closes the laboratory in
        round him at his full size: his bench stands lower and hides more of him, his cap, his face and the
        flask he holds up stand over it, nothing of him shows under it, and the still stands at the right."""
        with mock.patch.object(A, "alchemist", wraps=A.alchemist) as him, \
                mock.patch.object(A, "small_alchemist", wraps=A.small_alchemist) as small, \
                mock.patch.object(A, "athanor", wraps=A.athanor) as athanor, \
                mock.patch.object(A, "phone_lab", wraps=A.phone_lab) as lab:
            p = SET.h1_narrow(PROFILE, False)
        room = lab.call_args[0][-1]
        self.assertTrue(38 <= room < 47, room)
        self.assertTrue(him.called and not small.called, "the alchemist of a wide header, not the small one")
        (_, x, sy, _), kw = him.call_args
        top = kw["bench"]
        self.assertGreaterEqual(top - sy, 30, "his cap, his face and the flask he holds up over the bench")
        robe = {RAMP["blue"][n] for n in (1, 2, 4)}
        under = [(xx, yy) for xx in range(x, x + len(A.ALCHEMIST[0])) for yy in range(top + 7, p.h)
                 if p.get(xx, yy) in robe]
        self.assertEqual(under, [], "nothing of him under his bench")
        self.assertTrue(athanor.called, "and the still")

    def test_a_phone_lays_its_laboratory_out_under_its_words(self):
        """A phone's H1 leaves rows under its words for its laboratory: the alchemist of a wide header at his
        workbench, the retort and his books, and the larger still."""
        self.assertGreater(SET.phone_scene_rows, 0)
        h, _ = contents(KEY)["kit"]
        with mock.patch.object(A, "alchemist", wraps=A.alchemist) as him, \
                mock.patch.object(A, "retort", wraps=A.retort) as retort, \
                mock.patch.object(A, "athanor", wraps=A.athanor) as athanor:
            SET.h1_narrow(h, False)
        self.assertTrue(him.called and retort.called, "the alchemist and the retort")
        self.assertEqual(athanor.call_args[0][3:5], (16, 22), "the larger still")


# The pieces of a wide header's laboratory a reader can name, which drawn lighter it keeps, and what every header
# has round them: its frame, the shelf of vessels over it and its title.
PIECES = {"H1": ("alchemist", "workbench", "mortar", "book", "green_flask", "carboy", "books", "skull", "crocodile",
                 "window", "bench", "athanor", "alembic", "receiver", "retort", "wall_shelf", "armillary", "hourglass"),
          "H2": ("bench", "athanor", "alembic", "receiver", "wall_shelf", "spines", "jars", "books", "skull", "candle",
                 "chart", "herbs", "lantern", "retort", "green_flask")}
EVERY_HEADER = ("frame", "vessels", "transmuted_title")


class Lighter(unittest.TestCase):
    def test_the_longest_pages_keep_their_whole_laboratory_and_its_motion_within_the_budget(self):
        """The most a page can say comes out over the budget on a wide H1 and H2 at full weight, so the kit draws
        them lighter. By day and by night, moving and still, each comes within the budget and keeps every piece
        of its laboratory (the alchemist, the crocodile, the bench and its goods, the athanor, the flasks), the
        shelf of vessels and the frame, its title's rim by day and its glow by night, every light it has at full
        weight, and everything that moves at full weight, the glint across its title among it: lighter thins
        only texture. So it is kept all year and as September's design, with the month's mark."""
        most, _ = contents(KEY)["most"]
        names = sorted(set(PIECES["H1"]) | set(PIECES["H2"]) | set(EVERY_HEADER) | {"sunbeam", "moonbeam"})
        lighter = []
        for code in ("H1", "H2"):
            for theme in (DAY, DARK):
                night = bool(theme["dark"])
                for motion, held in ((True, SET), (False, SET), (True, HELD), (False, HELD)):
                    what = (code, theme["name"], "moving" if motion else "still", held.day)
                    svg, made, pieces = drawn_pieces(lambda: held.header(code, most, theme, True, motion), names,
                                                     held=held)
                    full, p = made[0], made[-1]
                    self.assertFalse(full.lite, what)
                    if p.lite:
                        lighter.append(what)
                    self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"], what)
                    wanted = set(PIECES[code]) | set(EVERY_HEADER)
                    if code == "H1":
                        wanted.add("moonbeam" if night else "sunbeam")
                    self.assertEqual(wanted - pieces[id(p)], set(), what)
                    self.assertEqual(lights(p), lights(full), what)
                    rim = f'<g stroke="{GOLD[4]}" stroke-opacity=' if night else f'<g stroke="{LEAD[0]}">'
                    self.assertIn(rim, svg, (what, "the title's glow by night and its rim by day"))
                    if motion:
                        self.assertIn("<animate", svg, what)
                        self.assertRegex(svg, r'<mask id="tg\d+"', (what, "the glint"))
                        self.assertEqual(motions(p), motions(full), what)
        self.assertGreaterEqual(len(lighter), 8, "the most a page can say is drawn lighter")


FOOTERS = (("F1", SET.f1), ("F2", SET.f2), ("F1n", SET.f1_narrow), ("F2n", SET.f2_narrow))


class Footers(unittest.TestCase):
    def test_every_footer_stands_on_a_bottom_shelf_as_deep_as_its_words_leave(self):
        """A footer's bottom shelf is laid once its words are set: four rows deep, a row shallower than a
        header's so its goods have the more room over it, and three where its last cell's words come down to
        the foot, so no word ever stands on it."""
        for name, (_, f) in contents(KEY).items():
            for code, draw in FOOTERS:
                p = draw(f, False)
                m = re.search(r'<pattern id="frf" y="(\d+)" width="40" height="(\d+)"', "".join(p.defs))
                self.assertTrue(m, (name, code, "the bottom shelf"))
                y, depth = int(m.group(1)), int(m.group(2))
                self.assertEqual(y + depth, p.h, (name, code))
                self.assertTrue(3 <= depth <= 4, (name, code, depth))
                self.assertTrue(p.clear_of_words(0, y, p.w, p.h), (name, code, "no word on the shelf"))
                if p.clear_of_words(0, p.h - 4, p.w, p.h):
                    self.assertEqual(depth, 4, (name, code, "four rows where the words leave them"))
        self.assertRegex(SET.header("H1", HEADER, DAY, True, True), r'<pattern id="frf" y="\d+" width="40" height="5"')
        sheet = SET.element("roster", E.describe("roster", ELEMENTS["contributors"]), DAY, "wide")
        self.assertIn('<pattern id="frt" y="0"', sheet, "a sheet's top board")

    def test_no_footer_is_bare_and_its_goods_keep_clear_of_every_word(self):
        """Wherever its words leave room a footer's shelves hold the laboratory's goods, books and jars, the
        skull, the carboy, a candle and the low things under the words, each standing on a shelf or a rule with
        two units between it and every word; over a stretch of wall the words leave empty the crocodile and
        the herbs hang from the top shelf."""
        hung = []
        for name, (_, f) in contents(KEY).items():
            for code, draw in FOOTERS:
                with mock.patch.object(A, "_good", wraps=A._good) as good, \
                        mock.patch.object(A, "crucible", wraps=A.crucible) as pot, \
                        mock.patch.object(A, "crocodile", wraps=A.crocodile) as croc:
                    p = draw(f, False)
                self.assertTrue(good.called, (name, code, "goods on the shelf"))
                for call in good.call_args_list:
                    _, kind, x, foot, _, _ = call[0]
                    w, h = A._size(kind)
                    self.assertTrue(p.clear_of_words(x - 2, foot - h - 2, x + w + 2, foot), (name, code, kind, x))
                for call in pot.call_args_list:
                    _, x, foot, _ = call[0]
                    art = A.CRUCIBLE_SMALL if call[1].get("small") else A.CRUCIBLE
                    self.assertTrue(p.clear_of_words(x - 2, foot - len(art) - 2, x + len(art[0]) + 2, foot),
                                    (name, code, "the crucible"))
                if croc.called:
                    hung.append((name, code))
        self.assertIn(("profile", "F2"), hung, "the crocodile over the empty middle of a footer with no notes")

    def test_the_crucible_reads_at_full_size_at_the_corner_of_the_notes(self):
        """The crucible, the footer's mark, stands 18 columns wide where the notes keep their corner for it, on
        the shelf of a wide footer and on the rule under the notes of a phone's; it stands smaller only where
        nothing else fits."""
        f = contents(KEY)["kit"][1]
        for draw in (SET.f1, SET.f1_narrow):
            with mock.patch.object(A, "crucible", wraps=A.crucible) as pot:
                p = draw(f, False)
            self.assertEqual(pot.call_count, 1)
            self.assertFalse(pot.call_args[1].get("small"), "full size")
            x = pot.call_args[0][1]
            self.assertLess(abs(x + len(A.CRUCIBLE[0]) // 2 - p.mark[0]), 12, "beside the corner of the notes")
        self.assertEqual((len(A.CRUCIBLE[0]), len(A.CRUCIBLE)), (18, 19))

    def test_a_link_is_a_small_corked_phial_with_a_bold_icon(self):
        for i, label in enumerate(("Issues", "Pull Requests", "Releases", "Actions")):
            for theme in (DAY, DARK):
                svg = SET.link(label, theme, i)
                self.assertLess(len(svg.encode("utf-8")), 2500, (label, theme["name"]))
                k = -1 if theme is DARK else 0
                self.assertIn(RAMP["amber"][3 + k], svg, "the cork")
                self.assertIn(RAMP["glass"][2], svg, "the glass")
        icons = {tuple(A.link_icon(i, False, "#000000")[0]) for i in range(4)}
        self.assertEqual(len(icons), 4, "a flask, an hourglass, the sign for gold and a book")


class Elements(unittest.TestCase):
    def test_an_avatar_is_an_alchemist_in_robe_and_cap_never_initials(self):
        for night in (False, True):
            p = Pix(60, 40)
            with mock.patch.object(Pix, "text", side_effect=AssertionError("initials lettered")) as lettered:
                SET.avatar(p, 10, 20, 0, {"initials": "AB", "name": "A B"}, night)
                SET.avatar(p, 30, 20, 1, {"initials": "CD", "name": "C D"}, night)
                SET.avatar(p, 50, 20, 2, {"name": "a bot"}, night)
            self.assertEqual(lettered.call_count, 0)
            painted = set(p.layers["base"].values())
            self.assertTrue(painted & set(RAMP["skin"]), "faces")
            self.assertTrue(painted & set(RAMP["bone"]), "a collar of fur")
        looks = set()
        for name in ("Imogen Vale", "Tomas Okafor", "Wren Castellan", "Ada", "Jabir", "Roger"):
            p = Pix(20, 30)
            A.alchemist_head(p, 9, 14, {"name": name, "initials": name[:2]}, 0, False)
            looks.add(frozenset(p.layers["base"].items()))
        self.assertEqual(len(looks), 6, "each in his own looks, drawn from his name")

    def test_a_counters_numerals_hold_4_5_on_their_labels_and_stand_over_their_jars(self):
        for night in (False, True):
            q = Pix(20, 20)
            SET.counter_cell(q, 2, 2, night)
            face = q.layers["base"][(7, 9)]
            self.assertGreaterEqual(contrast(SET.counter_ink(night, False), face), 4.5, night)
            self.assertGreaterEqual(contrast(SET.counter_ink(night, True), face), 2.0, night)
            k = SET.ink(night)
            self.assertNotIn(SET.counter_ink(night, False), {k["tag_ink"], k["muted"], k["body"]},
                             "an ink no word set before the jars shares, so its numerals are set after them")

    def test_the_instruments_are_glass_and_brass(self):
        """The histogram's bars are graduated cylinders filled with the elixirs by turns; the dial is a balance
        with its pans, lead in one and gold in the other; the counters are apothecary jars."""
        spec = E.describe("instruments", next(d for d in ELEMENTS.values() if d["kind"] == "instruments"))
        for theme in (DAY, DARK):
            svg = SET.element("instruments", spec, theme, "wide")
            for elixir in ("green", "violet", "amber"):
                self.assertTrue(any(c in svg for c in RAMP[elixir]), (theme["name"], elixir))
            self.assertIn(RAMP["blue"][3 + (-1 if theme is DARK else 0)], svg, "the jars' glaze")
            self.assertIn(GOLD[6], svg, "the nugget of gold in its pan")
            self.assertIn(LEAD[5], svg, "and the lead in the other")

    def test_a_cylinder_is_clear_glass_graduated_and_filled_with_its_elixir(self):
        """Each bar is a cylinder of clear glass as tall as the bar: its lip and its foot a pixel wider each side,
        a line of light down the inside of its near wall, clear glass under the lip, the elixir filling the rest,
        the graduation etched on the glass; by night the elixir glows on the wall and has bubbles in it."""
        green = RAMP["green"]
        for night in (False, True):
            p = Pix(30, 60)
            A.cylinder_bar(p, 8, 52, 12, 40, night, "green")
            base, top = p.layers["base"], 12
            for y in (top, 51):
                self.assertEqual({x for (x, yy) in base if yy == y}, set(range(7, 21)), (night, "lip and foot"))
            self.assertEqual(base[(8, 30)], RAMP["glass"][3], "the near wall, lit")
            self.assertEqual(base[(19, 30)], RAMP["glass"][1], "the far wall, dark")
            self.assertEqual(base[(9, 40)], green[6], "the line of light down the inside of the wall")
            if not night:
                self.assertEqual(base[(12, top + 1)], RAMP["glass"][6], "clear glass under the lip")
            self.assertIn(base[(12, 40)], green, "the elixir")
            ticks = [y for y in range(top + 4, 50) if base.get((17, y)) == RAMP["glass"][6]]
            self.assertGreaterEqual(len(ticks), 8, "the graduation etched every third row")
            glows = [s_ for s_ in p.shapes.get("haze", ()) if "<ellipse" in s_]
            self.assertEqual(bool(glows), night, "the elixir glows only by night")

    def test_the_busiest_weeks_cylinder_is_stoppered(self):
        spec = E.describe("instruments", next(d for d in ELEMENTS.values() if d["kind"] == "instruments"))
        heights = []

        def kept(p, bx, base, bw, v, night, elixir, L="base"):
            heights.append(v)
            return cylinder(p, bx, base, bw, v, night, elixir, L)
        cylinder = A.cylinder_bar
        for night in (False, True):
            heights.clear()
            with mock.patch.object(A, "cylinder_bar", kept), \
                    mock.patch.object(A, "stopper", wraps=A.stopper) as corked:
                SET.draw_element("instruments", spec, night, "wide")
            self.assertEqual(corked.call_count, 1, night)
            self.assertEqual(corked.call_args[0][4], max(heights), "the cork is in the tallest cylinder")

    def test_a_schematic_card_is_an_apothecary_label_in_a_frame_of_brass(self):
        """A card's frame is brass with a rivet at each corner, its words sit on a label of parchment that keeps
        them at 4.5:1, pale by day and dark by night, and its icon is engraved in a round brass medallion."""
        icon = {(1, 1), (2, 1), (3, 3), (5, 5)}
        for night in (False, True):
            k = SET.ink(night)
            p = Pix(120, 40)
            for (i, j) in icon:
                p.px(4 + 2 + i, 4 + (28 - 7) // 2 + j, k["body"])
            A.brass_card(p, 4, 4, 106, 28, night, k["body"])
            base = p.layers["base"]
            for (rx, ry) in ((5, 5), (107, 5), (5, 29), (107, 29)):
                self.assertEqual(base[(rx, ry)], BRASS[6 + (-1 if night else 0)], (night, "a rivet", rx, ry))
            label = base[(60, 16)]
            self.assertEqual(label, RAMP["bone"][0 if night else 5], night)
            for role in ("body", "muted"):
                self.assertGreaterEqual(contrast(k[role], label), 4.5, (night, role))
            engraved = {(x, y) for (x, y), c in base.items() if c == RAMP["oak"][0] and 6 <= x <= 16}
            self.assertEqual(len(engraved), len(icon), "the icon engraved in the medallion")
            self.assertIn(base[(11, 14)], BRASS, "the medallion is brass round the icon")

    def test_a_wire_is_glass_tubing_with_a_collar_at_each_bend(self):
        cells = [(x, 10, "h") for x in range(5, 30)] + [(30, y, "v") for y in range(10, 30)]
        cells.insert(25, (30, 10, "h"))
        for night in (False, True):
            p = Pix(50, 40)
            A.tube_over(p, cells, night)
            base = p.layers["base"]
            column = [base.get((15, y)) for y in range(9, 13)]
            self.assertEqual(column[0], RAMP["glass"][5 + (-1 if night else 0)], "the near wall, lit")
            self.assertEqual(column[3], RAMP["glass"][1], "the far wall")
            self.assertIn(column[2], GREEN, "the elixir")
            self.assertEqual(len(set(column)), 4, "two units of tube inside its walls")
            self.assertIn(base[(30, 10)], BRASS, "a brass collar at the bend")
            self.assertIn(base[(5, 10)], BRASS, "and where it leaves its card")

    def test_a_placard_is_a_brass_bound_cabinet_door(self):
        for theme in (DAY, DARK):
            svg = SET.element("placard", E.describe("placard", ELEMENTS["action"]), theme, "wide")
            self.assertIn(BRASS[1], svg, "the brass bindings")
            self.assertIn(RAMP["oak"][0], svg, "the oak frame")
            self.assertNotIn('<pattern id="plw"', svg, "no wall: a door")

    def test_the_seal_is_the_ouroboros_in_red_wax_and_its_ribbon_green_silk(self):
        spec = E.describe("certificate", ELEMENTS["conformance"])
        for theme in (DAY, DARK):
            p = SET.draw_element("certificate", spec, theme is DARK, "wide")
            painted = set(p.layers["base"].values())
            self.assertGreater(len(painted & set(RAMP["red"])), 3, "the serpent's wax")
            self.assertIn(GOLD[5], painted, "its gold eye")
            self.assertIn(GREEN[5], painted, "the silk ribbon")

    def test_a_release_keeps_under_what_it_brought(self):
        spec = E.describe("milestones", ELEMENTS["history"])
        for night in (False, True):
            p, pixels = sprites(lambda: SET.milestones(spec, night), "release", "today_mark")
            self.assertEqual(off_words(p, pixels, margin=1), [], night)


class Badges(unittest.TestCase):
    def test_a_brass_rim_lies_along_every_badges_top_row_with_the_letters_under_it(self):
        for style in BADGE_STYLES:
            drawn = [SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                       SET.badge_states()["green"])]
            drawn += [SET.plate_badge(style, "License", "MIT", "scale", mode) for mode in ("day", "night")]
            for p in drawn:
                top = {c for (x, y), c in p.layers["base"].items() if y == 0}
                self.assertEqual(top, {BRASS[5]}, style)
                self.assertTrue(all(y >= TOP for _, _, _, y, _ in p.uses["base"]), "the letters sit under the rim")


# The drawers of every header, wide and on a phone, by their code.
HEADERS = {("H1", True): lambda held: held.h1, ("H2", True): lambda held: held.h2, ("H3", True): lambda held: held.h3,
           ("H1", False): lambda held: held.h1_narrow, ("H2", False): lambda held: held.h2_narrow,
           ("H3", False): lambda held: held.h3_narrow}


def header(held, code, wide, h, night) -> Pix:
    """One header's drawing as `held` draws it, a wide one moving."""
    draw = HEADERS[(code, wide)](held)
    return draw(h, night, True) if wide else draw(h, night)


def cells_of(art: list, pal: dict, letters: str) -> set:
    """The colours `pal` paints the letters `letters` of character art `art` in."""
    return {pal[ch] for row in art for ch in row if ch in letters and pal.get(ch)}


class Hand(unittest.TestCase):
    """The set is drawn in the medieval collection's hand: it keeps to it as September's design and kept all year,
    its words are in the hand's inks on a wall within the hand's bands, every flame burns the hand's flame while
    the elixirs glow their own colours, the moon through the window is the hand's, its people are on the hand's
    skin, its glint and its slow drift keep the hand's time, nothing of its laboratory enters the top centre kept
    for the month's mark, and its composition stands to the hand's measure."""

    def test_it_keeps_to_its_hand_as_septembers_design_and_kept_all_year(self):
        self.assertEqual(check(HELD), [])
        self.assertEqual(check(SET), [])
        self.assertEqual((HELD.collection, HELD.month), ("medieval", 9))

    def test_its_words_are_in_the_hands_inks_on_a_wall_in_its_bands(self):
        """Its words and its quieter words are set in the hand's two inks, by day and by night, and so are a link's
        letters on their paper label; the limewashed wall behind them is in the hand's band by day, a touch under
        its brightest, and by night every band of the dark wall is in the night's."""
        for night in (False, True):
            k = SET.ink(night)
            self.assertEqual((k["body"], k["muted"]), (MEDIEVAL.body[night], MEDIEVAL.muted[night]), night)
        self.assertEqual(SET.link_colours(False)[2], MEDIEVAL.body[0], "a link's letters")
        light, chroma, hue = lab(C["paper"])
        lo, hi, most = MEDIEVAL.day_ground
        self.assertTrue(lo <= light <= hi and chroma <= most, (light, chroma))
        self.assertGreater(light, hi - 1, "a limewashed wall, only a touch under the band's brightest")
        self.assertEqual(C["paper"], RAMP["lime"][5])
        lo, hi, most = MEDIEVAL.night_ground
        for band in A.NIGHT_SKY:
            light, chroma, _ = lab(band)
            self.assertTrue(lo <= light <= hi and chroma <= most, (band, light, chroma))

    def test_every_flame_burns_on_the_hands_flame_and_the_elixirs_glow_their_own(self):
        """The furnace's fire, the candles, the lantern's candle, the crucible's lamp and the spirit lamp under the
        retort all burn on the hand's flame ramp, by day and by night, wide and on a phone; the elixirs' green and
        violet glows stay their own colours, for they are not flames."""
        flame = set(MEDIEVAL.ramp("flame"))
        self.assertEqual(RAMP["fire"], MEDIEVAL.ramp("flame"))
        h, f = contents(KEY)["kit"]
        burned = set()
        for code in ("H1", "H2", "H3"):
            for night in (False, True):
                p = header(HELD, code, True, h, night)
                burning = {c for L in layers_named(p, "fl") for c in p.layers[L].values()}
                self.assertLessEqual(burning, flame, (code, night, "the flames that flicker"))
                burned |= burning
                if night and code != "H3":
                    glows = {a["fill"] for (_, _, a, _) in overlays(p)} & {GREEN[5], VIOLET[5]}
                    self.assertTrue(glows, (code, "the elixirs glow their own green and violet"))
        self.assertFalse({GREEN[5], VIOLET[5]} & flame)
        self.assertIn(FIRE[6], burned, "a flame burns white-hot by night")
        q = Pix(40, 40)
        A.crucible(q, 4, 36, True)
        fire = set(q.layers["base"].values()) & (flame | set(RAMP["blue"]))
        self.assertTrue(fire and fire <= flame, "the crucible's lamp")
        for night in (False, True):
            q = Pix(40, 40)
            A.retort(q, 10, 36, night, motion=False)
            fy = 36 - len(A.TRIPOD) + 5
            lamp = {q.get(16 + dx, fy + dy) for dx, dy, _ in A.SPIRIT}
            self.assertLessEqual(lamp, flame if night else flame - {FIRE[6]}, (night, "the spirit lamp's flame"))

    def test_its_moon_is_the_hands(self):
        """By night a sliver of the hand's moon shows through the round window among the stars."""
        p = Pix(40, 40)
        A.window(p, 20, 20, 11, True, motion=False)
        moon = {c for c in p.layers["base"].values() if c in MEDIEVAL.ramp("moon")}
        self.assertTrue(moon)
        q = Pix(40, 40)
        A.window(q, 20, 20, 11, False, motion=False)
        self.assertFalse({c for c in q.layers["base"].values() if c in MEDIEVAL.ramp("moon")}, "no moon by day")

    def test_its_people_are_on_the_hands_skin(self):
        """The alchemist's face and his hand, the small alchemist's and the homunculus's are on the hand's lightest
        skin, and the roster's alchemists on one of the hand's three, each drawn from his name; a face in the roster
        keeps its tones by night."""
        skins = [MEDIEVAL.ramp(f"skin{i}") for i in range(3)]
        self.assertEqual((RAMP["skin"], RAMP["skin1"], RAMP["skin2"]), tuple(skins))
        for night in (False, True):
            p = Pix(60, 60)
            A.alchemist(p, 4, 4, night)
            face = {c for c in p.layers["base"].values() if c in skins[0]}
            self.assertGreaterEqual(len(face), 3, (night, "his face and his hand"))
            self.assertFalse({c for c in p.layers["base"].values() for r in skins[1:] if c in r}, night)
            q = Pix(30, 30)
            A.small_alchemist(q, 2, 2, night)
            self.assertTrue({c for c in q.layers["base"].values() if c in skins[0]}, (night, "the small alchemist"))
            q = Pix(30, 40)
            A.homunculus(q, 15, 20, night)
            self.assertTrue({c for c in q.layers["base"].values() if c in skins[0]}, (night, "the homunculus"))
        worn = set()
        for name in ("Imogen Vale", "Tomas Okafor", "Wren Castellan", "Ada", "Jabir", "Roger", "Maria", "Hermes"):
            faces = []
            for night in (False, True):
                q = Pix(20, 30)
                A.alchemist_head(q, 9, 14, {"name": name, "initials": name[:2]}, 0, night)
                faces.append({c for c in q.layers["base"].values() if any(c in r for r in skins)})
            self.assertEqual(faces[0], faces[1], (name, "the same face by night"))
            ramps = [i for i, r in enumerate(skins) if faces[0] <= set(r)]
            self.assertEqual(len(ramps), 1, (name, faces[0]))
            worn.add(ramps[0])
        self.assertEqual(worn, {0, 1, 2}, "the roster's alchemists wear all three of the hand's skins")

    def test_its_glint_and_its_drift_keep_the_hands_time(self):
        """A title's glint passes on the hand's period; the dust drifts down the shaft of sun on a slow sweep of
        the hand's; the flames flicker and the glints twinkle on the engine's cadences; and the laboratory's beat,
        its bubbles, drops, sand and sparks, keeps its own quick step."""
        moving = SET.header("H1", HEADER, DAY, True, True)
        glint = re.search(r'keyTimes="0;\.3;1" dur="([\d.]+)s"', moving)
        self.assertEqual(float(glint.group(1)), MEDIEVAL.glint)
        drift = re.search(r'<g clip-path="url\(#sb\d+\)"><g>.*?dur="([\d.]+)s"', moving)
        self.assertTrue(24 <= float(drift.group(1)) <= 48)
        cadences = {v[2] for v in BLINKS.values()}
        for theme in (DAY, DARK):
            for code in ("H1", "H2", "H3"):
                svg = HELD.header(code, HEADER, theme, True, True)
                for attrs in re.findall(r'<animate(?:Transform)? ([^>]*)/>', svg):
                    dur = float(re.search(r'dur="([\d.]+)s"', attrs).group(1))
                    self.assertTrue(dur in cadences | {MEDIEVAL.glint, A.BEAT} or 24 <= dur <= 48,
                                    (code, theme["name"], attrs))

    def test_nothing_of_the_laboratory_enters_the_top_centre_with_the_mark_or_without_it(self):
        """In every header, wide and on a phone, by day and by night, for every shared content, as September's design
        and kept all year, nothing its scenes, the vessels on the top shelf and the marks beside its title draw lies
        in the box the month's mark is drawn in or the two units round it, but the shelf the mark hangs over."""
        hooks = ("scene", "scene_narrow", "scene_under", "garland", "section_mark", "strip_mark")
        n = MEDIEVAL.mark_size
        for name, (h, _) in contents(KEY).items():
            for held in (HELD, SET):
                for (code, wide) in HEADERS:
                    for night in (False, True):
                        p, pixels = sprites(lambda: header(held, code, wide, h, night), *hooks, held=held)
                        x0, x1 = A.top_centre(p.w)
                        y0, y1 = MARK_Y - n // 2 - 2, MARK_Y - n // 2 + n + 2
                        inside = sorted((x, y) for (x, y) in pixels if x0 <= x < x1 and y0 <= y < y1
                                        and not A.SHELF <= y < A.SHELF + A.BOARD)
                        self.assertEqual(inside[:4], [], (name, held.day, code, wide, night))

    def test_its_composition_stands_to_the_hands_measure(self):
        """A wide H1 stands a scene on each side of its words, the alchemist at the left and the still at the
        right, each rising from the bench at least seven tenths of the way to the shelf over it (but the still of
        the least a page can say, whose header is the kit's shortest, which stands without its shelf of
        instruments); a wide H2's still rises its slot's full height beside the words; a wide H3's great sphere
        rises the strip's full height, or sixty rows where the strip is taller; and a phone's H1 builds its
        laboratory at least 48 rows tall, its H2 and H3 theirs at least 44 under their words (see `Phones`)."""
        top = A.SHELF + A.BOARD
        for name in ("kit", "repository", "profile", "least"):
            h, _ = contents(KEY)[name]
            p, pixels = sprites(lambda: HELD.h1(h, False, False), "scene", held=HELD)
            foot = max(y for _, y in pixels)
            words = [b for b in p.words if b[1] < foot]
            sides = ([y for (x, y) in pixels if x < min(b[0] for b in words) - 2],
                     [y for (x, y) in pixels if x > max(b[2] for b in words) + 2])
            for side, ys in zip(("left", "right"), sides):
                if name != "least" or side == "left":
                    self.assertGreaterEqual((foot - min(ys)) / (foot - top), 0.7, (name, side))
            p, pixels = sprites(lambda: HELD.h2(h, False, False), "scene", held=HELD)
            foot = max(y for _, y in pixels)
            self.assertGreaterEqual((foot - min(y for _, y in pixels)) / (foot - top), 0.8, (name, "the still"))
            p, pixels = sprites(lambda: HELD.h3(h, False, False), "scene", held=HELD)
            foot = max(y for _, y in pixels)
            self.assertGreaterEqual(foot - min(y for _, y in pixels), min(foot - top - 2, 60), (name, "the sphere"))
            p, pixels = sprites(lambda: HELD.h1_narrow(h, False), "scene_narrow", held=HELD)
            ys = [y for _, y in pixels]
            self.assertGreaterEqual(max(ys) - min(ys) + 1, 48, (name, "the phone's laboratory"))


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
        """The kit's own lines, the samples and the least a page can say come out as the kit draws them at full
        weight, with their motion and, drawn as September's design, the month's mark, at least 1,500 bytes under
        their budgets, so a longer profile keeps everything too; only the most a page can say is drawn lighter."""
        for name, (h, f) in contents(KEY).items():
            if name == "most":
                continue
            for theme in (DAY, DARK):
                for code in ("H1", "H2", "H3"):
                    for wide, motion in ((True, True), (True, False), (False, False)):
                        what = (name, code, theme["name"], wide, motion)
                        svg, made, _ = drawn_pieces(lambda: HELD.header(code, h, theme, wide, motion), held=HELD)
                        self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"] - 1500, what)
                        self.assertFalse(any(q.lite for q in made), what)
                        self.assertEqual("<animate" in svg, wide and motion, what)
                        self.assertIn(zodiac.LAPIS[3], svg, (what, "the month's mark"))
                for code in ("F1", "F2"):
                    for wide in (True, False):
                        svg, made, _ = drawn_pieces(lambda: SET.footer(code, f, theme, wide, False))
                        self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["footer"] - 1500, (name, code, wide))
                        self.assertFalse(any(q.lite for q in made), (name, code, wide))

    def test_text_colours_hold_4_5_on_the_paper_and_every_row_of_the_night(self):
        for night in (False, True):
            k = SET.ink(night)
            p = Pix(415, 200)
            grounds = {SET.bg_at(p, night, y) for y in range(p.h)}
            for role in ("title", "body", "muted", "accent"):
                for ground in grounds:
                    self.assertGreaterEqual(contrast(k[role], ground), 4.5, (night, role, ground))
            self.assertGreaterEqual(contrast(k["tag_ink"], k["tag"]), 4.5, (night, "tag"))
            fill, _, ink, _ = SET.link_colours(night)
            self.assertGreaterEqual(contrast(ink, fill), 4.5, (night, "a link's letters on its label"))
            self.assertGreaterEqual(contrast(k["tag_ink"], GREEN[5]), 4.5, (night, "the ribbon's silk"))

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
        families = {"red": PALETTE["red"], "orange": PALETTE["orange"], "yellow": PALETTE["yellow"],
                    "green": PALETTE["green"], "blue": PALETTE["blue"], "purple": PALETTE["purple"],
                    "white": PALETTE["white"], "dark": PALETTE["black"], "grey": PALETTE["slate"],
                    "brown": PALETTE["brown"]}
        taken = {family: nearest(hexc, swatches) for family, hexc in families.items()}
        self.assertEqual(len(set(taken.values())), len(taken), ("each family its own swatch", taken))

    def test_what_the_sets_letters_cannot_draw_is_left_to_the_kit(self):
        self.assertIsNone(self.badge("flat", message="中文"))


if __name__ == "__main__":
    unittest.main()
