# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Mosaic set's own rules, which the checks every set shares cannot know: what the night alone shows (the lapis
vault and its gold stars, the lamps' flames, the glow round them and the warm pools they throw, and the light they
lay on what hangs and stands near them) stays out of the day's files, and the gold ground's glitter out of the
night's; in a moving header a sheen crosses the gold by day, under the field behind every word, and by night the
tiles by each lamp glint instead; every small word keeps 4.5:1 with the lamps' light on the ground round it; a title
is built tile by tile in tesserae with their grout, deep blue on gold by day and gold on blue by night, and a glint
runs through it tile by tile only in a wide moving header; the garland is the running wave scroll laid in tesserae,
never a row of dots, its crests catching the light only in a wide moving header; an H1 is the apse, its two peacocks
drinking from the fountain under the arch with the vine and its grapes behind them and a lamp crown over them, the
birds taking turns to drink, the fountain sparkling and the eyes of their trains glinting in a moving header, and
beyond it the palace's arcade with the empress in its middle arch in her crown and her pearls, her jewelled collar
and her purple, holding her bowl of gold, and her ladies in patterned silks either side, all with the mosaic's large
dark eyes, and the procession of her court between them where the words leave it room, coming to the palace's door
with its curtain drawn aside and its fountain where the words leave the palace's height clear, setting out from the
gate of the port, its lighthouse, ships and city standing between the apse and the title where the rows allow; an H2
is the peacock drawn larger, the fan of its crest over its head and its tail half open, the light crossing its fan's
eyes in turn in a moving header, the port beyond it where there is room; an H3 is the fountain with its doves under a
lamp crown with as much of its court as the words leave room for, a peacock facing it or a pair either side of it
with their trains trailing, and where the band runs wide the vine's peopled scroll beside them, its birds pecking at
its grapes under oil lamps lit by night; the peacocks' heads stay under the apse's arch and a lamp's light inside the
walls it hangs in; every phone header of every shared content stands a scene, beside its words where they leave it
room and else under them; every scene, the scroll, the marks beside a title and the vine along a rule keep two units
from every word, on a phone and across a wide header; the most a page can say keeps its whole scene and its motion
within the budget, a drawing made lighter keeping every piece where it stood, and ordinary content is drawn at full
weight with room to spare; a footer stands on the floor mosaic, its guilloche and where a cell leaves room its opus
sectile, a row clear of every word, and wherever the cells leave room the doves of Pliny drink at their bowl, two
units clear of every word, their oil lamp beside them or over them, lit by night; a link is a marble plaque, a small
file; a schematic's card is a marble plaque in a rim of gold tesserae; the histogram's columns are stacked tesserae
with marble capitals; the dial is a gold sun disc, its hand the gnomon's shadow; the seal is a porphyry roundel, its
check laid in gold tesserae; a placard is a marble panel inlaid with cut stones; the roster's avatars are portraits
in mosaic, never initials; the time line is the vine, with grapes at the releases and a peacock at today; a counter's
numerals hold 4.5:1 on their marble; and a rim of gold tesserae lies along every badge's top with the letters under
it. It keeps to the medieval collection's hand as August's design and kept all year: its words in the hand's inks,
its gold burnished and its lapis quiet within the hand's bands, its lamps on the hand's flame, its court on the
hand's skins, the mark's box clear of every scene and star with a crest of the scroll whole under it, its heroes at
the composition's measure and its motion on the hand's times. The set is a theme, not a holiday on the calendar, so
the checks every registered set shares run here over the set directly, with the same contents and the same entry
points."""
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
from domain.holidays.designs import Holiday
from domain.holidays.designs.badges import PLATE, STATES, STYLES as BADGE_STYLES, inside, nearest
from domain.collections.medieval_mosaic import SET
from domain.collections.medieval_mosaic import art as A
from domain.collections.medieval_mosaic.palette import CALM, NIGHT_SKY, RAMP, X
from domain.collections.hand import CollectionSet, check, lab
from domain.holidays.designs.banners import MARK_Y
from domain.holidays.pixel import Pix, contrast
from domain.palette import PALETTE

support.install()
KEY = SET.key
HEADER = Header(tone="standard", holiday=KEY)
GOLD, LAPIS, FLAME, PEARL = RAMP["gold"], RAMP["lapis"], RAMP["flame"], RAMP["pearl"]
ITS_DAY = dt.date(2026, 8, 1)     # a day in August, which makes the Mosaic the collection's design for the month


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


# A block laid in a pattern (the scroll, the floor, the shaft of the fountain): what `sprites` reads to know which
# cells it covers.
RECT = re.compile(r'<rect x="(-?\d+)" y="(-?\d+)" width="(\d+)" height="(\d+)"')


def sprites(draw, *hooks) -> tuple:
    """`draw()`'s drawing, and every pixel of the sprites the set's `hooks` (names of its drawing hooks) put on it,
    gathered as they draw: their pixels on every layer, the cells of the symbols they place, the blocks they lay in
    a pattern and the cells of what they draw once and place twice (which the set keeps in the drawing's `filled`).
    Only what lands on the drawing returned counts, not on one a phone laid out first and laid out again."""
    found, cells = {}, {}
    symbol = Pix.symbol

    def kept(self, key, cells_=None, shapes="", mono=False):
        sid = symbol(self, key, cells_, shapes, mono)
        cells.setdefault(sid, set(cells_ or ()))
        return sid

    def watched(hook):
        def drawn(*args, **kw):
            p = next(a for a in args if isinstance(a, Pix))
            pixels = found.setdefault(id(p), (p, set()))[1]
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
    return p, found.get(id(p), (p, set()))[1]


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
    """The calls a spied art function made on the sheet `p` itself, not on the scratch sheets a scene draws its
    halves and its stagings on."""
    return [c for c in spy.call_args_list if c.args and c.args[0] is p]


def drawn_pieces(draw, held=SET) -> tuple:
    """`draw()`'s result and every canvas the set made for it, in turn: the set as `held`, the set itself or the
    set held for a day (see `Holiday.on`)."""
    made = []
    canvas = held.canvas

    def kept(*args, **kw):
        p = canvas(*args, **kw)
        made.append(p)
        return p
    with mock.patch.object(held, "canvas", kept):
        out = draw()
    return out, made


def layers_named(p: Pix, *prefixes) -> list:
    """The layers of `p` whose names begin with one of `prefixes` and that have something on them."""
    return [L for L in p.layers if L.startswith(prefixes) and (p.layers[L] or p.uses[L] or p.shapes[L])]


def glitter(p: Pix) -> set:
    """The tiles of the gold that glitter on `p`: the light thrown back at the corner of each, on the twinkling
    layers behind the drawing."""
    return {xy for L in layers_named(p, "tb") for xy, c in p.layers[L].items() if c == X["glint"]}


def moving(p: Pix) -> tuple:
    """What moves on `p`, by kind: each layer that moves and has something on it, by its name less its number and
    by how it moves, and how many pieces of its own markup move."""
    kinds = {(L.rstrip("0123456789"), p.meta[L][2][0]) for L in p.layers
             if p.meta[L][2] and (p.layers[L] or p.shapes[L] or p.uses[L])}
    return kinds, sum("<animate" in m for (_, _, m, _) in p.raws)


# The see-through light laid on a drawing: its pools and glows, each placed from the rings a file keeps once.
TAG = re.compile(r'<(/?)(g|use)\b([^>]*?)(/?)>')
ATTR = re.compile(r'([a-z-]+)="([^"]*)"')
PLACED = re.compile(r"translate\(([-\d.]+) ([-\d.]+)\) scale\(([-\d.]+) ([-\d.]+)\)$")


def overlays(p: Pix) -> list:
    """Every pool and glow laid on `p`, as (z, cx, cy, rx, ry, fill, opacity) for each of its rings, in the order
    they are drawn."""
    rings = {}
    for d in p.defs:
        m = re.match(r'<g id="([^"]+)">((?:<circle [^>]*/>)+)</g>$', d)
        if m:
            rings[m.group(1)] = [(float(r), float(a)) for r, a in
                                 re.findall(r'<circle r="([^"]+)" fill-opacity="([^"]+)"/>', m.group(2))]
    found = []
    for name, shapes in p.shapes.items():
        for close, kind, attrs, _ in TAG.findall("".join(shapes)):
            a = dict(ATTR.findall(attrs))
            m = PLACED.match(a.get("transform", ""))
            if close or kind != "use" or not m:
                continue
            cx, cy, rx, ry = (float(v) for v in m.groups())
            for reach, opacity in rings.get(a.get("href", "")[1:], ()):
                found.append((p.meta[name][0], cx, cy, rx * reach, ry * reach, a["fill"], opacity))
    return sorted(found, key=lambda t: t[0])


def _blend(c: tuple, top: str, a: float) -> tuple:
    t = [int(top[i:i + 2], 16) for i in (1, 3, 5)]
    return tuple(round(c[i] * (1 - a) + t[i] * a) for i in range(3))


def _rgb(c: str) -> tuple:
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def worst_words(p: Pix, night: bool, inks: list) -> list:
    """For each small word set on `p` (`inks`, as `lettered` keeps them), the lowest contrast its colour holds
    over its box: on the even field the tiles calm to behind it (by night the band lifted to the tiles' mean),
    under every pool and glow laid over that field."""
    shapes = overlays(p)
    base = p.layers["base"]
    worst = []
    for (x0, y0, x1, y1), ink in inks:
        low = 99.0
        for y in range(y0 + 1, y1 - 1):
            for x in range(x0 + 1, x1 - 1, 2):
                under = base.get((x, y))
                g = _rgb(under) if under else _rgb(SET.bg_at(p, night, y))
                if not under and night and not p.lite:
                    g = _blend(g, A.LIFT, A.CALM_LIFT)
                fg = _rgb(ink)
                for (z, cx, cy, rx, ry, fill, a) in shapes:
                    if rx > 0 and ry > 0 and ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1:
                        g = _blend(g, fill, a)
                        if z > 0:
                            fg = _blend(fg, fill, a)
                low = min(low, contrast("#%02X%02X%02X" % fg, "#%02X%02X%02X" % g))
        worst.append(((x0, y0, x1, y1), ink, round(low, 2)))
    return worst


def lettered(draw) -> tuple:
    """`draw()`'s drawing, and the box and colour of every line it set in small letters (titles, laid in their own
    tesserae, are left to the checks on the inks), on the drawing returned."""
    inks = []
    text = Pix.text

    def kept(self, x, y, s, c, font="57", scale=1, *args, **kw):
        w = text(self, x, y, s, c, font, scale, *args, **kw)
        if scale == 1 and s.strip():
            inks.append((self, self.words[-1], c))
        return w
    with mock.patch.object(Pix, "text", kept):
        p = draw()
    return p, [(box, c) for q, box, c in inks if q is p]


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


class Night(unittest.TestCase):
    def test_what_the_night_alone_shows_stays_out_of_the_day_and_the_glitter_out_of_the_night(self):
        """The vault's lapis and its gold stars, the lamps' flames, the glow round them and their warm pools are the
        night's; the gold ground is the day's, and its tiles glitter only in a day's moving header, twinkling behind
        the drawing as the stars do by night."""
        for code in ("H1", "H2", "H3"):
            draw = getattr(SET, code.lower())
            for motion in (True, False):
                day, night = draw(HEADER, False, motion), draw(HEADER, True, motion)
                what = (code, motion)
                day_svg, night_svg = day.svg("t", "d", still=not motion), night.svg("t", "d", still=not motion)
                self.assertNotIn(FLAME[6], day_svg, (what, "a lamp burning"))
                self.assertIn(FLAME[6], night_svg, (what, "the lamps burn by night"))
                self.assertNotIn(NIGHT_SKY[2], day_svg, (what, "the vault"))
                self.assertIn(NIGHT_SKY[2], night_svg, (what, "the vault"))
                self.assertIn(A.TILE[3], day_svg, (what, "the gold ground"))
                self.assertFalse(layers_named(day, "st", "fl", "fb", "haze"), (what, "stars or light by day"))
                self.assertFalse(any(day.uses[L] for L in layers_named(day, "tb")), (what, "no stars by day"))
                self.assertTrue(layers_named(night, "st", "tb"), (what, "the vault's stars"))
                self.assertTrue(layers_named(night, "fl") and layers_named(night, "fb", "haze"),
                                (what, "the flames, their glow and their pools"))
                self.assertFalse(glitter(night), (what, "no glitter by night"))
                self.assertEqual(bool(glitter(day)), motion, (what, "the gold glitters when it moves"))
                self.assertTrue(all(day.meta[L][2][0] == "twinkle" for L in layers_named(day, "tb")), what)
                self.assertEqual(day.lamps, [], (what, "nothing lit by day"))

    def test_a_sheen_crosses_the_gold_by_day_and_the_tiles_by_each_lamp_glint_by_night(self):
        """In a moving header by day a slow sheen crosses the gold: the ground's tiles lit as the light finds them,
        drawn once as a pattern of the ground's own courses and seen through a slanting window that travels the
        sheet, laid under the even field behind every word, crossing once in a slow sweep of the hand's. By night the
        tiles nearest each lamp glint in its light instead, warm, a few at a time, twinkling behind the drawing as the
        stars do, two units clear of every word. A still file has neither."""
        for code in ("H1", "H2", "H3"):
            draw = getattr(SET, code.lower())
            for motion in (True, False):
                day, night = draw(HEADER, False, motion), draw(HEADER, True, motion)
                what = (code, motion)
                sheen = [i for i, u in enumerate(day.under) if 'fill="url(#sh)"' in u]
                self.assertEqual(len(sheen), 1 if motion else 0, (what, "the sheen by day"))
                if sheen:
                    self.assertIn('<animateTransform attributeName="transform" type="translate"', day.under[sheen[0]])
                    self.assertIn(f'dur="{A.SHEEN_BEAT:g}s"', day.under[sheen[0]])
                    self.assertTrue(24 <= A.SHEEN_BEAT <= 48, "as slow as the hand's sweeps")
                    calmed = [i for i, u in enumerate(day.under) if f'fill="{CALM}"' in u]
                    self.assertTrue(calmed and sheen[0] < min(calmed), (what, "under the field behind the words"))
                self.assertFalse(any('url(#sh)' in u for u in night.under), (what, "no sheen by night"))
                glints = {xy for L in layers_named(night, "tb") for xy, c in night.layers[L].items() if c == FLAME[6]}
                self.assertEqual(bool(glints), motion, (what, "the lamps' tiles glint by night"))
                self.assertFalse(any(c == FLAME[6] for L in layers_named(day, "tb") for c in day.layers[L].values()))
                self.assertEqual(off_words(night, glints), [], what)
                for (x, y) in glints:
                    self.assertTrue(any(math.hypot(x - cx, y - cy) <= r for (cx, cy, r, *_) in night.lamps), what)

    def test_a_lamps_light_falls_on_what_stands_near_it_inside_the_walls_it_hangs_in(self):
        """By night every flame lays its warm light into the colours of what hangs and stands near it, the birds, the
        vine, the marble, the court's faces and robes; the apse's crown keeps its light inside the apse and the
        palace's lamps theirs inside the palace, so the procession between them walks unlit."""
        least, _ = contents(KEY)["least"]
        for draw in (lambda: SET.h1(least, True, True), lambda: SET.h1_narrow(least, True)):
            with mock.patch.object(A, "lamplight") as unlit:
                dark = draw()
            self.assertTrue(unlit.called)
            with mock.patch.object(A, "procession", wraps=A.procession) as walk:
                lit = draw()
            changed = {xy for xy, c in lit.layers["base"].items() if dark.layers["base"].get(xy) != c}
            self.assertGreater(len(changed), 100, "the lamps light what stands near them")
            _, a, b, *_ = drawn_on(lit, walk)[0].args
            self.assertEqual({xy for xy in changed if a <= xy[0] < b}, set(), "the procession walks unlit")

    def test_every_small_word_holds_4_5_with_the_lamps_light_on_the_ground_round_it(self):
        """The lamps' pools and the glow round their flames fall on the ground round the words as well as on the
        scenes: every line set in small letters keeps 4.5:1 over all of it, on every header, phone and footer the
        shared contents draw by night."""
        drawers = [("H1", lambda h, f: SET.h1(h, True, True)), ("H2", lambda h, f: SET.h2(h, True, True)),
                   ("H3", lambda h, f: SET.h3(h, True, True)), ("H1n", lambda h, f: SET.h1_narrow(h, True)),
                   ("H2n", lambda h, f: SET.h2_narrow(h, True)), ("H3n", lambda h, f: SET.h3_narrow(h, True)),
                   ("F1", lambda h, f: SET.f1(f, True)), ("F2", lambda h, f: SET.f2(f, True)),
                   ("F1n", lambda h, f: SET.f1_narrow(f, True)), ("F2n", lambda h, f: SET.f2_narrow(f, True))]
        for name, (h, f) in contents(KEY).items():
            for code, draw in drawers:
                p, inks = lettered(lambda: draw(h, f))
                low = [w for w in worst_words(p, True, inks) if w[2] < 4.5]
                self.assertEqual(low[:3], [], (name, code))


class Titles(unittest.TestCase):
    def test_a_title_is_laid_tile_by_tile_in_tesserae_with_their_grout(self):
        """A title's letters are laid in a pattern of tiles a font pixel each, in deep blues by day and golds by night,
        over the grout they are set in; by day a course of bright gold tiles hugs each letter, and by night the gold
        glows on the blue."""
        for night in (False, True):
            p = SET.h1(HEADER, night, False)
            defs, markup = "".join(p.defs), "".join(m for (_, _, m, _) in p.raws)
            pid = re.search(r'stroke="url\(#(tt\d[dn])\)"', markup)
            self.assertTrue(pid, night)
            self.assertEqual(pid.group(1)[-1], "n" if night else "d")
            tile = re.search(rf'<pattern id="{pid.group(1)}" width="5" height="7"[^>]*>(.*?)</pattern>', defs).group(1)
            ramp = GOLD if night else LAPIS
            tones = set(re.findall(r'(?:stroke|fill)="(#[0-9A-F]{6})"', tile))
            self.assertTrue(len(tones) >= 3 and tones <= set(ramp), (night, "tiles of one ramp's tones"))
            grout = GOLD[1] if night else LAPIS[0]
            self.assertIn(f'stroke="{grout}"/><use href="#', markup, (night, "the grout under the tiles"))
            hug = f'<g stroke="{GOLD[4]}" stroke-opacity=".28"' if night else f'<g stroke="{A.TILE[6]}"'
            self.assertIn(hug, markup, (night, "the glow by night, the gold course by day"))

    def test_a_glint_runs_through_the_title_only_in_a_wide_moving_header(self):
        for code in ("H1", "H2", "H3"):
            for theme in (DAY, DARK):
                moving = SET.header(code, HEADER, theme, True, True)
                self.assertRegex(moving, r'<clipPath id="gc\d+"><path d="[^"]*" transform="scale\(\d\)">'
                                         r'<animateTransform', (code, theme["name"]))
                self.assertIn('url(#tg', moving)
                for wide, motion in ((True, False), (False, False)):
                    self.assertNotIn('id="gc', SET.header(code, HEADER, theme, wide, motion), (code, wide, motion))

    def test_the_title_and_every_word_hold_4_5_on_the_field_the_tiles_calm_to(self):
        """Every tone a title's tiles take holds 4.5:1 on the even field the ground calms to behind it, by day on the
        gold and by night on every band of the vault lifted to the tiles' mean."""
        for night in (False, True):
            grounds = {CALM} if not night else {NIGHT_SKY[i] for i in range(len(NIGHT_SKY))}
            if night:
                grounds |= {"#%02X%02X%02X" % _blend(_rgb(c), A.LIFT, A.CALM_LIFT) for c in NIGHT_SKY}
            tones = {A._tile_fill(r, c, s, night) for s in (2, 3, 4) for r in range(7 * s) for c in range(5 * s)}
            tones -= {GOLD[1], LAPIS[0]}
            for tone in tones:
                for ground in grounds:
                    self.assertGreaterEqual(contrast(tone, ground), 4.5, (night, tone, ground))


class Scroll(unittest.TestCase):
    def test_the_garland_is_the_running_wave_scroll_never_a_row_of_dots(self):
        """Along every header's top the wave runs in a pattern of tesserae, in two blues on white between lines of
        gold tiles, from corner stone to corner stone; its crests catch a light that runs along them only in a wide
        moving header."""
        for code in ("H1", "H2", "H3"):
            for theme in (DAY, DARK):
                for wide, motion in ((True, True), (True, False), (False, False)):
                    svg = SET.header(code, HEADER, theme, wide, motion)
                    what = (code, theme["name"], wide, motion)
                    w = 415 if wide else 180
                    self.assertIn(f'<rect x="7" y="2" width="{w - 14}" height="10" fill="url(#wsw)"/>', svg, what)
                    for pid in ("wsa", "wsb"):
                        self.assertIn(f'fill="url(#{pid})"', svg, what)
                    self.assertEqual('fill="url(#wsl)"' in svg, wide and motion, what)
        tile = A._wave_cells(False)
        self.assertEqual(len(tile), A.WAVE_W * A.WAVE_H, "a whole tile, white between the blues, no gaps")
        self.assertEqual({c for c in tile.values()} & set(PEARL), {PEARL[5], PEARL[6]})


class Scenes(unittest.TestCase):
    def test_the_apse_has_its_peacocks_drinking_by_turns_at_the_fountain_under_the_lamp_crown(self):
        """An H1's apse stands its two peacocks on the rim of the fountain, the vine and its grapes behind them and the
        lamp crown over them; in a moving header they take turns to drink, an idle of the hand's length, the jet's
        drops sparkle as they fall and the eyes of their trains twinkle, and a still one keeps one drinking and one
        with its head up."""
        p = SET.h1(HEADER, False, True)
        kinds, _ = moving(p)
        self.assertLessEqual({("turn", "seq"), ("jet", "seq"), ("tw", "twinkle")}, kinds)
        self.assertEqual({p.meta[L][2][3] for L in layers_named(p, "turn")}, {A.TURN})
        self.assertTrue(4 <= A.TURN <= 8, "the birds idle on the hand's loop")
        still = SET.h1(HEADER, False, False)
        self.assertFalse({k for k, _ in moving(still)[0]} & {"turn", "jet", "tw"})
        for draw in (lambda: SET.h1(HEADER, False, True), lambda: SET.h1(HEADER, False, False)):
            with mock.patch.object(A, "peacock_neck", wraps=A.peacock_neck) as neck:
                q = draw()
            poses = sorted(c.args[5] for c in drawn_on(q, neck))
            self.assertIn("down", poses)
            self.assertIn("up", poses)
        svg = p.svg("t", "d")
        for c, what in ((RAMP["purple"][3], "the grapes"), (RAMP["teal"][4], "the trains"),
                        (RAMP["bronze"][4], "the lamp crown")):
            self.assertIn(c, svg, what)

    def test_the_peacocks_heads_stay_under_the_arch_of_the_apse(self):
        """However few rows the words leave the apse, on a phone as on a wide header, the basin stands low enough that
        both birds' heads, raised or bent to drink, lie inside the niche under its arch."""
        for name, (h, _) in contents(KEY).items():
            for draw in (lambda: SET.h1(h, False, True), lambda: SET.h1_narrow(h, False)):
                with mock.patch.object(A, "apse", wraps=A.apse) as apse, \
                        mock.patch.object(A, "peacock_neck", wraps=A.peacock_neck) as neck:
                    p = draw()
                (_, x0, x1, top, foot, *_), _ = drawn_on(p, apse)[0]
                _, niche = A._niche_cells(x0, x0 + (x1 - x0) // 2 * 2, top, foot)
                for c in drawn_on(p, neck):
                    _, x, perch, _, face, pose, *_ = c.args
                    art = A.NECK_UP if pose == "up" else A.NECK_DOWN
                    cells = A.cells_of(A.flip(art) if face == -1 else art, x, perch - A.PEACOCK_H + 1)
                    self.assertEqual(cells - niche, set(), (name, p.w, pose))

    def test_the_palace_holds_the_court_with_a_lamp_in_each_arch_and_the_procession_where_there_is_room(self):
        """Beyond the apse the palace's arcade of three bays holds the empress in her purple and a lady either side,
        its curtains drawn back, a lamp hung in each arch; where the words leave rows enough between them the
        empress's court walks in procession toward the palace, each figure in its robe and jewelled collar. Where a
        title runs close, the bays narrow a column rather than come near it."""
        for name, (h, _) in contents(KEY).items():
            with mock.patch.object(A, "palace", wraps=A.palace) as palace, \
                    mock.patch.object(A, "figure", wraps=A.figure) as figure, \
                    mock.patch.object(A, "hanging_lamp", wraps=A.hanging_lamp) as lamps, \
                    mock.patch.object(A, "procession", wraps=A.procession) as walk:
                p = SET.h1(h, False, True)
            (call,) = drawn_on(p, palace)
            bay = call.kwargs.get("bay", A.BAY)
            self.assertIn(bay, (A.BAY, A.BAY - 1), name)
            self.assertEqual(call.args[2], 3 * bay + A.COLUMN, name)
            robes = [c.kwargs["robe"] for c in drawn_on(p, figure)]
            self.assertEqual(robes[:3], ["pearl", "purple", "green"], name)
            self.assertEqual(len(drawn_on(p, lamps)), 3, name)
            self.assertEqual(bool(drawn_on(p, walk)), name == "least", name)
        profile, _ = contents(KEY)["profile"]
        with mock.patch.object(A, "palace", wraps=A.palace) as palace:
            p = SET.h1(profile, False, True)
        self.assertEqual(drawn_on(p, palace)[0].kwargs["bay"], A.BAY - 1, "a long name leaves the bays a column less")

    def test_the_empress_wears_her_crown_and_collar_and_holds_her_bowl_and_her_ladies_wear_patterned_silk(self):
        """The court is laid with the mosaic's large dark eyes, their whites showing under dark brows. The empress
        wears her crown of gold and jewels topped with pearls, the strings of pearls falling from it beside her face,
        the broad collar of gold and jewels over her shoulders and a cloak of purple in its folds down to its hem
        embroidered in gold, and holds a bowl of gold in her hands; her ladies' silks are patterned all over in figures
        of gold, each with its stone. A drawing made lighter lets the figures of the silk go and keeps the rest."""
        for kind, art in A.COURT.items():
            eyes = next(row for row in art if "e" in row)
            self.assertEqual(eyes.count("W"), 2, kind)
            self.assertEqual(eyes.count("e"), 2, kind)
            self.assertIn("bbFbb", "".join(art), (kind, "the brows"))
        empress = A.COURT["empress"]
        self.assertEqual(empress[0].count("p"), 5, "the pearls on the crown")
        self.assertTrue(all(row[0] == "p" and row[-1] == "p" for row in empress[3:9]), "the strings of pearls")
        self.assertGreaterEqual(sum(row.count("r") + row.count("g") for row in empress[9:14]), 8, "the collar")
        self.assertIn("KQLfYYYfLqK", empress, "the bowl of gold in her hands")
        self.assertIn("KrYgYrYgYrK", empress, "the hem embroidered in gold")
        lady = "".join(A.COURT["lady"])
        self.assertGreaterEqual(lady.count("s"), 20, "the figures of the silk")
        self.assertGreaterEqual(lady.count("z"), 6, "and their stones")
        plain = "".join(A.court_art("lady", 4, lite=True))
        self.assertEqual(plain.count("s") + plain.count("z"), 0, "lighter, the silk is plain")
        self.assertEqual(len(A.court_art("lady", 4, lite=True)), len(A.COURT["lady"]) + 4)

    def test_where_the_court_walks_to_it_the_palace_door_has_its_curtain_drawn_aside_and_its_fountain(self):
        """Where the words leave the palace's whole height clear at its left and the court walks to it, its door
        stands there, its curtain drawn aside on the dark of the hall and the small fountain on the floor before it,
        the procession coming to it; elsewhere the palace stands as it was. Two units clear of every word. Under a
        phone's words, where the court stands between the apse and the palace, the door stands at the palace's left
        and the court comes to it."""
        for name, (h, _) in contents(KEY).items():
            with mock.patch.object(A, "doorway", wraps=A.doorway) as door, \
                    mock.patch.object(A, "procession", wraps=A.procession) as walk:
                p = SET.h1_narrow(h, False)
            (call,) = drawn_on(p, door)
            _, a, b, *_ = drawn_on(p, walk)[0].args
            self.assertLess(b, call.args[1], (name, "the court comes to the door"))
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "doorway", wraps=A.doorway) as door, \
                        mock.patch.object(A, "procession", wraps=A.procession) as walk, \
                        mock.patch.object(A, "palace", wraps=A.palace) as palace:
                    p, pixels = sprites(lambda: SET.h1(h, night, True), "scene")
                what = (name, night)
                doors = drawn_on(p, door)
                self.assertEqual(len(doors), 1 if name == "least" else 0, what)
                self.assertEqual(off_words(p, pixels), [], what)
                if doors:
                    (call,) = doors
                    x0 = call.args[1]
                    self.assertEqual(x0 + A.DOOR_W - A.COLUMN, drawn_on(p, palace)[0].args[1], what)
                    _, a, b, *_ = drawn_on(p, walk)[0].args
                    self.assertLess(b, x0, (what, "the court walks up to the door"))
                    self.assertGreater(b, x0 - 6, what)
                    water = RAMP["azure"][3 if night else 4]
                    fountain = {xy for xy, c in p.layers["base"].items() if c == water and x0 <= xy[0] < x0 + A.DOOR_W}
                    self.assertTrue(fountain, (what, "the fountain's water"))

    def test_an_h2_is_the_peacock_with_its_tail_half_open_and_the_port_where_there_is_room(self):
        """A section's header stands the peacock large beside its title, its tail half open in a fan of eyes, and the
        port beyond it where the words leave room. The bird is drawn larger than the strip's peacocks, to stand in
        front of its fan, the fan of its crest over its head; in a moving header the light crosses the fan's eyes
        in turn, eye after eye from the ground up over the fan and down its far side."""
        least, _ = contents(KEY)["least"]
        self.assertGreater(len(A.SHOWING), len(A.DISPLAY) + 6, "the bird stands larger than the strip's")
        self.assertGreater(len(A.SHOWING[0]), len(A.DISPLAY[0]) + 6)
        self.assertEqual("".join(A.SHOWING[:3]).count("CC"), 3, "the three spoons of its crest")
        for h, port in ((HEADER, False), (least, True)):
            with mock.patch.object(A, "display_peacock", wraps=A.display_peacock) as bird, \
                    mock.patch.object(A, "port", wraps=A.port) as harbour:
                p = SET.h2(h, False, True)
            (call,) = drawn_on(p, bird)
            self.assertGreaterEqual(call.kwargs["R"], 40, "the fan as large as the room allows")
            self.assertEqual(bool(drawn_on(p, harbour)), port)
            steps = sorted((p.meta[L][2][1], L) for L in layers_named(p, "fg"))
            self.assertEqual(len(steps), A.FAN_GLINTS, "the light crosses the fan's eyes in turn")
            self.assertEqual([t for t, _ in steps], [round(i / A.FAN_GLINTS * A.FAN_SWEEP, 3)
                                                     for i in range(A.FAN_GLINTS)])
            self.assertEqual({p.meta[L][2][3] for _, L in steps}, {SET.hand.glint}, "on the hand's glint")
            eyes = call.kwargs["eyes"]
            self.assertEqual({xy for _, L in steps for xy, c in p.layers[L].items() if c == PEARL[6]}, set(eyes))
            still = SET.h2(h, False, False)
            self.assertFalse(layers_named(still, "fg", "tw"), "a still file holds still")

    def test_an_h3_is_the_fountain_with_its_doves_and_as_much_of_its_court_as_the_words_leave_room_for(self):
        """A strip's header stands the fountain with a dove on each end of its rim, one bent to drink, a lamp crown
        hung over it. Where the words leave the band beside them wider, a peacock stands facing it, its train trailing
        behind it, and where wider still a pair of them, one either side, their trains trailing along the ground both
        ways; and where the words leave the band wider yet, the vine grows out of a vase beside them in a peopled
        scroll, its birds pecking at its grapes and oil lamps hung over it. The court fills the band to within a few
        tiles of the words, and keeps two clear of them."""
        cases = {"kit": ("pair", False), "repository": ("one", False), "profile": ("one", False),
                 "most": ("one", False), "least": ("pair", True)}
        for name, (birds, vine) in cases.items():
            h, _ = contents(KEY)[name]
            with contextlib.ExitStack() as stack:
                spies = {n: stack.enter_context(mock.patch.object(A, n, wraps=getattr(A, n)))
                         for n in ("basin_fountain", "dove", "peacock_pair", "standing_peacock", "vine_scroll",
                                   "hanging_lamp", "lamp_crown")}
                p, pixels = sprites(lambda: SET.h3(h, False, True), "scene")
            self.assertEqual(len(drawn_on(p, spies["basin_fountain"])), 1, name)
            self.assertEqual({c.kwargs.get("drink", False) for c in drawn_on(p, spies["dove"])}, {False, True}, name)
            self.assertEqual(len(drawn_on(p, spies["lamp_crown"])), 1, name)
            self.assertEqual(bool(drawn_on(p, spies["peacock_pair"])), birds == "pair", name)
            self.assertEqual(bool(drawn_on(p, spies["standing_peacock"])), birds == "one", name)
            self.assertEqual(bool(drawn_on(p, spies["vine_scroll"])), vine, name)
            self.assertEqual(len(drawn_on(p, spies["hanging_lamp"])), 3 if vine else 0, name)
            self.assertEqual(off_words(p, pixels), [], name)
            # the court reaches to within a few tiles of the words beside it
            band = p.w - 8
            while p.clear_of_words(band - 3, 26, band + 2, p.h - 30):
                band -= 1
            near = min(x for (x, y) in pixels if 26 <= y < p.h - 30 and x >= band - 2)
            self.assertLess(near - band, 20, (name, band, near))
        for name in ("kit", "least"):
            h, _ = contents(KEY)[name]
            with mock.patch.object(A, "peacock_pair", wraps=A.peacock_pair) as pair:
                p = SET.h3(h, False, True)
            (call,) = drawn_on(p, pair)
            self.assertGreaterEqual(call.kwargs["train"], A.TRAIN_MIN, name)

    def test_a_strips_vine_is_a_peopled_scroll_with_its_lamps_lit_by_night(self):
        """The vine's scrolls hold grapes and birds by turns, a dove, a partridge and a small blue bird among them,
        each scroll's leaf on its stalk outside the stem's turn; by night the oil lamps hung over it burn, their warm
        light on the vine, and by day they hang cold."""
        least, _ = contents(KEY)["least"]
        with mock.patch.object(A, "scroll_bird", wraps=A.scroll_bird) as birds:
            day = SET.h3(least, False, True)
        self.assertEqual({c.args[1] for c in drawn_on(day, birds)}, {"dove", "partridge", "finch"})
        night = SET.h3(least, True, True)
        burning = {c for L in layers_named(night, "fl") for c in night.layers[L].values()}
        self.assertIn(FLAME[6], burning, "the lamps burn by night")
        self.assertFalse(layers_named(day, "fl"), "and hang cold by day")
        lamps = [lamp for lamp in night.lamps if lamp[0] < 300]
        self.assertGreaterEqual(len(lamps), 3, "a lamp over the scrolls, three of them")

    def test_where_the_rows_allow_an_h1_has_the_port_the_court_sets_out_from(self):
        """Between the apse and the title of an H1 whose words leave the rows, the port of the city stands: its
        lighthouse on its mole beside the apse, ships on the water, the city's walls with their towers and its
        buildings rising behind them, as tall as the words over them allow, and its gate where the walls end, from
        which the procession walks toward the palace; by night the lighthouse burns and a window here and there is lit.
        Where the words leave the rows no room, the H1 stays as it was."""
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with mock.patch.object(A, "port", wraps=A.port) as port, \
                        mock.patch.object(A, "procession", wraps=A.procession) as walk, \
                        mock.patch.object(A, "skyline", wraps=A.skyline) as city:
                    p, pixels = sprites(lambda: SET.h1(h, night, True), "scene")
                self.assertEqual(off_words(p, pixels), [], (name, night))
                if name != "least":
                    self.assertEqual(drawn_on(p, port), [], (name, night, "no room for the port"))
                    continue
                (call,) = drawn_on(p, port)
                self.assertEqual(call.kwargs["mouth"], "left", night)
                self.assertTrue(drawn_on(p, city), (night, "the city's buildings"))
                _, x0, x1, *_ = call.args
                (march,) = drawn_on(p, walk)
                self.assertLess(x1, march.args[1] + 4, (night, "the procession sets out from the gate"))
                self.assertGreater(x1 - x0, 120, night)
                if night:
                    self.assertIn(FLAME[4], {p.get(x, y) for x in range(x0, x1) for y in range(p.h)},
                                  "lit windows")


class Phones(unittest.TestCase):
    def test_every_sprite_keeps_two_units_clear_of_every_word_on_a_phone(self):
        """On a phone the apse, the palace, the court, the peacock, the port and the fountain, the scroll, the section
        mark and the vine along the rule are built to the rows the words leave free: no pixel of theirs lies within
        two units of a word's box, for any of the shared contents, by day or by night."""
        drawers = {"H1": SET.h1_narrow, "H2": SET.h2_narrow, "H3": SET.h3_narrow}
        for name, (h, _) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    p, pixels = sprites(lambda: drawer(h, night), "scene_narrow", "scene_under", "garland",
                                        "section_mark", "rule_decor")
                    hits = off_words(p, pixels)
                    self.assertEqual(hits[:6], [], (name, code, night, len(hits)))

    def test_every_sprite_keeps_two_units_clear_of_every_word_on_a_wide_header_too(self):
        """The scenes, the scroll, the marks beside a title, the vine along the rule and the lamps' light laid by
        the last pass keep the same two units from every word across a wide header."""
        drawers = {"H1": SET.h1, "H2": SET.h2, "H3": SET.h3}
        for name, (h, _) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    p, pixels = sprites(lambda: drawer(h, night, True), "scene", "garland", "section_mark",
                                        "strip_mark", "rule_decor", "finish")
                    hits = off_words(p, pixels)
                    self.assertEqual(hits[:6], [], (name, code, night, len(hits)))

    def test_every_phone_header_of_every_shared_content_stands_a_scene(self):
        """Every phone header of every shared content, by day and by night, drawn as the kit draws it, stands a scene
        of the set's on the drawing its file is made from: the apse and the palace on an H1, the peacock on an H2 and
        the fountain on an H3, beside the words where they leave it room and under them where they leave none."""
        pieces = {"H1": ("apse", "palace"), "H2": ("display_peacock",), "H3": ("basin_fountain",)}
        names = sorted({n for ns in pieces.values() for n in ns})
        for name, (h, _) in contents(KEY).items():
            for code, wanted in pieces.items():
                for theme in (DAY, DARK):
                    _, p, spies = served(lambda: SET.header(code, h, theme, False, False), names)
                    self.assertEqual([n for n in wanted if not drawn_on(p, spies[n])], [], (name, code, theme["name"]))

    def test_where_the_words_leave_no_room_beside_them_the_peacock_stands_under_them(self):
        """Where the words leave the peacock no room beside them, the header is laid out again with rows of its own
        under the words, and there the peacock stands with its tail half open, the lighthouse on its mole beyond it,
        two units clear of every word. A phone whose peacock stood beside its words is laid out just as the kit lays
        it out."""
        kinds = ("display_peacock", "port")
        for name in ("profile", "most", "kit"):
            h, _ = contents(KEY)[name]
            for night in (False, True):
                with contextlib.ExitStack() as stack:
                    spies = {k: stack.enter_context(mock.patch.object(A, k, wraps=getattr(A, k))) for k in kinds}
                    p, pixels = sprites(lambda: SET.h2_narrow(h, night), "scene_under")
                self.assertEqual([k for k in kinds if not drawn_on(p, spies[k])], [], (name, night))
                self.assertEqual(off_words(p, pixels), [], (name, night))
                self.assertEqual(p.h - Holiday.h2_narrow(SET, h, night).h, SET.PHONE_ROWS["H2"], (name, night))
        h, _ = contents(KEY)["least"]
        for night in (False, True):
            with mock.patch.object(SET, "scene_under", wraps=SET.scene_under) as under:
                mine = SET.h2_narrow(h, night).svg("t", "d", still=True)
            self.assertFalse(under.called, night)
            self.assertEqual(mine, Holiday.h2_narrow(SET, h, night).svg("t", "d", still=True), night)

    def test_a_phones_strip_stands_its_fountain_and_its_peacocks_under_its_words_as_tall_as_a_phones_hero(self):
        """No strip's title leaves the fountain its height beside it, so every phone's H3 leaves rows under its words,
        and there the fountain with its doves stands between its pair of peacocks, the hero at least forty rows tall
        as the composition asks, two units clear of every word, for every shared content by day and by night."""
        kinds = ("basin_fountain", "dove", "peacock_pair")
        for name, (h, _) in contents(KEY).items():
            for night in (False, True):
                with contextlib.ExitStack() as stack:
                    spies = {k: stack.enter_context(mock.patch.object(A, k, wraps=getattr(A, k))) for k in kinds}
                    p, pixels = sprites(lambda: SET.h3_narrow(h, night), "scene_under", "scene_narrow")
                self.assertEqual([k for k in kinds if not drawn_on(p, spies[k])], [], (name, night))
                self.assertEqual(off_words(p, pixels), [], (name, night))
                self.assertGreaterEqual(max(y for _, y in pixels) - min(y for _, y in pixels) + 1, 40, (name, night))
                self.assertEqual(SET.phone_rows("H3", 0), SET.PHONE_ROWS["H3"])

    def test_a_phones_h1_stands_the_apse_the_court_and_the_palace_under_its_words(self):
        """A phone's H1 leaves its scene the rows under its words, ten more for each note it sets, so the apse, the
        procession and the palace keep their size under the most a page can say."""
        for name, (h, _) in contents(KEY).items():
            with mock.patch.object(A, "apse", wraps=A.apse) as apse, \
                    mock.patch.object(A, "palace", wraps=A.palace) as palace, \
                    mock.patch.object(A, "procession", wraps=A.procession) as walk:
                p = SET.h1_narrow(h, False)
            (call,) = drawn_on(p, apse)
            _, x0, x1, top, foot, *_ = call.args
            self.assertEqual((x0, x1), (6, 54), name)
            self.assertGreaterEqual(foot - top, 54, name)
            self.assertTrue(drawn_on(p, palace) and drawn_on(p, walk), name)


class Longest(unittest.TestCase):
    PIECES = ("apse", "palace", "figure", "hanging_lamp", "lamp_crown", "fountain", "peacock_neck", "display_peacock",
              "meadow", "eye_glints", "frame", "scroll", "crest_light", "tesserae_title", "tile_glint", "glitter",
              "stars", "running_vine", "star_mark")

    def test_the_longest_page_keeps_its_whole_scene_and_its_motion_within_the_budget(self):
        """Every field at its longest, the wide H1 and H2, by day and by night, drawn as the kit draws them as the
        month's design with its mark and kept all year without it, come within the budget and still move, and the
        drawing each is made from has every piece the drawing at full weight has, each where it stood: the apse with
        its peacocks, the fountain, the vine and the lamp crown, the palace with the court and its lamps, the peacock
        in its display, the scroll and its crests' light, the title in its tesserae with its glint, the glitter by day
        and the stars by night; and everything that moves at full weight moves still, and every light it has burns
        still. A drawing made lighter thins only the texture between them: the ground's tones, the stars' number, the
        eyes that glint and the glints by the lamps, and the outer rings of the lamps' glow."""
        most, _ = contents(KEY)["most"]

        def pieces(spies, p):
            return sorted(re.sub(r"'tl\d+'", "'tl'", repr((n, c.args[1:], sorted(c.kwargs.items()))))
                          for n, spy in spies.items() for c in drawn_on(p, spy))

        def lit(p):
            return {fill for (_, _, _, _, _, fill, _) in overlays(p)} | \
                {c for L in layers_named(p, "fl") for c in p.layers[L].values()}
        lighter = []
        for held in (SET.on(ITS_DAY), SET):
            for code in ("H1", "H2"):
                for theme in (DAY, DARK):
                    svg, p, spies = served(lambda: held.header(code, most, theme, True, True), self.PIECES)
                    with mock.patch.dict(BUDGET, {"header": 10 ** 9}):
                        _, whole, full = served(lambda: held.header(code, most, theme, True, True), self.PIECES)
                    where = (code, theme["name"], held.day)
                    self.assertFalse(whole.lite, where)
                    if p.lite:
                        lighter.append(where)
                    self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"], where)
                    self.assertIn("<animate", svg, where)
                    self.assertEqual(pieces(spies, p), pieces(full, whole), where)
                    self.assertEqual(moving(p), moving(whole), where)
                    self.assertEqual(lit(p), lit(whole), where)
        self.assertIn(("H1", "dark", None), lighter, "the most a page can say is drawn lighter where it must be")
        self.assertIn(("H1", "dark", ITS_DAY), lighter, "and with the month's mark")


class Footers(unittest.TestCase):
    FOOTERS = (("F1", SET.f1), ("F2", SET.f2), ("F1n", SET.f1_narrow), ("F2n", SET.f2_narrow))

    def test_every_footer_stands_on_the_floor_mosaic_a_row_clear_of_every_word(self):
        """A footer stands on the floor mosaic along its foot, a row clear of the lowest word: the guilloche plaited
        in garnet and blue round its chain of dark eyes, in seven rows where the words leave them, in five where they
        leave fewer and else a string of tesserae; and wherever a cell leaves the floor room it rises over the plait
        in a band of opus sectile, roundels of porphyry and squares of serpentine on white marble. Nothing of it comes
        within a row of a word."""
        risen = set()
        for name, (_, f) in contents(KEY).items():
            for code, draw in self.FOOTERS:
                for night in (False, True):
                    p, pixels = sprites(lambda: draw(f, night), "_floored")
                    what = (name, code, night)
                    low = max(b[3] for b in p.words)
                    rows = next(n for n in (7, 5, 2) if p.h - (low + 1) >= n or n == 2)
                    plait = f'fg{rows}{"n" if night else "d"}'
                    self.assertIn(f'<pattern id="{plait}"', "".join(p.defs), what)
                    self.assertIn(f'fill="url(#{plait})"', "".join(p.shapes["base"]), what)
                    self.assertEqual({(x, p.h - 1) for x in range(p.w)} - pixels, set(), what)
                    self.assertEqual(off_words(p, pixels, margin=1)[:6], [], what)
                    if f'fill="url(#fs{"n" if night else "d"})"' in "".join(p.shapes["base"]):
                        risen.add((name, code))
        self.assertLessEqual({("repository", "F1"), ("least", "F1"), ("most", "F2")}, risen, "the sectile rises")

    def test_the_doves_of_pliny_stand_where_the_cells_leave_room_and_their_lamp_burns_by_night(self):
        """Wherever the cells leave a footer room, after the last of them or else at the corner of the notes, in a
        cell or over the words, the doves of Pliny stand at their bowl, one bent to drink and one facing it, on the
        floor, on a rule or on a ledge of gold, two units clear of every word; and the oil lamp stands beside them
        where there is room for it, or hangs over them, cold by day and lit by night, its light on them. On a phone
        as on a wide sheet; only a footer whose cells leave no room goes without."""
        crowded = {("most", "F1"), ("least", "F1n")}
        for name, (_, f) in contents(KEY).items():
            for code, draw in self.FOOTERS:
                for night in (False, True):
                    with mock.patch.object(A, "pliny", wraps=A.pliny) as doves, \
                            mock.patch.object(A, "hanging_lamp", wraps=A.hanging_lamp) as hung:
                        p = draw(f, night)
                    what = (name, code, night)
                    stood = drawn_on(p, doves)
                    self.assertEqual(len(stood), 0 if (name, code) in crowded else 1, what)
                    burning = any(c == FLAME[6] for L in p.layers.values() for c in L.values())
                    self.assertEqual(burning, night and bool(stood), what)
                    for call in stood:
                        _, x, row, _ = call.args
                        width = A.PLINY_W + (1 + len(A.LAMP_MARK[0]) if call.kwargs["lamp_beside"] else 0)
                        self.assertTrue(p.clear_of_words(x - 2, row - A.PLINY_H - 2, x + width + 2, row + 2), what)
                        self.assertTrue(call.kwargs["lamp_beside"] or drawn_on(p, hung), (what, "a lamp by them"))
                        white = {xy for xy, c in p.layers["base"].items() if c in (PEARL[6], PEARL[5], FLAME[6],
                                                                                  GOLD[5], GOLD[6])
                                 and x <= xy[0] < x + A.PLINY_W and row - A.PLINY_H <= xy[1] < row}
                        self.assertGreater(len(white), 30, (what, "the doves' white"))
                    for call in drawn_on(p, hung):
                        hx = call.args[1]
                        self.assertTrue(p.clear_of_words(hx - 6, A.FW - 2, hx + 7, call.args[3] + 9), what)

    def test_a_link_is_a_marble_plaque_and_a_small_file(self):
        for i, label in enumerate(("Issues", "Pull Requests", "Releases", "Actions")):
            for theme in (DAY, DARK):
                svg = SET.link(label, theme, i)
                self.assertLess(len(svg.encode("utf-8")), 2500, (label, theme["name"]))
                self.assertIn(f'fill="url(#mv{"n" if theme is DARK else "d"})"', svg, "the marble")
                self.assertIn(LAPIS[2], svg, "the panel of lapis the icon is inlaid on")


class Elements(unittest.TestCase):
    def test_an_avatar_is_a_portrait_in_mosaic_never_initials(self):
        """A contributor is a portrait in mosaic on a roundel of gold, a jewelled diadem on the hair, robed in their own
        colour by turns; a bot is a dove on the roundel."""
        robes = set()
        for night in (False, True):
            for i in range(3):
                p = Pix(40, 40)
                SET.avatar(p, 20, 20, i, {"initials": "IV", "name": "Imogen Vale"}, night)
                self.assertEqual(p.words, [], "no letters")
                drawn = set(p.layers["base"].values())
                self.assertIn(GOLD[4 - (1 if night else 0)], drawn, "the roundel and the diadem")
                robes.add(frozenset(drawn))
            p = Pix(40, 40)
            SET.avatar(p, 20, 20, 0, {"initials": "", "name": "bot"}, night)
            self.assertIn(PEARL[6 - (1 if night else 0)], set(p.layers["base"].values()), "the dove's white")
        self.assertEqual(len(robes), 6, "each in their own colour")

    def test_the_histogram_stands_columns_of_tesserae_with_marble_capitals(self):
        spec = E.describe("instruments", next(d for d in ELEMENTS.values() if d["kind"] == "instruments"))
        for theme in (DAY, DARK):
            k = -1 if theme is DARK else 0
            with mock.patch.object(A, "column_bar", wraps=A.column_bar) as bars:
                svg = SET.element("instruments", spec, theme, "wide")
            self.assertGreaterEqual(bars.call_count, 10, theme["name"])
            self.assertIn(PEARL[6 + k], svg, (theme["name"], "the capitals' white marble"))
            for stone in ("lapis", "porphyry", "green"):
                self.assertIn(RAMP[stone][3 + k], svg, (theme["name"], stone))

    def test_the_dial_is_a_gold_sun_disc_its_hand_the_gnomons_shadow(self):
        """The dial's face is a sun disc of rays in two golds, every figure on it at 4.5:1, in a rim of bright gold;
        its hand is the gnomon's shadow, and none of the layout's plain hand is left."""
        for night in (False, True):
            face = A.sun_face(night)
            rays = {face(x, y, 50, 40, 30) for x in range(20, 81) for y in range(10, 41)} - {None}
            self.assertEqual(len(rays), 2, "two golds by turns")
            for c in rays:
                for role in ("body", "muted"):
                    self.assertGreaterEqual(contrast(SET.ink(night)[role], c), 4.5, (night, role, c))
            p = Pix(120, 60)
            SET.dial(p, {"value": 7, "span": 30, "sub": "v1"}, 60, 44, 30, night)
            SET.finish(p, night)
            drawn = {c for xy, c in p.layers["base"].items() if (xy[0] - 60) ** 2 + (xy[1] - 44) ** 2 < 15 ** 2}
            self.assertNotIn(SET.ink(night)["accent"], drawn, (night, "the plain hand redrawn as a shadow"))
            self.assertIn(LAPIS[2] if night else RAMP["earth"][1], drawn, (night, "the gnomon's shadow"))
            self.assertLessEqual(rays, set(p.layers["base"].values()), night)

    def test_a_card_is_a_marble_plaque_in_a_rim_of_gold_tesserae(self):
        """A schematic's card is a plaque in a rim of gold tesserae, its icon inlaid again in gold on a panel of lapis
        at its left and a jewel at each top corner; and its wire is a line of gold tesserae."""
        for night in (False, True):
            k = -1 if night else 0
            p = Pix(120, 40)
            x, y, w, h = 4, 4, 104, 27
            SET.node(p, night, x, y, w, h, {"title": "Probes", "path": "crates/probe", "icon": "grid"}, seed=1)
            rim = {p.get(xx, y) for xx in range(x + 3, x + w - 3)}
            self.assertEqual(rim, {GOLD[5 + k], GOLD[4 + k]}, (night, "the rim's top"))
            panel = {p.get(xx, yy) for xx in range(x + 1, x + 14) for yy in range(y + 2, y + h - 2)}
            self.assertIn(LAPIS[2], panel, night)
            self.assertIn(GOLD[5 + k], panel, (night, "the icon in gold"))
            self.assertEqual((p.get(x + 2, y), p.get(x + w - 3, y)), (RAMP["red"][4 + k], RAMP["green"][4 + k]))
        svg = SET.element("schematic", E.describe("schematic", ELEMENTS["how-it-runs"]), DAY, "wide")
        self.assertIn(RAMP["red"][5], svg, "a garnet where the wire bends")

    def test_the_seal_is_a_porphyry_roundel_its_check_laid_in_gold(self):
        """The seal is a ring of porphyry set with garnets and emeralds in gold about its disc, and the check in its
        disc is laid again in gold tesserae with a dark shadow, by day and by night."""
        for theme in (DAY, DARK):
            night = theme is DARK
            k = -1 if night else 0
            with mock.patch.object(A, "gold_check", wraps=A.gold_check) as check:
                svg = SET.element("certificate", E.describe("certificate", ELEMENTS["conformance"]), theme, "wide")
            self.assertEqual(check.call_count, 1, theme["name"])
            for c, what in ((RAMP["porphyry"][3 + k], "the porphyry"), (RAMP["red"][5 + k], "a garnet"),
                            (RAMP["green"][5 + k], "an emerald"), (GOLD[6], "the check's lit tiles")):
                self.assertIn(c, svg, (theme["name"], what))
        p = Pix(120, 120)
        SET.rosette(p, 60, 60, 23, 31, 16, False)
        p.rect(53, 45, 14, 12, SET.ink(False)["accent"])
        A.gold_check(p, False, SET.ink(False)["accent"], SET.ink(False)["shadow"])
        check = {p.get(x, y) for x in range(53, 67) for y in range(45, 57)}
        self.assertEqual(check, {GOLD[4], GOLD[5], GOLD[6]}, "every tile of the check in gold")

    def test_a_placard_is_a_marble_panel_inlaid_with_cut_stones(self):
        for theme in (DAY, DARK):
            svg = SET.element("placard", E.describe("placard", ELEMENTS["action"]), theme, "wide")
            n = "n" if theme is DARK else "d"
            self.assertIn(f'fill="url(#ov{n})"', svg, (theme["name"], "the veined field"))
            self.assertEqual(svg.count(f'fill="url(#os{n})"'), 4, (theme["name"], "the border on all four sides"))
            self.assertIn(RAMP["porphyry"][4 - (1 if theme is DARK else 0)], svg, "its discs of porphyry")

    def test_the_time_line_is_the_vine_with_grapes_at_the_releases_and_a_peacock_at_today(self):
        spec = E.describe("milestones", ELEMENTS["history"])
        for theme in (DAY, DARK):
            with mock.patch.object(A, "grape_release", wraps=A.grape_release) as grapes, \
                    mock.patch.object(A, "today_peacock", wraps=A.today_peacock) as bird, \
                    mock.patch.object(A, "vine_line", wraps=A.vine_line) as vine:
                SET.element("milestones", spec, theme, "wide")
            self.assertTrue(vine.called and bird.called, theme["name"])
            self.assertGreaterEqual(grapes.call_count, 10, theme["name"])
            self.assertLessEqual({c.args[3] for c in grapes.call_args_list}, {"big", "major", "minor", "next", "made"})

    def test_a_counters_numerals_hold_4_5_on_their_marble(self):
        """Every numeral holds 4.5:1 on its cell of white marble, a leading nought fainter; and the marble lies on a
        layer under the drawing's own, so a numeral is laid over it whatever its colour."""
        for night in (False, True):
            q = Pix(20, 20)
            SET.counter_cell(q, 2, 2, night)
            self.assertFalse(q.layers["base"], night)
            face = q.layers["far"][(7, 8)]
            self.assertIn(face, PEARL, night)
            self.assertGreaterEqual(contrast(SET.counter_ink(night, False), face), 4.5, night)
            self.assertGreaterEqual(contrast(SET.counter_ink(night, True), face), 1.5, night)


class Badges(unittest.TestCase):
    def test_a_rim_of_gold_tesserae_lies_along_every_badges_top_with_the_letters_under_it(self):
        for style in BADGE_STYLES:
            drawn = [SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                       SET.badge_states()["green"])]
            drawn += [SET.plate_badge(style, "License", "MIT", "scale", mode) for mode in ("day", "night")]
            for p in drawn:
                top = [p.get(x, 0) for x in range(p.w) if inside(x, 0, p.w, p.h, BADGE_STYLES[style]["corner"])]
                self.assertTrue(top and set(top) == {GOLD[5], GOLD[4]}, (style, "tiles of two golds by turns"))
                self.assertTrue(all(y >= 2 for _, _, _, y, _ in p.uses["base"]), "the letters sit under the rim")

    def test_a_live_badges_states_are_stones(self):
        """A live badge shows its state in a stone: green serpentine, a pale gold, red porphyry and grey marble."""
        states = SET.badge_states()
        self.assertEqual({s: states[s][0] for s in ("green", "yellow", "red", "slate")},
                         {"green": RAMP["green"][2], "yellow": GOLD[5], "red": RAMP["porphyry"][3],
                          "slate": RAMP["stone"][2]})


