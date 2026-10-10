# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Hoard set's own rules, which the checks every set shares cannot know: it keeps to the medieval hand, as
December's design and kept all year, its words in the hand's inks, its ground in the hand's bands and warm by day,
its ember breath on the hand's flame and its moon the hand's, its motion on the hand's time, the top centre of every
header kept for the month's mark with the lintel's spirals and the icicles pausing whole on either side of it, and
its heroes and its footer's mark placed as the collection places them; a header's wall is drystone walling
with every block of its words on a dressed stone and the corbelled roof along its top, lit cold from the mouth and
warm from the gold by day; what the night alone shows (the ember of the dragon's breath, the barrow's dark, the
moon and the stars over the downs, the moon's shaft across the floor) stays out of the day's files, and by night
the breath lights the scales and the gold nearest it and its light and the moon's lie over the walls, softly on
the stones the words are on; a title is gold cloisonne set with garnets, with a glint that crosses it only in a
wide moving header; icicles hang from the lintel, never a row of dots, and a drop gathers and falls only in a wide
moving header; the dragon is the showpiece, coiled round and over a mountain of coins that pours down to the floor
with its treasures and gems on it, as large as its room allows, its tail swept out along the floor, its belly
pale against the gold by day and lit gold by night, its eye half opening and by night glowing, its smoke rising,
a coin sliding down the pile and a glint wandering over the gold in a moving header; the barrow's mouth is a
passage grave's great stones carved with spirals, the thief near the door going away over the snow with the cup
he took held high and his footprints behind him; where the words leave the floor clear the golden standard
stands over its own gold; an H2 is the dragon's great head resting its jaw on its gold, its eye opening, and an
H3 the great helm on its heap with the buckle, the clasps, a sword and a horn; every phone header of every shared
content stands
a scene of the set's, beside its words where they leave it room and else under them in rows of its own; the most
a page can say keeps its whole scene and its motion within the budget, a drawing made lighter keeping every piece
where it stood; every scene, the icicles, the marks beside a title and the coins along a rule keep two units
from every word; a footer ends in a drift of coins with the dragon's tail curled round a cup at its corner,
glinting by night, and keeps clear of every word; a link is a struck coin on a strap of garnet, a small file;
a schematic's card is a plaque of gold with its icon in gold on garnet and its wire a chain; the histogram
stacks coins; the dial is an arm ring, its hand a dragon; the counters are ingots; the timeline is a trail of
coins with gems and the dragon's eye; the roster's avatars are bracteates, never initials; the seal is a brooch
of gold and garnet; a placard is the iron bound lid of a chest; and a gold rim lies along every badge's top. The
set is a theme, not a holiday on the calendar, so the checks every registered set shares run here over the set
directly, with the same contents and the same entry points."""
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
from domain.banners.content import Header
from domain.banners.designs import DESIGNS, variants
from domain.canvas import BUDGET, DARK, DAY, colours, lint
from domain.collections.hand import MEDIEVAL, check, lab
from domain.elements import draw as E
from domain.holidays.designs import Holiday
from domain.holidays.designs.badges import PLATE, STATES, STYLES as BADGE_STYLES, inside
from domain.collections.medieval_hoard import SET
from domain.collections.medieval_hoard import art as A
from domain.collections.medieval_hoard.palette import NIGHT_SKY, RAMP, X
from domain.holidays.pixel import Pix, contrast
from domain.palette import PALETTE

support.install()
KEY = SET.key
HEADER = Header(tone="standard", holiday=KEY)
BARE = HEADER.with_(title="x", tagline="", description="", motto="", notes=())
GOLD, GARNET, DRAKE, EMBER = RAMP["gold"], RAMP["garnet"], RAMP["drake"], RAMP["ember"]
HELD = SET.on(dt.date(2026, 12, 1))     # the Hoard drawn as December's design, with the month's mark


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


# A symbol drawn as another one turned to face the other way, and a block laid in a pattern: what `sprites` reads
# to know which cells they cover.
MIRROR = re.compile(r'<use href="#(q\d+)" transform="matrix\(-1 0 0 1 (\d+) 0\)"/>')
RECT = re.compile(r'<rect x="(-?\d+)" y="(-?\d+)" width="(\d+)" height="(\d+)"')


def sprites(draw, *hooks) -> tuple:
    """`draw()`'s drawing, and every pixel of the sprites the set's `hooks` (names of its drawing hooks) put on it,
    gathered as they draw: their pixels on every layer, the cells of the symbols they place, the blocks they lay in
    a pattern and the cells of the shapes they fill (which the set keeps in the drawing's `filled`)."""
    pixels, cells = set(), {}
    symbol = Pix.symbol

    def kept(self, key, cells_=None, shapes="", mono=False):
        sid = symbol(self, key, cells_, shapes, mono)
        if sid not in cells:
            own = set(cells_ or ())
            for ref, w in MIRROR.findall(shapes):
                own |= {(int(w) - 1 - x, y) for x, y in cells.get(ref, ())}
            cells[sid] = own
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
    """The calls a spied art function made on the sheet `p` itself, not on the scratch canvases a scene tests its
    stagings on."""
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


def stamped(p, spy) -> list:
    """The pieces of art the spied `stamp` laid on the sheet `p`."""
    return [c.args[3] for c in drawn_on(p, spy)]


def mix(a: str, b: str, t: float) -> str:
    """The colour `a` with the colour `b` laid over it at opacity `t`."""
    ra, rb = (tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in (a, b))
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ra, rb))