def mark_box(w: int, margin: int = 2) -> tuple:
    """The box the month's mark takes at the top centre of a header `w` units wide, `margin` units wider all round,
    as (x0, y0, x1, y1), ends excluded."""
    n = SET.hand.mark_size
    x0, y0 = w // 2 - n // 2, MARK_Y - n // 2
    return x0 - margin, y0 - margin, x0 + n + margin, y0 + n + margin


def skin_of(colour: str) -> int:
    """Which of the hand's skins a colour is a tone of, or -1."""
    return next((i for i in range(3) if colour in SET.hand.ramp(f"skin{i}")), -1)


class Hand(unittest.TestCase):
    """The Mosaic drawn in its collection's hand (see `collections.hand`): it keeps to the hand as August's design
    and kept all year; its words are in the hand's inks; its gold is burnished and its lapis quiet, both in the
    hand's bands; its lamps burn on the hand's flame; its court is on the hand's skins; the mark's box stays clear
    of every scene and every star, a crest of the scroll lying whole under the mark; its heroes stand to the
    composition's measure; and its motion keeps the hand's times."""

    def test_it_keeps_to_its_hand_as_the_months_design_and_kept_all_year(self):
        self.assertIsInstance(SET, CollectionSet)
        self.assertEqual(SET.collection, "medieval")
        self.assertEqual(SET.on(ITS_DAY).month, 8)
        self.assertEqual(check(SET.on(ITS_DAY)), [])
        self.assertEqual(check(SET), [])

    def test_its_words_are_in_the_hands_inks(self):
        for night in (False, True):
            k = SET.ink(night)
            self.assertEqual((k["body"], k["muted"]), (SET.hand.body[night], SET.hand.muted[night]), night)

    def test_its_gold_is_burnished_and_its_lapis_quiet_in_the_hands_bands(self):
        """Behind the words the gold calms to a burnished gold, unmistakably gold in its hue and colour yet within
        the hand's band; every tile of the ground keeps to the band's colour too, warmer in its shadows and paler in
        its lights as gold is. By night every band of the vault, and the field lifted behind the words, is a lapis
        within the night's band."""
        lo, hi, most = SET.hand.day_ground
        light, chroma, hue = lab(CALM)
        self.assertTrue(lo <= light <= hi and 32 <= chroma <= most and 75 <= hue <= 95, (light, chroma, hue))
        self.assertTrue(all(lab(tone)[1] <= most for tone in A.TILE), "every tile of the gold")
        hues = [lab(tone)[2] for tone in A.TILE]
        self.assertEqual(hues, sorted(hues), "warmer in the shadows, paler in the lights")
        lo, hi, most = SET.hand.night_ground
        lifted = {"#%02X%02X%02X" % _blend(_rgb(c), A.LIFT, A.CALM_LIFT) for c in NIGHT_SKY}
        for c in [*NIGHT_SKY, *lifted]:
            light, chroma, hue = lab(c)
            self.assertTrue(lo <= light <= hi and chroma <= most and 270 <= hue <= 310, (c, light, chroma, hue))

    def test_every_lamp_burns_on_the_hands_flame(self):
        """The lamp crowns, the oil lamps, the lighthouse's fire and the light they throw burn on the hand's flame:
        every pixel on the flames' flickering layers and every pool and glow laid round them is a tone of it."""
        self.assertEqual(FLAME, SET.hand.ramp("flame"))
        least, _ = contents(KEY)["least"]
        for draw in (SET.on(ITS_DAY).h1, SET.on(ITS_DAY).h2, SET.on(ITS_DAY).h3):
            p = draw(least, True, True)
            burning = {c.split(":")[0] for L in layers_named(p, "fl") for c in p.layers[L].values()}
            self.assertTrue(burning, draw)
            self.assertLessEqual(burning | {t[5] for t in overlays(p)}, set(FLAME), draw)

    def test_the_court_is_on_the_hands_skins_in_the_mosaics_own_proportions(self):
        """The court keeps the mosaic's own proportions, each figure eleven wide with the mosaic's large dark eyes,
        and takes the hand's skin: every face of the empress, her ladies, the procession and the portraits is on one
        of the hand's three skins, and among them all three are worn."""
        self.assertTrue(all(len(row) == A.FIGURE_W for art in A.COURT.values() for row in art))
        least, _ = contents(KEY)["least"]
        worn = set()
        for night in (False, True):
            with mock.patch.object(A, "court_pal", wraps=A.court_pal) as pal:
                SET.on(ITS_DAY).h1(least, night, False)
                for i in range(6):
                    A.portrait(Pix(40, 40), 20, 20, i, night)
            for call in pal.call_args_list:
                colours = A.court_pal(*call.args, **call.kwargs)
                worn |= {skin_of(colours["f"]), skin_of(colours["F"])}
        self.assertEqual(worn, {0, 1, 2})

    def test_the_marks_box_stays_clear_of_every_scene_and_star_with_the_mark_and_without_it(self):
        """The box the month's mark takes, and two units round it, holds nothing of a scene, a star or a glittering
        tile, in every header wide and on a phone, for every shared content, by day and by night, as August's design
        and kept all year."""
        for month in (True, False):
            for name, (h, _) in contents(KEY).items():
                for code in ("H1", "H2", "H3"):
                    for wide in (True, False):
                        for night in (False, True):
                            def draw():
                                held = SET.on(ITS_DAY) if month else SET
                                if wide:
                                    return getattr(held, code.lower())(h, night, True)
                                return getattr(held, f"{code.lower()}_narrow")(h, night)
                            hooks = ("scene", "sky") if wide else ("scene_narrow", "scene_under", "sky")
                            p, pixels = sprites(draw, *hooks)
                            x0, y0, x1, y1 = mark_box(p.w)
                            inside = [xy for xy in pixels if x0 <= xy[0] < x1 and y0 <= xy[1] < y1]
                            self.assertEqual(inside, [], (month, name, code, wide, night))

    def test_a_crest_of_the_wave_scroll_lies_whole_under_the_mark(self):
        """A crest of the scroll is centred under the mark, so the mark covers it whole and the run of crests ends
        evenly either side, on a wide header and a phone's, with the mark and without it."""
        for wide in (True, False):
            for held in (SET.on(ITS_DAY), SET):
                svg = held.header("H1", HEADER, DAY, wide, False)
                off = int(re.search(r'<pattern id="wsw" x="(-?\d+)"', svg).group(1))
                self.assertEqual(((415 if wide else 180) // 2 - off) % A.WAVE_W, A.WAVE_W // 2, (wide, held.day))

    def test_its_heroes_stand_to_the_compositions_measure(self):
        """A section's scene, the peacock in its display, rises at least four fifths of the band from the scroll to
        its ground; the fountain and its court rise a strip's full height; and the hero of a phone's H2 and H3 stands
        at least forty rows tall, for the kit's own lines, the samples and the least a page can say."""
        for name, (h, _) in contents(KEY).items():
            if name == "most":
                continue
            for code, wide, need in (("H2", True, 0.8), ("H3", True, 0.94), ("H2", False, 40), ("H3", False, 40)):
                draw = (lambda: getattr(SET, code.lower())(h, False, True)) if wide else \
                    (lambda: getattr(SET, f"{code.lower()}_narrow")(h, False))
                p, pixels = sprites(draw, *(("scene",) if wide else ("scene_narrow", "scene_under")))
                top, foot = min(y for _, y in pixels), max(y for _, y in pixels)
                if wide:
                    self.assertGreaterEqual(foot - top + 1, need * (foot - A.SCROLL_FOOT), (name, code))
                else:
                    self.assertGreaterEqual(foot - top + 1, need, (name, code))

    def test_its_motion_keeps_the_hands_times(self):
        """A title's glint passes once every twelve seconds, the hand's glint, its window stepping a tile at a time
        and shown only while it makes its first crossing of the period; the light along the scroll's crests and the
        sheen over the gold are slow sweeps of the hand's; and the peacocks take turns to drink on an idle of its
        length."""
        for h in (HEADER, contents(KEY)["least"][0], contents(KEY)["most"][0]):
            svg = SET.header("H1", h, DAY, True, True)
            inner = float(re.search(r'<clipPath id="gc\d+"><path [^>]*><animateTransform [^>]*dur="([\d.]+)s"',
                                    svg).group(1))
            crossings = round(SET.hand.glint / inner)
            self.assertAlmostEqual(crossings * inner, SET.hand.glint, places=6)
            gate = re.search(r'<g clip-path="url\(#gc\d+\)"><animate attributeName="opacity" values="1;0" '
                             r'keyTimes="0;([\d.]+)" dur="([\d.]+)s"', svg)
            if crossings > 1:
                self.assertEqual((float(gate.group(1)), float(gate.group(2))), (1 / crossings, SET.hand.glint))
            else:
                self.assertIsNone(gate)
            crest = float(re.search(r'<clipPath id="wc\d+"><rect [^>]*><animateTransform [^>]*dur="([\d.]+)s"',
                                    svg).group(1))
            self.assertTrue(24 <= crest <= 48 and 24 <= A.SHEEN_BEAT <= 48, (crest, A.SHEEN_BEAT))
        self.assertTrue(4 <= A.TURN <= 8)


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
        weight, with their motion and with the month's mark where the design is drawn as its month's, at least 1,500
        bytes under their budgets, so a longer profile keeps everything too; only the most a page can say is drawn
        lighter. The least a page can say, whose H1 by night stands the apse, the port, the city, the court in
        procession, the palace's door and the palace, is the fullest."""
        for name, (h, f) in contents(KEY).items():
            if name == "most":
                continue
            for theme in (DAY, DARK):
                for code in ("H1", "H2", "H3"):
                    for wide, motion in ((True, True), (True, False), (False, False)):
                        for held in (SET.on(ITS_DAY), SET):
                            what = (name, code, theme["name"], wide, motion, held.day)
                            svg, made = drawn_pieces(lambda: held.header(code, h, theme, wide, motion), held)
                            self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"] - 1500, what)
                            self.assertFalse(any(q.lite for q in made), what)
                            self.assertEqual("<animate" in svg, wide and motion, what)
                for code in ("F1", "F2"):
                    for wide in (True, False):
                        svg, made = drawn_pieces(lambda: SET.footer(code, f, theme, wide, False))
                        self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["footer"] - 1500, (name, code, wide))
                        self.assertFalse(any(q.lite for q in made), (name, code, wide))

    def test_text_colours_hold_4_5_on_the_paper_and_every_row_of_the_night(self):
        for night in (False, True):
            k = SET.ink(night)
            p = Pix(415, 200)
            grounds = {SET.bg_at(p, night, y) for y in range(p.h)}
            if night:
                grounds |= {"#%02X%02X%02X" % _blend(_rgb(c), A.LIFT, A.CALM_LIFT) for c in NIGHT_SKY}
            for role in ("title", "body", "muted", "accent"):
                for ground in grounds:
                    self.assertGreaterEqual(contrast(k[role], ground), 4.5, (night, role, ground))
            self.assertGreaterEqual(contrast(k["tag_ink"], k["tag"]), 4.5, (night, "tag"))
            fill, _, ink, _ = SET.link_colours(night)
            self.assertGreaterEqual(contrast(ink, fill), 4.5, (night, "a link's letters on its plaque"))

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