def cut(rects, spans, origin: int, period: int, clear: tuple, inside: tuple) -> list:
    """The motifs a band of them laid in `rects`, (x, width), cuts within the columns `inside` (the sheet between its
    standing stones) or lays in the columns `clear`: its motifs take the columns `spans` of a tile repeating every
    `period` columns from column `origin`. [] when every motif it lays is whole and clear of them."""
    lo, hi = clear
    bad = []
    for rx, rw in rects:
        for n in range(-1, (rx + rw - origin) // period + 2):
            for s, e in spans:
                a, b = origin + n * period + s, origin + n * period + e
                if b < rx or a >= rx + rw:
                    continue
                if (a < rx and rx > inside[0]) or (b >= rx + rw and rx + rw < inside[1]) or (a < hi and b >= lo):
                    bad.append(((rx, rw), (a, b)))
    return bad


def laid(p, pid: str) -> list:
    """The blocks a pattern `pid` is laid in on a drawing's base layer, as (x, width)."""
    return [(int(x), int(w)) for x, w in re.findall(r'<rect x="(\d+)" y="\d+" width="(\d+)" height="\d+" '
                                                   rf'fill="url\(#{pid}\)"/>', "".join(p.shapes["base"]))]


class Hand(unittest.TestCase):
    """The Hoard in the medieval collection's hand (see `collections.hand`)."""

    def test_it_keeps_to_its_hand_as_decembers_design_and_kept_all_year(self):
        self.assertEqual(check(HELD), [])
        self.assertEqual(check(SET), [])

    def test_its_words_are_in_the_hands_inks(self):
        for night in (False, True):
            k = SET.ink(night)
            self.assertEqual((k["body"], k["muted"]), (MEDIEVAL.body[night], MEDIEVAL.muted[night]), night)

    def test_its_ground_falls_in_the_hands_bands(self):
        """By day the chalk behind every word falls in the hand's day band and leans warm, alone, under the snow's
        cold light from the mouth at each of its steps and under the gold's warmth at each of its; by night every
        row of the dark and the dressed stones the words are cut on fall in its night band."""
        lo, hi, most = MEDIEVAL.day_ground
        chalk = SET.bg_at(Pix(415, 100), False, 50)
        for c in [chalk] + [mix(chalk, RAMP["frost"][5], a) for _, a in A.SNOWLIGHT] + \
                [mix(chalk, GOLD[6], a) for _, a in A.WARMTH]:
            light, chroma, hue = lab(c)
            self.assertTrue(lo <= light <= hi and chroma <= most, (c, light, chroma))
            self.assertTrue(chroma >= 6 or 40 <= hue <= 110, (c, "warm", chroma, hue))
        lo, hi, most = MEDIEVAL.night_ground
        for c in set(NIGHT_SKY) | {RAMP["earth"][2]}:
            light, chroma, _ = lab(c)
            self.assertTrue(lo <= light <= hi and chroma <= most, (c, light, chroma))

    def test_its_fire_burns_on_the_hands_flame_and_its_moon_is_the_hands(self):
        """The dragon's ember breath is the hand's flame, every colour its fire lays by night a tone of that ramp, and
        the moon over the snow is drawn on the hand's moon ramp."""
        self.assertEqual(EMBER, MEDIEVAL.ramp("flame"))
        flame = set(MEDIEVAL.ramp("flame"))
        for draw in (SET.h1, SET.h2):
            p = draw(HEADER, True, True)
            lit = [n for n in p.layers if n.startswith(("fl", "fb"))]
            fire = {c.split(":")[0] for n in lit for c in p.layers[n].values()}
            fire |= set(re.findall(r'fill="(#[0-9A-F]{6})"', "".join(shape for n in lit for shape in p.shapes[n])))
            self.assertTrue(fire, draw.__name__)
            self.assertLessEqual(fire, flame, draw.__name__)
        q = Pix(40, 60)
        A._view(q, 5, 5, 30, 55, True, False)
        disc = {q.get(7 + i, 15 + j) for j, row in enumerate(A.MOON) for i, ch in enumerate(row) if ch != "."}
        self.assertLessEqual(disc, set(MEDIEVAL.ramp("moon")))

    def test_it_moves_in_the_hands_time(self):
        """A title's glint passes every twelve seconds, the hand's period, whatever the title's length; the ember
        flickers and the gold twinkles on the engine's cadences; the dragon's eyes, its smoke, the drop and the sliding
        coin idle in loops of four to eight seconds; and the glint wanders over the hoard in a slow sweep."""
        for h in (HEADER, BARE, contents(KEY)["most"][0]):
            svg = HELD.header("H1", h, DARK, True, True)
            periods = re.findall(r'<clipPath id="gl\d+"><polygon[^>]*><animateTransform[^>]*dur="([\d.]+)s"', svg)
            self.assertTrue(periods)
            self.assertEqual({float(d) for d in periods}, {MEDIEVAL.glint})
        night = HELD.header("H1", HEADER, DARK, True, True)
        self.assertIn('dur="1.8s"', night, "the ember flickers")
        self.assertIn('dur="1.5s"', night, "the gold twinkles")
        for loop in (A.EYE_LOOP, A.BIG_EYE_LOOP, A.SMOKE_LOOP, A.DRIP, A.SLIDE):
            self.assertTrue(4 <= loop <= 8, loop)
        self.assertTrue(24 <= A.WANDER <= 48)
        self.assertIn(f'dur="{A.WANDER:g}s"', night, "the glint wandering over the hoard")

    def test_its_top_centre_is_kept_for_the_months_mark(self):
        """On every header, wide and on a phone, as December's design and kept all year, the lintel's spirals and the
        icicles under it pause for the month's mark, each run of them ending with a whole one on either side of the
        mark's box and the two units round it, and no scene reaches into those columns over the mark's foot."""
        n = MEDIEVAL.mark_size
        spirals = A._motifs([(i, j) for j, row in enumerate(A.SPIRALS) for i, ch in enumerate(row) if ch == "#"])
        for held in (HELD, SET):
            for name in ("kit", "least", "most"):
                h, _ = contents(KEY)[name]
                for code in ("H1", "H2", "H3"):
                    for wide in (True, False):
                        draw = getattr(held, code.lower() if wide else f"{code.lower()}_narrow")
                        args = (h, False, True) if wide else (h, False)
                        with mock.patch.object(A, "icicles", wraps=A.icicles) as ice:
                            p, pixels = sprites(lambda: draw(*args), "scene", "scene_narrow", "scene_under")
                        what = (name, code, wide, held.day)
                        clear = (p.w // 2 - n // 2 - 2, p.w // 2 - n // 2 + n + 2)
                        self.assertEqual(SET.top_centre(p), clear)
                        inside = (A.SIDE, p.w - A.SIDE)
                        self.assertEqual(cut(laid(p, "frl"), spirals, A.SIDE + 2, len(A.SPIRALS[0]), clear, inside), [],
                                         what)
                        (call,) = [c for c in drawn_on(p, ice) if c.args[3] == A.HEAD_LINTEL]
                        x0, x1, top, night = call.args[1:5]
                        run = min(x1 - x0, A.ICE_RUN)
                        cells, _ = A._icicle_cells(run, top, A.ICE_FOOT, night, call.kwargs.get("seed", 0), p.lite)
                        clusters = A._motifs([xy for xy in cells if xy[1] >= 1])
                        self.assertEqual(cut(laid(p, f"icd{call.kwargs.get('seed', 0)}"), clusters, x0, run, clear,
                                             inside), [], what)
                        self.assertFalse([x for x, _ in p.icicles if clear[0] <= x < clear[1]], what)
                        foot = 10 + n // 2 + 3
                        self.assertFalse([(x, y) for x, y in pixels if clear[0] <= x < clear[1] and y < foot], what)

    def test_its_footer_mark_stands_at_the_right_end_after_the_way_back_up(self):
        """Where a footer has no closing notes, its mark, the dragon's tail round a cup, stands at its right end after
        the way back up."""
        for name in ("profile", "repository", "least"):
            _, f = contents(KEY)[name]
            for night in (False, True):
                p = SET.f1(f, night)
                x0, _ = p.marked_at
                self.assertGreater(x0, max(b[2] for b in p.words), (name, night))

    def test_its_scenes_are_drawn_to_the_collections_measure(self):
        """A phone's H1 leaves at least 48 rows under its words for its barrow, and a phone's H2 and H3 stand the
        dragon's head and the great helm under their words at least 40 rows tall."""
        self.assertGreaterEqual(SET.phone_scene_rows, 48)
        for name in ("kit", "profile", "most"):
            h, _ = contents(KEY)[name]
            for code, draw in (("H2", SET.h2_narrow), ("H3", SET.h3_narrow)):
                p, pixels = sprites(lambda: draw(h, False), "scene_under")
                ys = [y for _, y in pixels]
                self.assertGreaterEqual(max(ys) - min(ys) + 1, 40, (name, code))


class Night(unittest.TestCase):
    def test_what_the_night_alone_shows_stays_out_of_the_day(self):
        """The barrow's dark and the ember of the dragon's breath are the night's; by day the barrow is lit cold by
        the snow at its mouth and neither is drawn."""
        for code in ("H1", "H2", "H3"):
            day = SET.header(code, HEADER, DAY, True, True)
            night = SET.header(code, HEADER, DARK, True, True)
            for band in NIGHT_SKY:
                self.assertNotIn(band, day, (code, "the night's dark"))
            self.assertTrue([band for band in NIGHT_SKY if band in night], code)
            for ember in EMBER[4:]:
                self.assertNotIn(ember, day, (code, "the breath by day"))
        for code in ("H1", "H2"):
            self.assertIn(EMBER[6], SET.header(code, HEADER, DARK, True, True), (code, "the ember in its nostrils"))
        for code, draw in (("H1", SET.h1), ("H2", SET.h2)):
            with mock.patch.object(A, "breath", wraps=A.breath) as breath:
                draw(HEADER, False, True)
                self.assertFalse(breath.called, code)
                draw(HEADER, True, True)
                self.assertTrue(breath.called, code)

    def test_by_night_the_dragons_own_light_reaches_across_the_floor_and_up_the_wall(self):
        """By night the ember of the breath pools across the floor before the dragon and catches the coins along it,
        the moon lays a cold shaft across the floor in at the mouth, and every pool and shaft is laid over the walls
        once they are built, the dressed stones the words are on taking only a little of it; by day none of it is
        drawn."""
        for night in (False, True):
            with mock.patch.object(A, "breath", wraps=A.breath) as breath, \
                    mock.patch.object(A, "lamp", wraps=A.lamp) as lamp, \
                    mock.patch.object(A, "shaft", wraps=A.shaft) as shaft:
                p = SET.h1(HEADER, night, True)
            lit = [m for z, _, m, _ in p.raws if 'mask="url(#lm' in m]
            self.assertEqual(bool(lit), night, "the light laid over the walls")
            self.assertEqual(bool(drawn_on(p, shaft)), night, "the moon's shaft across the floor")
            if night:
                (call,) = drawn_on(p, breath)
                self.assertIsNotNone(call.kwargs.get("floor"), "its light across the floor")
                floor = [c for c in drawn_on(p, lamp) if c.kwargs.get("only") == set(GOLD)]
                self.assertTrue(floor, "the coins along the floor catching it")
                self.assertGreaterEqual(max(c.args[3] for c in floor), 40, "far out across the gold")
                self.assertIn(EMBER[3], lit[0])
                self.assertIn(RAMP["frost"][4], lit[0], "the moon's cold light")
                mask = re.search(r'<mask id="lm\d+">.*?</mask>', p.svg("t", "d")).group(0)
                self.assertIn(f'fill="{RAMP["stone"][4]}"', mask, "the stones the words are on in its shade")

    def test_by_night_the_dragons_eye_glows_amber_as_it_opens(self):
        """In a moving header by night its eye opens amber, and the scales round it come up in its light; by day
        its eye opens gold."""
        for night, iris in ((False, GOLD[5]), (True, RAMP["amber"][5])):
            p = SET.h1(HEADER, night, True)
            opened = p.layers["ey1"]
            self.assertIn(iris, set(opened.values()), night)
            lit = {c for c in opened.values() if c in DRAKE[4:]}
            self.assertEqual(bool(lit), night, (night, "the scales in its light"))

    def test_the_breath_lights_the_scales_and_the_gold_nearest_it(self):
        """A light lays its warmth into what it falls on: the scales and the gold within its reach come up a tone,
        two in its near half, its own pixels and what lies past its reach left as they are."""
        p = Pix(60, 20)
        for x in range(60):
            p.px(x, 10, DRAKE[2])
            p.px(x, 11, GOLD[2])
        A.lamp(p, 5, 10, 20, EMBER[4], {(4, 10)})
        A.lights(p)
        self.assertEqual(p.get(4, 10), DRAKE[2], "its own pixel")
        self.assertEqual(p.get(6, 10), DRAKE[4], "two tones in its near half")
        self.assertEqual(p.get(20, 11), GOLD[3], "a tone further out")
        self.assertEqual(p.get(40, 10), DRAKE[2], "nothing past its reach")
        self.assertEqual(p.lamps, [], "each light laid once")

    def test_the_view_through_the_mouth_is_snow_by_day_and_moonlit_by_night(self):
        """Through the mouth the snowy downs roll away under the sky with a bare tree on the ridge and the thief
        going away up the slope with the cup held high; the moon and a few stars hang over them only by night."""
        for night, sky, snow in ((False, RAMP["frost"][6], "#FFFFFF"), (True, RAMP["night"][0], RAMP["frost"][3])):
            p = Pix(40, 60)
            with mock.patch.object(A, "stamp", wraps=A.stamp) as stamp:
                end = A._view(p, 5, 5, 30, 55, night, False)
            laid = "".join(p.shapes["base"])
            self.assertIn(f'fill="{sky}"', laid, night)
            self.assertIn(f'fill="{snow}"', laid, night)
            self.assertTrue(end, "the thief going away over the snow")
            self.assertIn(GOLD[6], set(p.layers["base"].values()), "the cup he took, held up")
            arts = stamped(p, stamp)
            self.assertIn(A.THIEF, arts)
            self.assertIn(A.TREE, arts, "the bare tree on the ridge")
            self.assertEqual(A.MOON in arts, night, "the moon by night only")
            q = Pix(40, 60)
            A._view(q, 5, 5, 30, 55, night, True)
            stars = {c for n, L in q.layers.items() if n.startswith("tw") for c in L.values()}
            self.assertEqual(bool(stars & {RAMP["frost"][5], RAMP["frost"][6]}), night, "a few stars by night only")


class Titles(unittest.TestCase):
    def test_a_title_is_gold_cloisonne_set_with_garnets(self):
        """Every letter is garnet cut in cells by gold walls, a rim of gold round it; never Alchemist's lead turning
        to gold nor Illuminated's leaf."""
        for theme, k in ((DAY, 0), (DARK, 1)):
            svg = SET.header("H1", HEADER, theme, True, True)
            pattern = re.search(r'<pattern id="pacl\d+[dn]".*?</pattern>', svg).group(0)
            self.assertIn(GOLD[3 + k], pattern, "the gold walls between the cells")
            self.assertIn(GARNET[3 + k], pattern, "the garnets")
            self.assertIn(f'<g stroke="{GOLD[5 + k]}">', svg, "the rim, lit")
        cells = {A.cell_fill(r, c, 2, False) for r in range(14) for c in range(4)}
        self.assertTrue(cells & set(GOLD) and cells & set(GARNET))
        self.assertFalse(cells - set(GOLD) - set(GARNET), "gold and garnet only")

    def test_the_glint_crosses_the_title_only_in_a_wide_moving_header(self):
        moving = SET.header("H1", HEADER, DAY, True, True)
        self.assertIn('<clipPath id="gl', moving, "the glint's window")
        self.assertRegex(moving, r'values="-?\d+ 0;\d+ 0;\d+ 0" keyTimes="0;\.4;1"', "it crosses and rests")
        for still in (SET.header("H1", HEADER, DAY, True, False), SET.header("H1", HEADER, DAY, False, False)):
            self.assertNotIn('<clipPath id="gl', still)


class Icicles(unittest.TestCase):
    def test_icicles_hang_from_the_lintel_never_a_row_of_dots(self):
        """The icicles are a tile of tapering spikes of ice hung from the lintel, the longest reaching no lower than
        two rows over the highest a title is set, and a drop gathers on one and falls only in a wide moving
        header."""
        q = Pix(415, 40)
        A.icicles(q, A.SIDE, q.w - A.SIDE, A.HEAD_LINTEL, False)
        self.assertTrue(q.icicles, "the tips a drop can gather on")
        self.assertLessEqual(max(y for _, y in q.icicles), A.ICE_FOOT)
        p = SET.h1(HEADER, False, True)
        drops = sorted(n for n in p.meta if p.meta[n][2] and p.meta[n][2][0] == "seq" and n.startswith("dr"))
        self.assertGreaterEqual(len(drops), 4, "the drop gathering, swelling, falling, splashing")
        cells, _ = A._icicle_cells(A.ICE_RUN, A.HEAD_LINTEL, A.ICE_FOOT, False)
        lengths = {}
        for (x, y) in cells:
            lengths[x] = max(lengths.get(x, 0), y)
        self.assertGreaterEqual(max(lengths.values()), 8, "spikes, not dots")
        self.assertIn('<pattern id="icd', SET.header("H1", HEADER, DAY, True, True), "a tile of icicles")
        still = SET.header("H1", HEADER, DAY, True, False)
        self.assertNotIn("<animate", still, "the drop kept on its tip in a still file")


class Dragon(unittest.TestCase):
    def test_the_dragon_sleeps_its_eye_half_opening_its_smoke_rising_and_a_coin_sliding(self):
        """In a moving header the dragon's eye lifts open on its gold and shuts again, its smoke curls up in three
        frames and a coin slips down the heap; a still drawing keeps one curl of smoke, its eye shut and no coin
        moving."""
        moving = SET.h1(HEADER, False, True)
        seqs = {n for n in moving.meta if moving.meta[n][2] and moving.meta[n][2][0] == "seq"}
        self.assertTrue({"ey0", "ey1", "ey2"} <= seqs, "the eye")
        self.assertTrue({"sm0", "sm1", "sm2"} <= seqs, "the smoke")
        coin = [m for _, _, m, s in moving.raws if "animateTransform" in m and not s]
        self.assertTrue(coin, "the coin sliding")
        still = SET.h1(HEADER, False, False)
        seqs = {n for n in still.meta if still.meta[n][2] and still.meta[n][2][0] == "seq"}
        self.assertFalse([n for n in seqs if n.startswith(("ey", "sm"))], "its eye shut")
        self.assertTrue(still.layers.get("sm"), "one curl of smoke")
        self.assertNotIn("animateTransform", still.svg("t", "d", still=True), "the coin at rest")

    def test_the_hoard_is_a_mountain_of_coins_with_its_treasures_and_gems(self):
        """The dragon coils round a mountain of coins that pours down before it to the floor: a sword driven into it
        with its garnet pommel, an open chest spilling its coins, a round shield with its boss, the helmet, a
        drinking horn, goblets and the crown lying on it, and gems in garnet, emerald and sapphire, as many as the
        room the words leave holds."""
        for h in (HEADER, BARE):
            with mock.patch.object(A, "stamp", wraps=A.stamp) as stamp, \
                    mock.patch.object(A, "jewel", wraps=A.jewel) as jewel, \
                    mock.patch.object(A, "chest", wraps=A.chest) as chest:
                p = SET.h1(h, False, True)
            arts = stamped(p, stamp)
            for piece in ("CUP", "SWORD", "SHIELD", "HELMET", "HORN", "GOBLET", "CROWN"):
                self.assertIn(getattr(A, piece), arts, piece)
            self.assertTrue(drawn_on(p, chest), "the open chest")
            self.assertEqual({c.args[3] for c in drawn_on(p, jewel)}, {"garnet", "emerald", "sapphire"})
            self.assertIn('fill="url(#cnd0)"', p.svg("t", "d"), "the coins")
        with mock.patch.object(A, "lair", wraps=A.lair) as lair, \
                mock.patch.object(A, "_coins", wraps=A._coins) as coins:
            p = SET.h1(BARE, False, True)
        x0c, x1, top, g, night, motion, nx, L, tail = drawn_on(p, lair)[0].args[1:]
        mountain = drawn_on(p, coins)[0].args[1]
        self.assertLessEqual(min(mountain), nx - 40, "pouring down before it to the floor")
        self.assertGreaterEqual(max(mountain), x1, "heaped to the wall behind it")
        self.assertLessEqual(min(mountain.values()), top + (g - top) // 3, "a mountain filling its coil")

    def test_a_glint_wanders_over_the_gold_by_day_and_by_night(self):
        """In a moving header a glint of light swells and fades on one spot of the gold after another, by day and
        by night; a still drawing keeps it caught on one."""
        for night in (False, True):
            moving = SET.h1(HEADER, night, True)
            wander = [m for z, _, m, s in moving.raws if "<use href=" in m and "animateTransform" in m and s]
            self.assertTrue(wander, night)
            steps = re.search(r'type="translate" values="([^"]+)"', wander[0]).group(1).split(";")
            self.assertGreaterEqual(len(set(steps)), 6, "from spot to spot")
            still = SET.header("H1", HEADER, DARK if night else DAY, True, False)
            self.assertNotIn("<animate", still)

    def test_the_dragon_is_the_showpiece_coiled_round_and_over_its_hoard(self):
        """The dragon fills the room the words leave at the right from the icicles to the floor: its back arched over
        its hoard with its wing folded on it and its spines along it, its head as large as the room allows resting
        on its forelegs, and where the words leave the floor clear its tail swept out along it toward the middle,
        past the cup and the spilt coins."""
        most, _ = contents(KEY)["most"]
        for h, least in ((HEADER, 36), (BARE, 32), (most, 32)):
            with contextlib.ExitStack() as stack:
                spies = {n: stack.enter_context(mock.patch.object(A, n, wraps=getattr(A, n)))
                         for n in ("lair", "wing", "spines", "paw", "head", "treasure")}
                p = SET.h1(h, False, True)
            (call,) = drawn_on(p, spies["lair"])
            x0c, x1, top, g, night, motion, nx, L, tail = call.args[1:]
            self.assertGreaterEqual(L, least, "its head")
            self.assertGreaterEqual(g - top, min(70, g - A.ICE_FOOT - 3), "from the icicles to the floor")
            self.assertGreaterEqual(x1 - x0c, 48, "the room at the right")
            self.assertEqual(len(drawn_on(p, spies["wing"])), 1, "its wing folded on its back")
            self.assertGreaterEqual(len(drawn_on(p, spies["spines"])), 2, "its spines along its back and neck")
            self.assertEqual(len(drawn_on(p, spies["paw"])), 2, "its forelegs, its head resting on them")
            self.assertEqual(len(drawn_on(p, spies["head"])), 1)
            if h is not most:
                cup = next(c for c in drawn_on(p, spies["treasure"]) if c.args[3] is A.CUP)
                self.assertLess(tail, cup.args[1], "its tail swept on past the cup")
        with mock.patch.object(A, "lair", wraps=A.lair) as lair:
            p = SET.h1(BARE, False, True)
        self.assertLessEqual(drawn_on(p, lair)[0].args[9], p.w // 2 + 12, "toward the middle")

    def test_the_dragon_never_reads_as_a_blob_against_its_gold(self):
        """Its scales run from a dark underside to edges lit almost white, and its belly is plated in pale ivory by
        day and lit gold from the hoard under it by night."""
        real = A.scales
        for night, belly in ((False, A.BONE), (True, GOLD)):
            laid = set()

            def watch(p, *a, **k):
                before = dict(p.layers["base"])
                real(p, *a, **k)
                laid.update(c for xy, c in p.layers["base"].items() if before.get(xy) != c)
            with mock.patch.object(A, "scales", watch):
                SET.h1(HEADER, night, True)
            k = -1 if night else 0
            self.assertTrue({DRAKE[0], DRAKE[1]} <= laid, (night, "its outline and its shadowed underside"))
            self.assertIn(DRAKE[6 + k], laid, (night, "the lit edges of its scales"))
            self.assertTrue({belly[4 + k], belly[5 + k]} & laid, (night, "its belly"))

    def test_the_mouth_is_a_passage_graves_great_stones_carved_with_spirals(self):
        """At the left the barrow's mouth stands between its massive carved jambs under a deep capstone carved with
        the three spirals, the snow blown in across the floor, and through it the thief, near the door and sixteen
        units tall, goes away over the downs with the cup held high, his footprints going out behind him over the
        snow; the moon over the snow by night."""
        self.assertGreaterEqual(len(A.THIEF) - 4, 16, "the thief from his hood to his feet")
        for night in (False, True):
            with mock.patch.object(A, "mouth", wraps=A.mouth) as mouth, \
                    mock.patch.object(A, "footprints", wraps=A.footprints) as prints, \
                    mock.patch.object(A, "_rock", wraps=A._rock) as rock, \
                    mock.patch.object(A, "stamp", wraps=A.stamp) as stamp:
                p = SET.h1(HEADER, night, True)
            self.assertEqual(len(drawn_on(p, mouth)), 1, night)
            self.assertEqual(len(drawn_on(p, prints)), 2, "over the floor and out over the snow")
            arts = stamped(p, stamp)
            self.assertIn(A.THIEF, arts, "the thief with the cup")
            self.assertEqual(A.MOON in arts, night, "the moon over the snow by night only")
            self.assertTrue(p.layers.get("prints"), "his footprints, laid over the light on the snow")
            stones = drawn_on(p, rock)
            self.assertEqual(len(stones), 3, "two jambs and the capstone")
            cap = [c for c in stones if c.kwargs.get("carve") is A.TRIPLE_SPIRAL]
            self.assertTrue(cap, "the three spirals across the capstone")
            x0, y0, x1, y1 = cap[0].args[1:5]
            self.assertGreaterEqual((x1 - x0, y1 - y0), (44, 19), "a massive stone")

    def test_where_the_words_leave_the_floor_clear_the_golden_standard_stands(self):
        """Between the mouth and the hoard, where the words leave the floor its room, the golden standard of the
        poem stands over its own heap of gold with a chest beside it, shining with its own light by night; where
        the words take the floor it is left out."""
        for night in (False, True):
            with mock.patch.object(A, "standard", wraps=A.standard) as standard, \
                    mock.patch.object(A, "lamp", wraps=A.lamp) as lamp:
                p = SET.h1(BARE, night, True)
            self.assertEqual(len(drawn_on(p, standard)), 1, night)
            self.assertEqual(bool([c for c in lamp.call_args_list if c.args[4] == GOLD[4]]), night, "its own light")
        with mock.patch.object(A, "standard", wraps=A.standard) as standard:
            p = SET.h1(HEADER, False, True)
        self.assertFalse(drawn_on(p, standard))


class Scenes(unittest.TestCase):
    def test_an_h2_is_the_dragons_great_head_on_its_gold_its_eye_opening(self):
        """A section's scene is the dragon's head itself, large and horned, its jaw resting on the coins, its teeth
        over its lip, its smoke rising and in a moving header its great eye opening, with only as much neck as the
        room allows."""
        for night in (False, True):
            with mock.patch.object(A, "head_on_gold", wraps=A.head_on_gold) as head, \
                    mock.patch.object(A, "_coins", wraps=A._coins) as coins, \
                    mock.patch.object(A, "spines", wraps=A.spines) as spines:
                p = SET.h2(HEADER, night, True)
            (call,) = drawn_on(p, head)
            nx, L, x1, g = call.args[1:5]
            self.assertGreaterEqual(L, 60, "large")
            self.assertLessEqual(x1 - nx, round(1.72 * L), "only so much of its neck as the room allows")
            self.assertTrue(drawn_on(p, spines), "the spines along its neck")
            jaw = g - 4
            under = [c for c in drawn_on(p, coins) if all(t <= jaw + 3 for x, t in c.args[1].items()
                                                         if nx + 8 <= x <= nx + 0.6 * L)]
            self.assertTrue(under, "its jaw resting on the coins")
            seqs = {n for n in p.meta if p.meta[n][2] and p.meta[n][2][0] == "seq"}
            self.assertTrue({"be0", "be1", "be2"} <= seqs, "its great eye opening and shutting")
            self.assertTrue({"sm0", "sm1", "sm2"} <= seqs, "its smoke")
            teeth = {c for (x, y), c in A._head(L, night) if c == A.BONE[5 + (-1 if night else 0)]}
            self.assertTrue(teeth, "its teeth")

    def test_an_h3_is_the_great_helm_on_its_heap_and_the_cup(self):
        """A strip's scene is the great helm of the ship burial, drawn large with its face mask, its brows set with
        garnets and the dragon over the brow, raised on a heap of coins with the great gold buckle, the shoulder
        clasps, a sword and a drinking horn heaped on the gold before it and the coins spilt along the floor under
        the words; the cup beside the title or, where the title leaves it no room, standing on the coins before the
        helm; by night the gleam of the gold lights the helm."""
        self.assertGreaterEqual((len(A.GREAT_HELM[0]), len(A.GREAT_HELM)), (25, 30), "the helm drawn large")
        helm = "".join(A.GREAT_HELM)
        self.assertTrue({"r", "R", "Z", "G", "k"} <= set(helm), "gold and garnet, and the dark of its eyes")
        for h in (HEADER, BARE):
            for night in (False, True):
                with mock.patch.object(A, "helm_on_gold", wraps=A.helm_on_gold) as helm_on, \
                        mock.patch.object(A, "treasure", wraps=A.treasure) as treasure, \
                        mock.patch.object(A, "lamp", wraps=A.lamp) as lamp:
                    p = SET.h3(h, night, True)
                (call,) = drawn_on(p, helm_on)
                self.assertIs(call.kwargs.get("art"), A.GREAT_HELM)
                laid = [c.args[3] for c in drawn_on(p, treasure)]
                for piece in ("BUCKLE", "CLASPS", "BLADE", "HORN"):
                    self.assertIn(getattr(A, piece), laid, (piece, night))
                self.assertTrue(A.CUP in laid or getattr(p, "marked", False), "the cup")
                gleam = [c for c in drawn_on(p, lamp) if set(RAMP["silver"]) <= (c.kwargs.get("only") or set())]
                self.assertEqual(bool(gleam), night, "the gold's gleam on the helm by night")
                self.assertGreater(call.args[1] - call.kwargs["left"], 90, "the coins spilt along the floor")


class Walls(unittest.TestCase):
    def test_a_header_is_walled_in_drystone_with_its_words_on_dressed_stones(self):
        """Every header, wide or on a phone, is walled in drystone courses from the lintel to its rule, every block of
        its words on a great dressed stone of even face, the walling never within its words' box, and the corbelled
        roof's great flat stones along the top under the lintel; by day lit cold from the mouth and warm from the
        gold, by night dark but where its lights fall. A footer and an element keep the chalk with its flints."""
        for code, draw in (("H1", SET.h1), ("H2", SET.h2), ("H3", SET.h3)):
            for night in (False, True):
                with mock.patch.object(A, "wall", wraps=A.wall) as wall:
                    p = draw(HEADER, night, True)
                (call,) = drawn_on(p, wall)
                svg = p.svg("t", "d")
                self.assertIn(f'<pattern id="ds{"n" if night else "d"}"', svg, (code, night))
                calm = p.stones
                for (a, b, c, d) in (w for w in p.words if w[3] <= call.args[5]):
                    inside = {(x, y) for x in range(a, c) for y in range(b, d)}
                    self.assertLessEqual(inside, calm | {(x, y) for (x, y) in inside if y >= call.args[5]},
                                         (code, night, "every word on a dressed stone"))
                self.assertIn(RAMP["stone"][1 if night else 5], set(p.layers["wall"].values()), "the roof's stones")
                self.assertEqual(f'fill="{GOLD[6]}" fill-opacity' in svg, not night, "the gold's warmth by day")
        for night in (False, True):
            with mock.patch.object(A, "wall", wraps=A.wall) as wall:
                p = SET.h1_narrow(HEADER, night)
            self.assertTrue(drawn_on(p, wall), ("a phone's header", night))
        _, f = contents(KEY)["kit"]
        with mock.patch.object(A, "wall", wraps=A.wall) as wall:
            p = SET.f1(f, False)
        self.assertFalse(drawn_on(p, wall), "a footer keeps its chalk")
        self.assertIn('<pattern id="ps"', p.svg("t", "d"), "and its flints")

class Phones(unittest.TestCase):
    def test_every_sprite_keeps_two_units_clear_of_every_word_on_a_phone(self):
        """On a phone the barrow, the dragon's head, the helm, the scenes under the words, the icicles, the section
        mark and the coins along the rule are built to the rows the words leave free: no pixel of theirs lies
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
        drawers = {"H1": SET.h1, "H2": SET.h2, "H3": SET.h3}
        for name, (h, _) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    p, pixels = sprites(lambda: drawer(h, night, True), "scene", "garland", "section_mark",
                                        "strip_mark", "rule_decor")
                    hits = off_words(p, pixels)
                    self.assertEqual(hits[:6], [], (name, code, night, len(hits)))

    def test_what_the_last_pass_lays_keeps_clear_of_every_word(self):
        """The drop, the night's light on what stands near it and the dial's dragon keep the same two units."""
        for name, (h, _) in contents(KEY).items():
            for code, drawer in (("H1", SET.h1), ("H2", SET.h2), ("H3", SET.h3)):
                p, pixels = sprites(lambda: drawer(h, True, True), "finish")
                self.assertEqual(off_words(p, pixels)[:6], [], (name, code))

    def test_every_phone_header_of_every_shared_content_stands_a_scene(self):
        """Every phone header of every shared content, by day and by night, drawn as the kit draws it, stands a scene
        of the set's on the drawing its file is made from: the barrow on an H1, the dragon's head or the dragon on
        its hoard on an H2 and the great helm on its gold on an H3, beside the words where they leave it room and
        under them where they leave none."""
        pieces = {"H1": ("phone_barrow",), "H2": ("head_peeking", "phone_section"),
                  "H3": ("helm_on_gold", "phone_strip")}
        names = sorted({n for ns in pieces.values() for n in ns})
        for name, (h, _) in contents(KEY).items():
            for code, wanted in pieces.items():
                for theme in (DAY, DARK):
                    _, p, spies = served(lambda: SET.header(code, h, theme, False, False), names)
                    self.assertTrue([n for n in wanted if drawn_on(p, spies[n])], (name, code, theme["name"]))

    def test_where_the_words_leave_no_room_beside_them_the_scene_stands_under_them(self):
        """A title as wide as the phone with a page of words under it leaves the dragon's head no room beside them,
        so the header is laid out again with rows of its own under the words, and there the dragon's great head on its
        gold with the helmet and the crown spilt before it stands whole, two units clear of every word; so does the
        head where the column beside the words is too narrow for a head that reads. The great helm stands taller
        than the strip beside any title, so on every phone's H3 it stands under the words, raised on its heap with
        its cup and the coins spilt along the floor. A phone whose scene stood beside its words is laid out just as
        the kit lays it out."""
        whole = {"H2": ("phone_section", "head_on_gold"), "H3": ("phone_strip", "helm_on_gold")}
        for name, codes in (("profile", ("H2", "H3")), ("most", ("H2", "H3")), ("kit", ("H2", "H3")),
                            ("least", ("H3",))):
            h, _ = contents(KEY)[name]
            for code, kinds in ((c, whole[c]) for c in codes):
                draw, own = getattr(SET, f"{code.lower()}_narrow"), getattr(Holiday, f"{code.lower()}_narrow")
                for night in (False, True):
                    with contextlib.ExitStack() as stack:
                        spies = {k: stack.enter_context(mock.patch.object(A, k, wraps=getattr(A, k))) for k in kinds}
                        p, pixels = sprites(lambda: draw(h, night), "scene_under")
                    self.assertEqual([k for k in kinds if not drawn_on(p, spies[k])], [], (name, code, night))
                    self.assertEqual(off_words(p, pixels), [], (name, code, night))
                    self.assertEqual(p.h - own(SET, h, night).h, SET.PHONE_ROWS[code], (name, code, night))
        for name, codes in (("least", ("H2",)),):
            h, _ = contents(KEY)[name]
            for code in codes:
                draw, own = getattr(SET, f"{code.lower()}_narrow"), getattr(Holiday, f"{code.lower()}_narrow")
                for night in (False, True):
                    with mock.patch.object(SET, "scene_under", wraps=SET.scene_under) as under:
                        mine = draw(h, night).svg("t", "d", still=True)
                    self.assertFalse(under.called, (name, code, night))
                    self.assertEqual(mine, own(SET, h, night).svg("t", "d", still=True), (name, code, night))

    def test_a_phones_barrow_has_its_mouth_and_its_dragon(self):
        for name in ("kit", "profile", "least", "most"):
            h, _ = contents(KEY)[name]
            with mock.patch.object(A, "mouth", wraps=A.mouth) as mouth, \
                    mock.patch.object(A, "lair", wraps=A.lair) as lair:
                p = SET.h1_narrow(h, False)
            self.assertTrue(drawn_on(p, mouth) and drawn_on(p, lair), name)


class Longest(unittest.TestCase):
    PIECES = ("lair", "head", "wing", "paw", "spines", "mouth", "_view", "_rock", "standard", "head_on_gold",
              "helm_on_gold", "frame", "icicles", "cloisonne_title", "glint", "breath", "smoke", "slide", "drip",
              "drift", "footprints", "treasure", "set_out", "wall", "light")

    def test_the_longest_page_keeps_its_whole_scene_and_its_motion_within_the_budget(self):
        """Every field at its longest, the wide H1, H2 and H3, by day and by night, drawn as the kit draws them, come
        within the budget and still move, and the drawing each is made from has every piece the drawing at full
        weight has, each where it stood: the dragon coiled on its hoard with its wing, its spines, its forelegs and
        its head and its treasures, the barrow's mouth and its stones, the dragon's head on its gold, the helm on its
        heap, the walls, the stones and the icicles, the title in gold cloisonne with its glint, the drop, the sliding
        coin, and by night the breath and the light laid over the walls. A drawing made lighter thins only the
        texture between them."""
        most, _ = contents(KEY)["most"]

        def pieces(spies, p):
            return sorted(re.sub(r"'tt\d+'", "'tt'", repr((n, c.args[1:], sorted(c.kwargs.items()))))
                          for n, spy in spies.items() for c in drawn_on(p, spy))
        for code, named in (("H1", {"lair", "head", "wing", "paw", "mouth", "slide"}), ("H2", {"head_on_gold", "head"}),
                            ("H3", {"helm_on_gold"})):
            for theme in (DAY, DARK):
                svg, p, spies = served(lambda: SET.header(code, most, theme, True, True), self.PIECES)
                with mock.patch.dict(BUDGET, {"header": 10 ** 9}):
                    _, whole, full = served(lambda: SET.header(code, most, theme, True, True), self.PIECES)
                where = (code, theme["name"])
                self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"], where)
                self.assertIn("<animate", svg, where)
                self.assertEqual(pieces(spies, p), pieces(full, whole), where)
                self.assertLessEqual(named, {n for n, spy in spies.items() if drawn_on(p, spy)}, where)


class Footers(unittest.TestCase):
    def test_every_footer_ends_in_a_drift_of_coins_with_the_tail_round_a_cup(self):
        """Every footer ends in a drift of coins along its foot, heaped wherever the cells leave room, and the
        dragon's tail tip curled round a cup stands on the coins at the corner of the notes, on a phone as on a
        wide sheet, drawn small where the words leave it only a narrow corner, its gold glinting by night."""
        for name, (_, f) in contents(KEY).items():
            for draw in (SET.f1, SET.f2, SET.f1_narrow, SET.f2_narrow):
                for night in (False, True):
                    with mock.patch.object(A, "stamp", wraps=A.stamp) as stamp:
                        p = draw(f, night)
                    self.assertIn('fill="url(#cn', p.svg("t", "d"), (name, draw.__name__, night, "the coins"))
                    marks = [a for a in stamped(p, stamp) if a is A.TAIL_CUP or a is A.TAIL_CUP_S]
                    self.assertEqual(len(marks), 1, (name, draw.__name__, night, "the mark"))
                    if night:
                        x0, y0 = p.marked_at
                        self.assertEqual(p.get(x0 + 4, y0 + 3), X["glint"], (name, draw.__name__))

    def test_the_drift_and_the_mark_keep_clear_of_every_word(self):
        for name, (_, f) in contents(KEY).items():
            for draw in (SET.f1, SET.f2, SET.f1_narrow, SET.f2_narrow):
                for night in (False, True):
                    p, pixels = sprites(lambda: draw(f, night), "_footed")
                    self.assertEqual(off_words(p, pixels, margin=1)[:6], [], (name, draw.__name__, night))

    def test_a_link_is_a_struck_coin_on_a_strap_of_garnet_and_a_small_file(self):
        for i, label in enumerate(("Issues", "Pull Requests", "Releases", "Actions")):
            for theme in (DAY, DARK):
                svg = SET.link(label, theme, i)
                self.assertLess(len(svg.encode("utf-8")), 2500, (label, theme["name"]))
                self.assertIn(GARNET[2], svg, "the strap")
                self.assertIn(GOLD[0], svg, "the coin's rim")
        devices = {A.LINK_ORDER[i % len(A.LINK_ORDER)] for i in range(4)}
        self.assertEqual(len(devices), 4, "each its own device")
        for device in A.LINK_DEVICES.values():
            self.assertEqual((len(device), len(device[0])), (7, 7))


class Badges(unittest.TestCase):
    def test_a_gold_rim_and_a_row_of_garnets_lie_along_every_badges_top_with_the_letters_under_it(self):
        for style in BADGE_STYLES:
            corner = BADGE_STYLES[style]["corner"]
            drawn = [SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                       SET.badge_states()["green"])]
            drawn += [SET.plate_badge(style, "License", "MIT", "scale", mode) for mode in ("day", "night")]
            for p in drawn:
                top = [p.get(x, 0) for x in range(p.w) if inside(x, 0, p.w, p.h, corner)]
                self.assertTrue(top and set(top) <= {GOLD[5], GOLD[4]}, (style, "the gold rim"))
                cells = {p.get(x, 1) for x in range(p.w) if inside(x, 1, p.w, p.h, corner)}
                self.assertTrue({GARNET[4], GOLD[3]} <= cells, (style, "garnets between gold walls"))
                self.assertTrue(all(y >= 2 for _, _, _, y, _ in p.uses["base"]), "the letters sit under it")

    def test_a_counters_numerals_hold_4_5_on_their_ingot(self):
        """Every numeral holds 4.5:1 on its ingot, a leading nought fainter; and the ingot lies on a layer under the
        drawing's own, so a numeral is struck over it whatever its colour."""
        for night in (False, True):
            q = Pix(20, 20)
            SET.counter_cell(q, 2, 2, night)
            self.assertFalse(q.layers["base"], night)
            face = q.layers["far"][(7, 8)]
            self.assertIn(face, GOLD, "gold")
            self.assertGreaterEqual(contrast(SET.counter_ink(night, False), face), 4.5, night)
            self.assertGreaterEqual(contrast(SET.counter_ink(night, True), face), 1.5, night)
            k = SET.ink(night)
            self.assertNotIn(SET.counter_ink(night, False), {k["tag_ink"], k["muted"], k["body"]})


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
        """The kit's own lines, the samples (the profile also with a motto and a note, the heaviest of its kind) and
        the least a page can say, drawn as December's design with the month's mark, are served at full weight, a wide
        moving header with its motion, and every file keeps 1.5 KB under its budget; only the most a page can say is
        served lighter."""
        ordinary = {name: contents(KEY)[name] for name in ("kit", "repository", "profile", "least")}
        h, f = ordinary["profile"]
        ordinary["noted"] = (h.with_(motto="Built to be rebuilt.", notes=("All times in EST.",)), f)
        lite, canvas = [], type(SET).canvas
        with mock.patch.object(type(SET), "canvas", lambda self, w, hh: lite.append(self._lite) or canvas(self, w, hh)):
            for name, (h, f) in ordinary.items():
                for theme in (DAY, DARK):
                    for code in ("H1", "H2", "H3"):
                        for wide, motion in ((True, True), (True, False), (False, False)):
                            what = (name, code, theme["name"], wide, motion)
                            svg = HELD.header(code, h, theme, wide, motion)
                            self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"] - 1500, what)
                            self.assertEqual("<animate" in svg, wide and motion, what)
                    for code in ("F1", "F2"):
                        for wide in (True, False):
                            svg = HELD.footer(code, f, theme, wide, False)
                            self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["footer"] - 1500, (name, code))
        self.assertFalse(any(lite), "nothing ordinary is drawn lighter")

    def test_text_colours_hold_4_5_on_the_paper_and_every_row_of_the_night(self):
        """Every text colour holds 4.5:1 on the chalk and on every bed of the wall by day, on every row of the
        night, and the tag's letters on the tag; a link's letters on their strap."""
        for night in (False, True):
            k = SET.ink(night)
            p = Pix(415, 200)
            grounds = {SET.bg_at(p, night, y) for y in range(p.h)}
            grounds |= set(A._strata_cells(night).values())
            if night:
                # a dressed stone's face, and the most light that falls on it through the stones' shade in the mask
                stone = RAMP["earth"][2]
                grounds |= {stone, mix(stone, EMBER[3], 0.12), mix(stone, RAMP["frost"][4], 0.12)}
            for role in ("title", "body", "muted", "accent"):
                for ground in grounds:
                    self.assertGreaterEqual(contrast(k[role], ground), 4.5, (night, role, ground))
            self.assertGreaterEqual(contrast(k["tag_ink"], k["tag"]), 4.5, (night, "tag"))
            fill, _, ink, _ = SET.link_colours(night)
            self.assertGreaterEqual(contrast(ink, fill), 4.5, (night, "a link's letters"))

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

    def test_the_rosters_avatars_are_bracteates_never_initials(self):
        """A contributor is a gold bracteate on its loop, its field enamelled in their own colour and a head stamped
        on it, the colour and the head following from their name; a bot's is stamped with its icon."""
        for night in (False, True):
            k = -1 if night else 0
            p = Pix(40, 40)
            before = len(p.words)
            SET.avatar(p, 20, 20, 0, {"initials": "IV", "name": "Imogen Vale"}, night)
            self.assertEqual(len(p.words), before, "no letters")
            drawn = set(p.layers["base"].values())
            self.assertTrue({GOLD[6 + k], GOLD[1]} <= drawn, "the beaded gold rim")
            enamels = [RAMP[e][2 + k] for e in A.ENAMELS]
            self.assertEqual(len(drawn & set(enamels)), 1, "its field enamelled")
        q = Pix(40, 40)
        SET.avatar(q, 20, 20, 0, {"initials": "IV", "name": "Imogen Vale"}, False)
        r = Pix(40, 40)
        SET.avatar(r, 20, 20, 3, {"initials": "IV", "name": "Imogen Vale"}, False)
        self.assertEqual(q.layers["base"], r.layers["base"], "the same person the same wherever they stand")
        heads = set()
        for name in ("Imogen Vale", "Tomas Okafor", "Wren Castellan", "Ada", "Bo"):
            s = Pix(40, 40)
            SET.avatar(s, 20, 20, 0, {"initials": "XX", "name": name}, False)
            heads.add(tuple(sorted(s.layers["base"].items())))
        self.assertGreaterEqual(len(heads), 4, "people told apart")
        bot = Pix(40, 40)
        SET.avatar(bot, 20, 20, 0, {"name": "dependabot", "icon": "gear"}, False)
        self.assertEqual(len(bot.words), 0)
        self.assertIn(GOLD[5], set(bot.layers["base"].values()), "its icon stamped in gold")

    def test_the_histogram_stacks_gold_coins_and_marks_the_busiest_with_a_garnet(self):
        for night in (False, True):
            k = -1 if night else 0
            p = Pix(40, 60)
            SET.hist_bar(p, 10, 50, 10, 30, night)
            col = [p.get(14, y) for y in range(20, 50)]
            self.assertIn(GOLD[1], col, "the line under each coin")
            self.assertIn(GOLD[5 + k], col, "each coin's rim lit")
            self.assertEqual(p.get(14, 50), None, "standing on the base")
            q = Pix(20, 20)
            SET.peak_mark(q, 5, 5, night)
            self.assertIn(GARNET[5 + k], set(q.layers["base"].values()))

    def test_a_card_is_a_gold_plaque_with_its_icon_in_gold_on_garnet(self):
        """A schematic's card is a plaque of gold, its raised rim lit along its top and left, and down its left a
        slab of garnet in gold walls, cut in cells, with the card's icon worked in gold on it; never a plain box with a
        coloured tab. Its wire is a chain of gold."""
        for night in (False, True):
            k = -1 if night else 0
            p = Pix(120, 40)
            x, y, w, h = 4, 4, 104, 28
            SET.node(p, night, x, y, w, h, {"title": "Probes", "path": "crates/probe", "icon": "grid"}, seed=1)
            self.assertEqual(p.get(x + 20, y + 1), GOLD[5 + k], "the rim, lit")
            self.assertEqual(p.get(x + 50, y + h - 1), GOLD[1] if not night else GOLD[2], "its dark edge")
            slab = {p.get(xx, yy) for xx in range(x + 2, x + 12) for yy in range(y + 2, y + h - 2)}
            self.assertTrue({GARNET[4 + k], GOLD[6 + k]} <= slab, "the icon in gold on the garnet")
            self.assertNotIn(SET.ink(night)["body"], slab, "the layout's icon taken up")
            q = Pix(60, 20)
            SET.wire(q, night, [(2, 10), (50, 10)])
            line = [q.get(xx, 9) for xx in range(4, 40)]
            self.assertIn(GOLD[5], line, "the links lit along their tops")
            self.assertIn(None, [q.get(xx, 10) for xx in range(4, 40)], "the wall through the rings")

    def test_the_dial_is_an_arm_ring_its_hand_a_dragon(self):
        """The dial is a gold arm ring twisted along its length, its ends dragons' heads with garnet eyes, its ticks
        punched in it; its hub a gold boss set with a garnet; and its hand the layout drew is taken up and laid again
        as a dragon's neck and head, none of the plain hand left."""
        for night in (False, True):
            k = -1 if night else 0
            p = Pix(120, 60)
            SET.dial(p, {"value": 7, "span": 30, "sub": "v1"}, 60, 44, 30, night)
            SET.finish(p, night)
            drawn = set(p.layers["base"].values())
            self.assertNotIn(SET.ink(night)["accent"], drawn, "the plain hand redrawn as a dragon")
            self.assertTrue({DRAKE[4 + k], DRAKE[5 + k]} <= drawn, "its neck in the dragon's scales")
            self.assertTrue({GOLD[2 + k], GOLD[5 + k], GOLD[1]} <= drawn, "the twisted gold")
            self.assertIn(GARNET[5 + k], drawn, "the garnet eyes")

    def test_the_timeline_is_a_trail_of_coins_with_gems_and_the_dragons_eye(self):
        for night in (False, True):
            k = -1 if night else 0
            p = Pix(80, 30)
            SET.timeline_line(p, 4, 60, 15, night)
            self.assertIn(GOLD[6 + k], {p.get(x, y) for x in range(4, 60) for y in (13, 14)}, "coins lit")
            for kind in ("big", "major", "next", "made"):
                q = Pix(30, 30)
                SET.release(q, 15, 15, kind, night)
                self.assertTrue(set(q.layers["base"].values()) & set(GOLD), kind)
            q = Pix(30, 30)
            SET.release(q, 15, 15, "minor", night)
            self.assertIn(RAMP["glass"][4 + k], set(q.layers["base"].values()), "a patch a bead of glass")
            e = Pix(30, 30)
            SET.today_mark(e, 15, 15, night)
            self.assertTrue({DRAKE[0], GOLD[5 + k]} <= set(e.layers["base"].values()), "the dragon's eye")

    def test_the_seal_is_a_brooch_of_gold_and_garnet(self):
        for night in (False, True):
            k = -1 if night else 0
            p = Pix(100, 100)
            SET.rosette(p, 50, 50, 23, 31, 16, night)
            drawn = set(p.layers["base"].values())
            self.assertTrue({GARNET[4 + k], GARNET[2 + k], GOLD[5 + k], GOLD[1]} <= drawn, night)
        svg = SET.element("certificate", E.describe("certificate", ELEMENTS["conformance"]), DAY, "wide")
        self.assertIn(GOLD[6], svg, "its face laid in gold")

    def test_a_placard_is_the_iron_bound_lid_of_a_chest(self):
        """A placard is a chest's lid of ash boards bound round in iron with gilt nails, a gilt angle with a garnet at
        each corner, its words on the boards at 4.5:1."""
        for theme, night in ((DAY, False), (DARK, True)):
            k = -1 if night else 0
            svg = SET.element("placard", E.describe("placard", ELEMENTS["action"]), theme, "wide")
            self.assertIn(f'<pattern id="ash{"n" if night else "d"}"', svg, "the boards")
            self.assertIn(RAMP["iron"][5 + k], svg, "the iron band, lit")
            self.assertIn(GARNET[5 + k], svg, "a garnet at each corner")
            boards = (RAMP["sand"][5], RAMP["sand"][4], RAMP["sand"][6]) if not night else \
                (RAMP["oak"][1], RAMP["oak"][2])
            for ground in boards:
                for role in ("body", "muted"):
                    self.assertGreaterEqual(contrast(SET.ink(night)[role], ground), 4.5, (night, role, ground))


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

    def test_the_live_states_are_gems_emerald_gold_ruby_and_onyx(self):
        states = SET.badge_states()
        self.assertEqual(states["green"][0], RAMP["emerald"][2])
        self.assertEqual(states["yellow"][0], GOLD[4])
        self.assertEqual(states["red"][0], GARNET[3])
        self.assertIn(states["slate"][0], RAMP["flint"])

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
