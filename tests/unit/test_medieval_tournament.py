# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The Tournament set's own rules, which the checks every set shares cannot know: what the night alone shows (the
torches, the lanterns, the pavilions glowing from within, the gold cord's glints) stays out of the day's files; a
title is lettered in painted silk edged in gold cord, with a gleam that runs across it only in a wide moving
header; the valance is dagged silk that ripples, never a row of coloured dots; the joust fills its slot, the near
knight large below under his gold lion and the far one higher and smaller beyond the tilt under his swan, both
lances couched, under the standard of the lists, and meets in a burst of splinters with its coronel spinning away
that comes round only in a wide moving header, by night with sparks and the torch's glint on the plate, its flash
breaking round the far knight; the stand rises in two tiers of ladies and lords under its canopy with the herald
before it, its lanterns lighting their faces by night; a phone with the rows has the joust too; an H3 is the
tiltyard with its quintain, or the crested helm on its post when the title has no room for the helm beside it; every
phone header of every shared content stands a scene of the set's, and a phone's H2 and H3 always stand theirs under
the words at their full height in rows of their own, 44 rows tall or more: the camp beside the lists, the knight at
rest on his great horse, and the tiltyard, the knight charging the quintain; the camp has its knight at rest, his
squire with his lance and his shields at the pavilion's door, lit from within by night, and the camp and the lists
have their pavilions beyond where the words leave room, the camp's no two alike, by its tree of shields, the knight
being armed in its open pavilion large enough to read at 1x, his squire setting the great helm on his head; the
most a page can say keeps its whole scene and its motion within the budget, a drawing made lighter keeping every
piece where it stood; a lantern hangs from the valance by night only, and its light leaves every word its contrast;
every scene, the valance, the marks beside a title, the lanterns and the counter-lists along a rule keep two units
from every word, on a phone and across a wide header; a footer stands on the tilt's barrier, which runs its whole
width with a post at every bay where it stands tall, with the herald's trumpet and lantern at the corner of its
notes, lit by night, and the design's mark, the crested great helm on its post, at the right end of a title block
and beside the scale bar, all of it clear of every word; a link is a banneret, a small file; a schematic's card is
painted silk with its icon on a shield; the dial is the quintain, its hand a lance; the seal is the prize on its
cushion; a gold cord lies along every badge's top; a counter's numerals hold 4.5:1 on the herald's cheque and are
painted over it; and the roster's avatars are crested helms, never initials.
The set is a theme, not a holiday on the calendar, so the checks every registered set shares run here over the set
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
from domain.elements import draw as E
from domain.holidays.designs import Holiday
from domain.holidays.designs.badges import PLATE, STATES, STYLES as BADGE_STYLES, inside
from domain.collections.hand import MEDIEVAL, CollectionSet, check, lab
from domain.collections.medieval_tournament import SET
from domain.collections.medieval_tournament import art as A
from domain.collections.medieval_tournament.palette import NIGHT_SKY, RAMP, SKINS, X
from domain.holidays.pixel import Pix, contrast
from domain.palette import PALETTE

support.install()
KEY = SET.key
HEADER = Header(tone="standard", holiday=KEY)
# A title that fills a header's width on two lines.
LONG = HEADER.with_(title="w" * 40)
FLAME, G, V = RAMP["flame"], RAMP["or"], RAMP["vert"]
SKIN = {c for skin in SKINS for c in skin}
MAY = dt.date(2026, 5, 1)       # a day that makes the design its month's


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


# A symbol drawn as another one turned to face the other way, and a block laid in a pattern, shifted along where it
# carries on a pattern laid further back (as the valance's right run does): what `sprites` reads to know which cells
# they cover.
MIRROR = re.compile(r'<use href="#(q\d+)" transform="matrix\(-1 0 0 1 (\d+) 0\)"/>')
RECT = re.compile(r'<rect x="(-?\d+)" y="(-?\d+)" width="(\d+)" height="(\d+)"[^>]*?'
                  r'(?: transform="translate\((-?\d+) 0\)")?/>')


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
                for x, y, w, h, dx in RECT.findall("".join(shapes[laid.get(L, 0):])):
                    x = int(x) + int(dx or 0)
                    pixels.update((xx, yy) for xx in range(x, x + int(w)) for yy in range(int(y), int(y) + int(h)))
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
    def test_what_the_night_alone_shows_stays_out_of_the_day(self):
        """Flames, the lanterns' light on the canvas, the pavilions glowing from within and the torches' light on what
        stands near them are the night's; by day the torches stand cold."""
        for code in ("H1", "H2", "H3"):
            day = SET.header(code, HEADER, DAY, True, True)
            night = SET.header(code, HEADER, DARK, True, True)
            for flame in (FLAME[6], FLAME[5]):
                self.assertNotIn(flame, day, (code, "a flame by day"))
            self.assertNotIn("flicker", " ".join(str(m) for m in SET.h1(HEADER, False, True).meta.values()), code)
            self.assertIn(FLAME[5], night, (code, "the night's fire"))
            for band in NIGHT_SKY:
                self.assertNotIn(band, day, (code, "the night's canvas"))
            self.assertIn(NIGHT_SKY[0], night, code)
        p = SET.h1(HEADER, True, True)
        self.assertTrue(p.lamps, "the torches, the stand's lanterns and the pavilion's door light what stands near")

    def test_the_pavilions_glow_from_within_by_night(self):
        p = Pix(120, 80)
        A.pavilion(p, 40, 70, True, "purpure", motion=False)
        self.assertIn(FLAME[5], set(p.layers["base"].values()), "the canvas lit from within")
        q = Pix(120, 80)
        A.pavilion(q, 40, 70, False, "purpure", motion=False)
        self.assertNotIn(FLAME[5], set(q.layers["base"].values()))


class Titles(unittest.TestCase):
    def test_a_title_is_painted_silk_edged_in_gold_cord(self):
        for theme, cord in ((DAY, "cordd"), (DARK, "cordn")):
            svg = SET.header("H1", HEADER, theme, True, True)
            self.assertIn(f'<pattern id="{cord}"', svg, "the cord's twist")
            self.assertIn(f'stroke="url(#{cord})"', svg, "laid round the letters")
            self.assertIn('id="pasilk4', svg, "the silk, a band a row of the face")

    def test_the_gleam_runs_across_the_silk_only_in_a_wide_moving_header(self):
        moving = SET.header("H1", HEADER, DAY, True, True)
        self.assertIn('<clipPath id="gl', moving, "the gleam's window")
        self.assertRegex(moving, r'values="-?\d+ 0;\d+ 0;\d+ 0" keyTimes="0;\.45;1"', "it sweeps across and rests")
        for still in (SET.header("H1", HEADER, DAY, True, False), SET.header("H1", HEADER, DAY, False, False)):
            self.assertNotIn('<clipPath id="gl', still)

    def test_the_valance_is_dagged_silk_that_ripples_never_a_row_of_dots(self):
        p = SET.h1(HEADER, False, True)
        ripples = [n for n in p.meta if n.startswith("rip")]
        self.assertEqual(len(ripples), 4, "the dags ripple in four phases, a wave along the valance")
        self.assertTrue(all(p.meta[n][2][0] == "bob" for n in ripples))
        lifts = {tuple(p.meta[n][2][1]) for n in ripples}
        self.assertEqual(len(lifts), 4, "each phase lifts in its own time")
        svg = SET.header("H1", HEADER, DAY, True, True)
        self.assertIn('<pattern id="vah"', svg, "the dags' heads, a tile of silk tongues")
        self.assertIn('<pattern id="vab"', svg, "the band embroidered with its chevron")
        reach = max(y for (_, y, _) in ((x, y, c) for (x, y), c in A._dag_cells(False, False).items()))
        self.assertLessEqual(5 + reach, A.VALANCE_FOOT, "the fringe ends two rows over a title's dimension")


def drawn_on(p, spy) -> list:
    """The calls a spied art function made on the sheet `p` itself, not on the scratch canvases a scene tests its
    stagings on."""
    return [c for c in spy.call_args_list if c.args and c.args[0] is p]


class Joust(unittest.TestCase):
    def test_the_lances_meet_at_the_tilt_in_a_burst_of_splinters(self):
        """The strike comes round frame by frame: the flash, then the slivers bursting out in an arc, flying and
        falling, the broken coronel spinning away; a still drawing keeps the flash with the slivers about it and the
        coronel in the air."""
        moving = SET.h1(HEADER, False, True)
        frames = sorted(n for n in moving.meta if n.startswith("bs") and moving.meta[n][2]
                        and moving.meta[n][2][0] == "seq")
        self.assertEqual(frames, ["bs0", "bs1", "bs2", "bs3"], "the flash, the burst, the slivers flying and falling")
        self.assertIn("lw", moving.meta, "the lance whole before it breaks")
        self.assertIn(RAMP["wood"][6], set(moving.layers["bs1"].values()), "the slivers of the shaft")
        for n in ("bs1", "bs2", "bs3"):
            self.assertIn(RAMP["steel"][5], set(moving.layers[n].values()), (n, "the coronel spinning away"))
        flown = [max(xs) - min(xs) for xs in ([x for (x, _), c in moving.layers[n].items() if c == RAMP["wood"][6]]
                                              for n in ("bs1", "bs2"))]
        self.assertLess(flown[0], flown[1], "the slivers fly outward")
        still = SET.h1(HEADER, False, False)
        self.assertFalse([n for n in still.meta if still.meta[n][2] and still.meta[n][2][0] == "seq"
                          and n.startswith("bs")], "a still drawing keeps the splinters in the air")
        burst = set(still.layers["bs1"].values())
        self.assertTrue({RAMP["wood"][6], RAMP["steel"][5], "#FFFFFF"} <= burst, "slivers, coronel and flash")

    def test_the_joust_fills_its_slot_under_the_standard_of_the_lists(self):
        """Where the words leave the lists a narrow slot, the near knight rides a third larger below and the far
        knight beyond the tilt higher and smaller, each under his crest; both lances are couched and painted in their
        knights' tinctures; and the standard of the lists flies over them from just under the valance down to the
        tilt. Where the slot is wide the joust spreads along the tilt with the knights' pavilions at its far end."""
        with mock.patch.object(A, "mounted", wraps=A.mounted) as mounted, \
                mock.patch.object(A, "lance", wraps=A.lance) as lance, \
                mock.patch.object(A, "lists_standard", wraps=A.lists_standard) as standard:
            p = SET.h1(HEADER, False, True)
        knights = drawn_on(p, mounted)
        near = [c for c in knights if c.kwargs.get("face") == 1]
        far = [c for c in knights if c.kwargs.get("face") == -1]
        self.assertEqual(len(near), 1)
        self.assertEqual(len(far), 1)
        self.assertEqual(near[0].kwargs["size"], "L", "the near knight a third larger")
        self.assertIn(far[0].kwargs["size"], ("M", "S"), "the far knight smaller")
        self.assertLess(far[0].args[2], near[0].args[2], "and higher, beyond the tilt")
        self.assertEqual({c.args[5] for c in drawn_on(p, lance)}, {"gules", "azure"}, "both lances couched")
        (flag,) = drawn_on(p, standard)
        self.assertLessEqual(flag.args[3], A.VALANCE_FOOT + 6, "the standard flies from just under the valance")
        bare = HEADER.with_(title="x", tagline="", description="", motto="", notes=())
        with mock.patch.object(A, "joust", wraps=A.joust) as joust, \
                mock.patch.object(A, "pavilion", wraps=A.pavilion) as pavilion:
            q = SET.h1(bare, False, True)
        (spread,) = drawn_on(q, joust)
        self.assertEqual(spread.kwargs["layout"], "spread")
        ends = [c.args[1] for c in drawn_on(q, pavilion)]
        self.assertTrue(ends and min(ends) > 4 + A.LAYOUTS["spread"][3] + 36, "the pavilions at the tilt's far end")

    def test_by_night_the_torch_glints_on_the_plate_and_the_burst_throws_sparks(self):
        night, day = SET.h1(HEADER, True, True), SET.h1(HEADER, False, True)
        plate = A.PLATE
        lit = [xy for L in night.layers if L.startswith("fl") for xy, c in night.layers[L].items()
               if c in (FLAME[4], FLAME[3]) and night.layers["base"].get(xy) in plate]
        self.assertGreaterEqual(len(lit), 6, "the torch's light along the plate's edges")
        sparks = set(night.layers["bs1"].values()) | set(night.layers["bs2"].values())
        self.assertTrue({FLAME[6], G[6]} <= sparks, "the sparks of the strike")
        self.assertNotIn(FLAME[6], set(day.layers["bs1"].values()) | set(day.layers["bs2"].values()))

    def test_the_crests_stand_bold_and_the_flash_breaks_round_the_far_knight(self):
        """The near knight rides under a gold lion's head with its mane and the far knight under a white swan, each a
        strong silhouette over his helm; and the still frame's flash leaves the far knight to himself beyond the
        heart of the strike, its rays breaking out round him."""
        with mock.patch.object(A, "stamp", wraps=A.stamp) as stamp, \
                mock.patch.object(A, "burst", wraps=A.burst) as burst:
            p = SET.h1(HEADER, False, False)
        arts = [c.args[3] for c in drawn_on(p, stamp)]
        lion = A.RIDER_CRESTS["L"]["lion"][0]
        self.assertTrue(lion in arts or A.flip(lion) in arts, "the near knight's lion")
        swans = [A.RIDER_CRESTS[size]["swan"][0] for size in ("M", "S")]
        self.assertTrue(any(a in arts or A.flip(a) in arts for a in swans), "the far knight's swan")
        (strike,) = drawn_on(p, burst)
        spare, (cx, cy) = strike.kwargs["spare"], strike.args[1:3]
        self.assertGreater(len(spare), 100, "the far knight and his horse")
        flash = {xy for xy, c in p.layers["bs1"].items() if c in ("#FFFFFF", G[6], FLAME[4], FLAME[3])}
        self.assertTrue(flash, "the flash")
        self.assertEqual([xy for xy in flash & spare if abs(xy[0] - cx) + abs(xy[1] - cy) > 2], [])

    def test_the_knights_ride_in_plate_with_crests_on_caparisoned_horses(self):
        p = SET.h1(HEADER, False, False)
        colours_ = set(p.layers["base"].values())
        for tinc in ("gules", "azure"):
            self.assertTrue(set(RAMP[tinc]) & colours_, (tinc, "a caparison"))
        self.assertIn(RAMP["steel"][4], colours_, "plate")
        self.assertIn(RAMP["argent"][6], colours_, "the swan of a crest")


class Scenes(unittest.TestCase):
    def drawn(self, draw, *names):
        """Which of the set's sprites (by the names of its art) `draw()` puts on its sheet."""
        called = set()

        def spy(name):
            real = getattr(A, name)

            def drawn(*args, **kw):
                called.add(name)
                return real(*args, **kw)
            return drawn
        with mock.patch.multiple(A, **{name: spy(name) for name in names}):
            draw()
        return called

    def test_an_h3_is_the_tiltyard_with_the_quintain_or_the_helm_on_its_post(self):
        """Beside a title with its crested helm an H3's tiltyard has the quintain, a knight running at it where the
        words leave room enough; when the title is too long for the helm beside it, the helm stands on its post in
        the quintain's place."""
        kinds = ("quintain_post", "tilting", "helm_stand", "lance_rack")
        kit = self.drawn(lambda: SET.h3(HEADER, False, True), *kinds)
        self.assertTrue({"quintain_post", "lance_rack"} <= kit and "helm_stand" not in kit, kit)
        bare = HEADER.with_(title="x", tagline="", description="", motto="", notes=())
        self.assertEqual(self.drawn(lambda: SET.h3(bare, False, True), *kinds),
                         {"tilting", "quintain_post", "lance_rack"})
        long = bare.with_(title="W" * 26)
        self.assertEqual(self.drawn(lambda: SET.h3(long, True, True), *kinds), {"helm_stand", "lance_rack"})

    def test_an_h2_is_the_camp_and_an_h1_the_lists_with_pavilions_beyond_where_there_is_room(self):
        """The camp's pavilions stand back beyond the knight at rest, and the knights' pavilions beyond the tilt,
        where the words leave the room; a drawing made lighter keeps every one of them where it stood."""
        bare = HEADER.with_(title="x", tagline="", description="", motto="", notes=())
        for draw, least in ((SET.h1, 2), (SET.h2, 3)):
            far = []
            for lite in (False, True):
                SET._lite = lite
                try:
                    with mock.patch.object(A, "pavilion", wraps=A.pavilion) as pavilion:
                        draw(bare, True, True)
                finally:
                    SET._lite = False
                far.append([(c.args[1:], c.kwargs) for c in pavilion.call_args_list if c.kwargs.get("far")])
            self.assertGreaterEqual(len(far[0]), least)
            self.assertEqual(far[1], far[0], "a drawing made lighter keeps them")

    def test_the_camp_beyond_differs_pavilion_by_pavilion_by_its_tree_of_shields(self):
        """Where the words leave an H2 the ground, the camp beyond the knight at rest has the tree of shields hung
        with the knights' shields, the one last struck askew, and pavilions differing in size and state: one with
        its door looped wide on a knight being armed within, one laced shut."""
        bare = HEADER.with_(title="x", tagline="", description="", motto="", notes=())
        for night in (False, True):
            with mock.patch.object(A, "pavilion", wraps=A.pavilion) as pavilion, \
                    mock.patch.object(A, "shield_tree", wraps=A.shield_tree) as tree:
                p = SET.h2(bare, night, True)
            self.assertEqual(len(drawn_on(p, tree)), 1, "the tree of shields")
            far = [c for c in drawn_on(p, pavilion) if c.kwargs.get("far")]
            self.assertEqual(len({(c.kwargs["w"], c.kwargs["h"]) for c in far}), len(far), "no two alike")
            self.assertTrue({"arming", "closed"} <= {c.kwargs.get("state") for c in far}, "their states")
            (arming,) = [c for c in far if c.kwargs.get("state") == "arming"]
            cx, foot = arming.args[1], arming.args[2]
            door = {p.layers["base"].get((x, y)) for x in range(cx - 9, cx + 10) for y in range(foot - 20, foot)}
            self.assertTrue({RAMP["steel"][6], RAMP["vert"][3 if night else 4]} <= door,
                            "the knight in his plate and his squire in the host's green")
            if night:
                self.assertIn(FLAME[6], door, "the door lit from within")
        struck = [n for n in p.meta if re.fullmatch(r"st\d+_\d", n) and p.meta[n][2] and p.meta[n][2][0] == "seq"]
        self.assertEqual(len(struck), 2, "the struck shield swings on its strap")

    def test_the_knight_being_armed_reads_at_1x(self):
        """The knight being armed in the camp's open pavilion stands as tall as the squire at a knight's horse's head,
        his face turned to his own squire, who reaches up with the great helm, its sight cut across it, and sets it
        on his head; the door is cut wide enough to show them both whole."""
        art = A.ARMING
        self.assertGreaterEqual((len(art[0]), len(art)), (19, 20), "a figure a reader can make out at 1x")
        self.assertTrue(all(len(row) == len(art[0]) for row in art))
        face = min(j for j, row in enumerate(art) if "f" in row[:9])
        rim, hair, crown = art[face - 2], art[face - 1], art[:face - 2]
        self.assertEqual(set(rim[2:9]), {"K"}, "the helm's rim")
        self.assertIn("h", hair[2:9], "the rim on his hair: the helm set on his head")
        steel = [j for j, row in enumerate(crown) if "S" in row[:10]]
        sight = [j for j, row in enumerate(crown) if row[1:9].count("K") >= 7 and 0 < j < len(crown) - 1]
        self.assertTrue(steel and sight and min(steel) < min(sight) < max(steel), "the helm, its sight across it")
        self.assertTrue(any("g" in row[9:12] for row in crown), "the squire's hand on the helm")
        bare = HEADER.with_(title="x", tagline="", description="", motto="", notes=())
        with mock.patch.object(A, "pavilion", wraps=A.pavilion) as pavilion:
            p = SET.h2(bare, False, True)
        (arming,) = [c for c in drawn_on(p, pavilion) if c.kwargs.get("state") == "arming"]
        cx, foot = arming.args[1], arming.args[2]
        x0 = cx - len(art[0]) // 2
        drawn = {(i, j) for j, row in enumerate(art) for i, ch in enumerate(row) if ch != "."}
        sunk = [(i, j) for i, j in drawn if p.layers["base"].get((x0 + i, foot - len(art) + j)) is None]
        self.assertEqual(sunk, [], "every pixel of them drawn")

    def test_the_camp_has_its_knight_his_squire_and_his_shields_at_the_lit_door(self):
        """Where its rows allow, an H2's camp has its knight at rest a third larger, his squire at his horse's head
        holding his lance with his pennon, a lance planted at each side of the pavilion's door with a pennon and his
        shield hung on it; by night the open door is lit from within and its light falls on the ground."""
        spies = {name: mock.patch.object(A, name, wraps=getattr(A, name))
                 for name in ("squire", "knight_at_rest", "door_lances", "pavilion")}
        for night in (False, True):
            calls = {}
            with spies["squire"] as squire, spies["knight_at_rest"] as knight, spies["door_lances"] as lances, \
                    spies["pavilion"] as pavilion:
                p = SET.h2(HEADER, night, True)
                calls = {"squire": drawn_on(p, squire), "knight": drawn_on(p, knight), "lances": drawn_on(p, lances),
                         "great": [c for c in drawn_on(p, pavilion) if c.kwargs.get("great")]}
            self.assertEqual(len(calls["squire"]), 1, night)
            self.assertEqual(calls["knight"][0].kwargs.get("size"), "L", "the knight at rest a third larger")
            self.assertEqual(len(calls["lances"]), 1)
            self.assertEqual(len(calls["great"]), 1)
            cx = calls["great"][0].args[1]
            door = {p.layers["base"].get((x, y)) for x in range(cx - 4, cx + 4) for y in range(p.h)}
            if night:
                self.assertIn(FLAME[6], door, "the door lit from within")
                spill = [xy for L in p.layers if L.startswith("fl") for xy in p.layers[L]
                         if abs(xy[0] - cx) < 10 and xy[1] >= calls["great"][0].args[2]]
                self.assertTrue(spill, "its light on the ground before it")
            else:
                self.assertNotIn(FLAME[6], door)

    def test_a_lantern_hangs_from_the_valance_by_night_only(self):
        """By night lanterns hang lit from the valance; over an H1's lists the standard's cresset and the lanterns
        along the stand's canopy burn in their places. By day none is lit."""
        for code, draw in (("H1", SET.h1), ("H2", SET.h2), ("H3", SET.h3)):
            with mock.patch.object(A, "hanging_lanterns", wraps=A.hanging_lanterns) as lanterns:
                day = draw(HEADER, False, True)
                self.assertFalse(lanterns.called)
                p = draw(HEADER, True, True)
                self.assertTrue(lanterns.called)
            self.assertFalse(getattr(day, "lit_stand", False))
            if code == "H1":
                self.assertTrue(getattr(p, "lit_stand", False), "the stand's lanterns lit along its canopy")
            else:
                self.assertIn(FLAME[4], set(p.layers["base"].values()), "the lantern's lit glass")

    def test_the_stand_is_the_h1s_second_showpiece(self):
        """At the right of an H1 the stand rises in two tiers of ladies in their hennins and lords in their bright
        dress under a striped canopy, a banner on each outer post and the knights' shields hung along its front, a
        lady waving her favour; the herald stands before it, his trumpet raised; and by night the lanterns along its
        canopy light the faces under them."""
        with mock.patch.object(A, "stand", wraps=A.stand) as stand, \
                mock.patch.object(A, "herald", wraps=A.herald) as herald, \
                mock.patch.object(A, "stamp", wraps=A.stamp) as stamp:
            p = SET.h1(HEADER, True, True)
        (s,) = drawn_on(p, stand)
        self.assertEqual((s.kwargs["tiers"], s.kwargs["banners"]), (2, True), "two tiers, a banner on each post")
        (h,) = drawn_on(p, herald)
        self.assertLess(h.args[1], s.args[1], "the herald before it, toward the lists")
        arts = [c.args[3] for c in drawn_on(p, stamp)]
        self.assertGreaterEqual(sum(1 for a in arts if a in A.SHIELDS.values()), 4, "the knights' shields")
        self.assertIn(A.FOLK["lady"], arts, "a lady in her hennin")
        self.assertTrue({"favour_0", "favour_1"} <= set(p.meta), "her favour waved")
        x0, foot, w = s.args[1], s.args[2], s.kwargs["w"]
        faces = {xy for xy, c in p.layers["base"].items() if c in SKIN and x0 <= xy[0] < x0 + w}
        lit = {xy for L in p.layers if L.startswith("fl") for xy in p.layers[L]}
        self.assertGreaterEqual(len(faces & lit), 12, "the lanterns' light on their faces")
        self.assertTrue(foot > max(y for _, y in faces), "under the canopy, over the stand's foot")


class Phones(unittest.TestCase):
    def test_every_sprite_keeps_two_units_clear_of_every_word_on_a_phone(self):
        """On a phone the lists, the pavilion, the helm, the camp and the tiltyard under the words, the valance, the
        section mark and the counter-lists on the rule are built to the rows the words leave free: no pixel of theirs
        lies within two units of a word's box, for any of the shared contents, by day or by night."""
        drawers = {"H1": SET.h1_narrow, "H2": SET.h2_narrow, "H3": SET.h3_narrow}
        for name, (h, _) in contents(KEY).items():
            for code, drawer in drawers.items():
                for night in (False, True):
                    p, pixels = sprites(lambda: drawer(h, night), "scene_narrow", "scene_under", "garland",
                                        "section_mark", "rule_decor")
                    hits = off_words(p, pixels)
                    self.assertEqual(hits[:6], [], (name, code, night, len(hits)))

    def test_every_sprite_keeps_two_units_clear_of_every_word_on_a_wide_header_too(self):
        """The scenes, the valance, the marks beside a title and the counter-lists on the rule keep the same two
        units from every word across a wide header."""
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
        of the set's on the drawing its file is made from: the lists on an H1, the knight at rest in his camp on an
        H2 and the knight running at the quintain on an H3."""
        pieces = {"H1": ("joust",), "H2": ("knight_at_rest",), "H3": ("tilting",)}
        names = sorted({n for ns in pieces.values() for n in ns})
        for name, (h, _) in contents(KEY).items():
            for code, wanted in pieces.items():
                for theme in (DAY, DARK):
                    _, p, spies = served(lambda: SET.header(code, h, theme, False, False), names)
                    self.assertTrue([n for n in wanted if drawn_on(p, spies[n])], (name, code, theme["name"]))

    def test_a_phones_h2_and_h3_stand_their_heroes_under_the_words_at_their_full_height(self):
        """Whatever its title, a phone's H2 stands the knights' camp and its H3 the tiltyard under its words, in rows
        of their own (`PHONE_ROWS`) across the phone on their own ground: the camp beside the lists, the tilt running
        back to the standard of the lists and a pavilion beyond it, the knight at rest on his great horse, his squire
        with his lance and his great pavilion with a lance at each side of its door; the tiltyard with a pavilion
        standing back, the knight on his great horse running at the quintain, the rack of lances, the helm on its
        post and a torch. Each rises 44 rows or more, all of it under the last of the words and two units clear of
        them, with nothing beside the title and no counter-lists on the rule under it, for every shared content, by
        day and by night; and by night the camp's great pavilion, the standard's cresset and the yard's torch burn."""
        whole = {"H2": ("tilt", "lists_standard", "pavilion", "squire", "knight_at_rest", "door_lances"),
                 "H3": ("pavilion", "tilting", "quintain_post", "lance_rack", "helm_stand", "torch")}
        large = {"H2": "knight_at_rest", "H3": "tilting"}
        for name, (h, _) in contents(KEY).items():
            for code, kinds in whole.items():
                draw, own = getattr(SET, f"{code.lower()}_narrow"), getattr(Holiday, f"{code.lower()}_narrow")
                for night in (False, True):
                    where = (name, code, night)
                    with contextlib.ExitStack() as stack:
                        spies = {k: stack.enter_context(mock.patch.object(A, k, wraps=getattr(A, k)))
                                 for k in kinds + ("counter_lists",)}
                        p, pixels = sprites(lambda: draw(h, night), "scene_under")
                    self.assertEqual([k for k in kinds if not drawn_on(p, spies[k])], [], where)
                    self.assertEqual(drawn_on(p, spies[large[code]])[0].kwargs.get("size"), "L", where)
                    self.assertEqual(drawn_on(p, spies["counter_lists"]), [], where)
                    self.assertEqual(off_words(p, pixels), [], where)
                    xs, ys = [x for x, _ in pixels], [y for _, y in pixels]
                    self.assertGreaterEqual(max(ys) - min(ys) + 1, 44, where)
                    self.assertGreaterEqual(min(ys), max(b[3] for b in p.words if b[1] < max(ys)), where)
                    self.assertLessEqual(min(xs), 6, where)
                    self.assertGreaterEqual(max(xs), 172, where)
                    self.assertEqual(p.h - own(SET, h, night).h, SET.PHONE_ROWS[code], where)
                    self.assertEqual(sprites(lambda: draw(h, night), "scene_narrow")[1], set(), where)
                    lit = {p.layers[L].get(xy) for L in p.layers for xy in pixels}
                    self.assertEqual(FLAME[6] in lit, night, where)

    def test_the_lists_stand_where_the_words_leave_them_room(self):
        """The kit's own lines leave a phone's H1 its lists, the joust among them; and the most a page can say is
        given the room its rows leave, never more."""
        for name in ("kit", "profile"):
            h, _ = contents(KEY)[name]
            p, pixels = sprites(lambda: SET.h1_narrow(h, False), "scene_narrow")
            shown = {p.get(*xy) for xy in pixels}
            self.assertTrue(set(RAMP["gules"]) & shown and set(RAMP["azure"]) & shown,
                            (name, "two knights at the tilt"))
            self.assertIn("#FFFFFF", shown, (name, "and the flash of the strike"))
        tall = HEADER.with_(tagline="A tagline that goes on for rather longer than most do, so that it has to wrap "
                            "onto a second line and perhaps even a third one on a phone.",
                            description="And a description under the tagline.", motto="A motto with a few words.",
                            notes=("A second note.", "A third, longer general note."))
        with mock.patch.object(A, "joust", wraps=A.joust) as joust:
            p = SET.h1_narrow(tall, False)
        self.assertEqual([c.kwargs["layout"] for c in drawn_on(p, joust)], ["compact"], "the joust in thirty rows")
        most, _ = contents(KEY)["most"]
        p, pixels = sprites(lambda: SET.h1_narrow(most, False), "scene_narrow")
        self.assertEqual(off_words(p, pixels), [])


class Longest(unittest.TestCase):
    PIECES = ("joust", "mounted", "lance", "tilt", "burst", "lists_standard", "flame", "torch", "stand", "herald",
              "pavilion", "shield_tree", "knight_at_rest", "squire", "door_lances", "valance", "frame", "silk_title",
              "gleam", "hanging_lanterns", "counter_lists", "ground")

    def test_the_longest_page_keeps_its_whole_scene_and_its_motion_within_the_budget(self):
        """Every field at its longest, the wide H1 and H2, by day and by night, drawn as the kit draws them, pinned
        or as the month's design with its mark, come within the budget and still move, and the drawing each is made
        from has every piece the drawing at full weight has, each where it stood: the joust under the standard of
        the lists, the stand with the herald before it, the camp with the knight at rest, his squire and his great
        pavilion with its lances, the valance, the poles, the title in silk and gold cord with its gleam, and by
        night the lanterns and the cresset. A drawing made lighter thins only the texture between them, and shows
        the strike in fewer frames."""
        most, _ = contents(KEY)["most"]

        def pieces(spies, p):
            return sorted(re.sub(r"'tt\d+'", "'tt'", repr((n, c.args[1:], sorted(c.kwargs.items()))))
                          for n, spy in spies.items() for c in drawn_on(p, spy))
        scenes = (("H1", {"joust", "lists_standard", "stand", "herald"}),
                  ("H2", {"pavilion", "knight_at_rest", "squire", "door_lances"}))
        for held in (SET, SET.on(MAY)):
            for code, named in scenes:
                for theme in (DAY, DARK):
                    svg, p, spies = served(lambda: held.header(code, most, theme, True, True), self.PIECES)
                    with mock.patch.dict(BUDGET, {"header": 10 ** 9}):
                        _, whole, full = served(lambda: held.header(code, most, theme, True, True), self.PIECES)
                    where = (code, theme["name"], "the month's" if held is not SET else "pinned")
                    self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"], where)
                    self.assertIn("<animate", svg, where)
                    self.assertEqual(pieces(spies, p), pieces(full, whole), where)
                    self.assertLessEqual(named, {n for n, spy in spies.items() if drawn_on(p, spy)}, where)


class Footers(unittest.TestCase):
    def test_every_footer_stands_on_the_tilts_barrier_with_the_heralds_mark_at_its_corner(self):
        """Every footer stands on the tilt's barrier, its planking painted green and white rising wherever the cells
        leave room; an F1's notes have the herald's mark at their corner, his trumpet hung on a pole with its banner
        and a lantern on the pole's head, lit by night and cold by day, on a phone as on a wide sheet."""
        f = contents(KEY)["kit"][1]
        for code in ("F1", "F2"):
            for wide in (True, False):
                svg = SET.footer(code, f, DAY, wide, False)
                self.assertIn('<pattern id="trf"', svg, (code, wide, "the barrier's green band and gold fringe"))
                self.assertIn('<pattern id="trk"', svg, (code, wide, "its planking"))
        h = int(re.search(r'height="(\d+)"', SET.footer("F2", f, DAY, True, False)).group(1)) // 2
        risen = [int(y) for y in re.findall(r'<rect x="\d+" y="(\d+)" width="\d+" height="\d+" fill="url\(#trk\)"',
                                            SET.footer("F2", f, DAY, True, False))]
        self.assertTrue(risen and min(risen) < h - 6, "the planking risen where the cells leave room")
        for wide in (True, False):
            with mock.patch.object(A, "herald_mark", wraps=A.herald_mark) as mark:
                day, night = (SET.footer("F1", f, theme, wide, False) for theme in (DAY, DARK))
            self.assertEqual(mark.call_count, 2, (wide, "the herald's mark by day and by night"))
            self.assertIn(RAMP["gules"][3], day, (wide, "the trumpet's banner"))
            self.assertIn(FLAME[6], night, (wide, "the lantern lit by night"))
            self.assertNotIn(FLAME[6], day, (wide, "and cold by day"))

    def test_the_mark_stands_on_what_lies_under_it_the_shorter_where_the_notes_are_short(self):
        """On a phone the mark's pole stands on the rule under the notes, and where one line of notes leaves it less
        room the trumpet hangs close under the lantern; on a wide sheet it stands on the barrier."""
        f = contents(KEY)["kit"][1]
        for closing, short in (("Thanks for reading.", True), ("Drawn at both ends. Fetched at neither.", False)):
            with mock.patch.object(A, "herald_mark", wraps=A.herald_mark) as mark:
                SET.footer("F1", f.with_(closing=closing), DAY, False, False)
            (call,) = mark.call_args_list
            self.assertEqual(call.kwargs["short"], short, closing)

    def test_the_barrier_runs_the_whole_width_with_a_post_at_every_bay(self):
        """Every footer of every shared content, by day and by night, stands on the tilt's barrier from edge to edge,
        its rail and its fringe along every column of its foot; and where a wide footer's barrier stands five rows
        tall or more, as it does along a block of cells without notes and along every scale bar, an oak post capped
        in gilt stands at every bay along it."""
        WD = RAMP["wood"]
        for name, (_, f) in contents(KEY).items():
            for draw in (SET.f1, SET.f2, SET.f1_narrow, SET.f2_narrow):
                for night in (False, True):
                    where, k = (name, draw.__name__, night), -1 if night else 0
                    p = draw(f, night)
                    self.assertEqual({x for x, y in p.filled if y == p.h - 1}, set(range(p.w)), where)
                    if p.w == 415 and (draw == SET.f2 or not f.get("closing")):
                        base = p.layers["base"]
                        posts = [x for x in range(p.w - 1) if base.get((x, p.h - 3)) == WD[4 + k]
                                 and base.get((x + 1, p.h - 3)) == WD[2 + k] and base.get((x, p.h - 6))]
                        self.assertGreaterEqual(len(posts), p.w // A.BAY - 2, where)

    def test_the_designs_mark_stands_at_the_right_end_and_beside_the_scale_bar(self):
        """The design's mark, the crested great helm of the lion with its mantling on its post, stands at the right end
        of a wide title block after the way back up wherever its cells leave the room, large; a block with notes,
        whose cells run to its right end, keeps the herald's mark at the corner of its notes instead. Every scale bar,
        wide and on a phone, has the helm in its cell beside the bar, standing on the barrier's ground or, on a
        phone, on the rule under the bar; and a phone's title block with no notes has the small helm set down on its
        barrier where its last row of cells leaves it room. Each is at least 15 units wide, to read at 1x, and keeps
        two units clear of every word, by day and by night."""
        for name, (_, f) in contents(KEY).items():
            notes = bool(f.get("closing"))
            for draw in (SET.f1, SET.f2, SET.f1_narrow, SET.f2_narrow):
                for night in (False, True):
                    where = (name, draw.__name__, night)
                    p = draw(f, night)
                    spot = getattr(p, "helm_at", None)
                    if draw == SET.f1 and notes:
                        self.assertIsNone(spot, where)
                        continue
                    if draw == SET.f1_narrow and (notes or name == "least"):
                        self.assertIsNone(spot, where)
                        continue
                    self.assertIsNotNone(spot, where)
                    x, size, foot = spot
                    w = A.HELMS[size][2]
                    cells = {(x + i, foot + j) for i, j in A._helm_cells(size)}
                    self.assertEqual(off_words(p, cells), [], where)
                    self.assertGreaterEqual(w, 15, where)
                    if draw == SET.f1:
                        self.assertIn(size, ("L", "Ls"), where)
                        self.assertGreater(x, max(b[2] for b in p.words), where)
                        self.assertGreaterEqual(x + w, p.w - 12, where)
                    elif draw == SET.f1_narrow:
                        self.assertEqual(size, "S", where)
                    else:
                        self.assertIn(size, ("L", "Ls", "M"), where)
                        bar = 18 if p.w == 415 else 12       # the scale bar's left end, its box 52 wide
                        self.assertGreaterEqual(x, bar + 51, (where, "beside the bar"))
                        self.assertLessEqual(x + w, 94 if p.w == 415 else 108, (where, "within its cell"))
                        if p.w < 415:
                            self.assertEqual(foot, 34, where)
                            self.assertEqual(p.get(x + 11, 34), SET.ink(night)["rule"], (where, "on the rule"))

    def test_the_barrier_and_the_mark_keep_clear_of_every_word(self):
        """The barrier rises only where the cells leave it room and the mark stands only where the notes leave it,
        a clear row kept from every word in every footer the shared contents ask for."""
        for name, (_, f) in contents(KEY).items():
            for draw in (SET.f1, SET.f2, SET.f1_narrow, SET.f2_narrow):
                for night in (False, True):
                    p, pixels = sprites(lambda: draw(f, night), "_footed")
                    self.assertEqual(off_words(p, pixels, margin=1)[:6], [], (name, draw.__name__, night))

    def test_a_link_is_a_banneret_and_a_small_file(self):
        for i, label in enumerate(("Issues", "Pull Requests", "Releases", "Actions")):
            for theme in (DAY, DARK):
                svg = SET.link(label, theme, i)
                self.assertLess(len(svg.encode("utf-8")), 2500, (label, theme["name"]))
                self.assertIn(RAMP["steel"][5 if theme is DAY else 4], svg, "the lance's coronel")


class Badges(unittest.TestCase):
    def test_a_gold_cord_lies_along_every_badges_top_with_the_letters_under_it(self):
        for style in BADGE_STYLES:
            drawn = [SET.classic_badge(style, "Build", "Passing", "pulse", SET.badge_label(),
                                       SET.badge_states()["green"])]
            drawn += [SET.plate_badge(style, "License", "MIT", "scale", mode) for mode in ("day", "night")]
            for p in drawn:
                top = [p.get(x, 0) for x in range(p.w) if inside(x, 0, p.w, p.h, BADGE_STYLES[style]["corner"])]
                self.assertTrue(top and set(top) <= {G[5], G[4], G[2]}, (style, "the cord"))
                self.assertTrue(all(y >= 2 for _, _, _, y, _ in p.uses["base"]), "the letters sit under the cord")

    def test_a_counters_numerals_hold_4_5_on_the_heralds_cheque(self):
        """Every numeral holds 4.5:1 on its cheque, a leading nought fainter; and the cheque lies on a layer under the
        drawing's own, so a numeral is painted over it whatever its colour (a colour the letters of the sheet's tag
        share is set before the cells on the drawing's own layer, and a cell there would cover it)."""
        for night in (False, True):
            q = Pix(20, 20)
            SET.counter_cell(q, 2, 2, night)
            self.assertFalse(q.layers["base"], night)
            face = q.layers["far"][(7, 8)]
            self.assertGreaterEqual(contrast(SET.counter_ink(night, False), face), 4.5, night)
            self.assertGreaterEqual(contrast(SET.counter_ink(night, True), face), 1.5, night)


class Hand(unittest.TestCase):
    """The design is drawn in the medieval collection's hand (`collections.hand`): its words in the hand's inks, its
    canvas within the hand's grounds, its fires on the hand's flame, its people's faces and hands on the hand's skins,
    its title's gleam and its figures on the hand's times, and the month's mark at its headers' top centre, clear of
    every scene."""

    def test_it_keeps_to_its_hand_as_its_months_design_and_kept_all_year(self):
        self.assertIsInstance(SET, CollectionSet)
        self.assertEqual((SET.collection, SET.month), ("medieval", 5))
        self.assertEqual(check(SET.on(MAY)), [])
        self.assertEqual(check(SET), [])

    def test_its_words_are_in_the_hands_inks(self):
        for night in (False, True):
            k = SET.ink(night)
            self.assertEqual((k["body"], k["muted"]), (MEDIEVAL.body[night], MEDIEVAL.muted[night]), night)

    def test_its_canvas_falls_within_the_hands_grounds(self):
        """By day both panels of the canvas and the key a label's backing is laid in, and by night every band of the
        canvas, fall within the hand's bands of lightness and colour."""
        for night, grounds in ((False, (X["panel_a"], X["panel_b"], X["key"])), (True, NIGHT_SKY)):
            lo, hi, most = MEDIEVAL.night_ground if night else MEDIEVAL.day_ground
            for c in grounds:
                light, chroma, hue = lab(c)
                self.assertTrue(lo <= light <= hi, (night, c, light))
                self.assertLessEqual(chroma, most, (night, c))
                self.assertTrue(night or chroma >= 6 or 40 <= hue <= 110, (c, "a nearly colourless day leans warm"))

    def test_every_flame_burns_on_the_hands_flame(self):
        """The torches, the cresset, the lanterns, the pavilions lit from within and the herald's lantern on a footer
        burn on the hand's flame: the set's flame is the hand's, and every colour that flickers, the flames, their
        glows and the light they lay, is a tone of it."""
        self.assertEqual(RAMP["flame"], MEDIEVAL.ramp("flame"))
        tones = set(MEDIEVAL.ramp("flame"))
        for name in ("kit", "least"):
            h, f = contents(KEY)[name]
            drawn = [("H1", SET.h1(h, True, True)), ("H2", SET.h2(h, True, True)), ("H3", SET.h3(h, True, True))]
            for what, p in drawn + ([("F1", SET.f1(f, True))] if f.get("closing") else []):
                flickers = [L for L in p.layers if p.meta[L][2] and p.meta[L][2][0] == "flicker"]
                lit = {c.split(":")[0] for L in flickers for c in p.layers[L].values()}
                lit |= {c for L in flickers for c in re.findall(r'fill="(#[0-9A-F]{6})"', "".join(p.shapes[L]))}
                self.assertTrue(lit, (name, what))
                self.assertLessEqual(lit, tones, (name, what))

    def test_every_face_and_hand_is_on_the_hands_skins(self):
        """The spectators in the stand, the herald, the squire at the knight's horse's head, the knight being armed
        and his squire have their faces and hands on the hand's three skins, by figure, all three among them."""
        for i in range(3):
            self.assertEqual(RAMP[f"skin{i}"], MEDIEVAL.ramp(f"skin{i}"))
            for night in (False, True):
                self.assertLessEqual(set(A.skin(i, night).values()), set(SKINS[i]), (i, night))
        bare = HEADER.with_(title="x", tagline="", description="", motto="", notes=())
        for night in (False, True):
            drawn = set(SET.h1(HEADER, night, True).layers["base"].values())
            drawn |= set(SET.h2(bare, night, True).layers["base"].values())
            self.assertEqual({i for i, skin in enumerate(SKINS) if set(skin) & drawn}, {0, 1, 2}, night)
        self.assertEqual({row[10:].count("f") for row in A.ARMING}, {0}, "the squire's hands are his own")

    def test_its_title_gleams_and_its_figures_move_on_the_hands_times(self):
        """The gleam crosses the title every `glint` seconds of the hand; the strike of the joust, the run at the
        quintain and the lady's favour waved come round in a figure's loop of four to eight seconds."""
        svg = SET.header("H1", HEADER, DAY, True, True)
        gleam = re.search(r'<clipPath id="gl\d+"><polygon[^>]*><animateTransform[^>]*dur="([\d.]+)s"', svg)
        self.assertEqual(float(gleam.group(1)), MEDIEVAL.glint)
        for loop in (A.STRIKE, A.TILT, A.WAVE):
            self.assertTrue(4 <= loop <= 8, loop)
        p = SET.h1(HEADER, False, True)
        for name, loop in (("lw", A.STRIKE), ("bs1", A.STRIKE), ("favour_0", A.WAVE)):
            self.assertEqual(p.meta[name][2][3], loop, name)
        bare = HEADER.with_(title="x", tagline="", description="", motto="", notes=())
        q = SET.h3(bare, False, True)
        self.assertEqual({q.meta[n][2][3] for n in q.meta if n.startswith(("qs", "qf"))}, {A.TILT})

    def test_the_months_mark_hangs_at_the_top_centre_only_as_its_months_design(self):
        held = SET.on(MAY)
        for name in ("kit", "least"):
            h, _ = contents(KEY)[name]
            for night in (False, True):
                for draw in ("h1", "h2", "h3"):
                    wide = getattr(held, draw)(h, night, True), getattr(SET, draw)(h, night, True)
                    phone = getattr(held, draw + "_narrow")(h, night), getattr(SET, draw + "_narrow")(h, night)
                    for month, kept in (wide, phone):
                        self.assertTrue(any(L.startswith("mark") for L in month.layers), (name, draw, night))
                        self.assertFalse(any(L.startswith("mark") for L in kept.layers), (name, draw, night))

    def test_the_months_marks_box_is_kept_clear_of_every_scene(self):
        """The box the month's mark takes, and two units round it, holds nothing of a header's scene, wide or on a
        phone, by day or by night, for every shared content, whether or not the mark is drawn: the valance's band
        runs on behind it, but its dags pause there, and the spangles, the quintain and the rest keep out."""
        drawers = {"H1": (SET.h1, SET.h1_narrow), "H2": (SET.h2, SET.h2_narrow), "H3": (SET.h3, SET.h3_narrow)}
        hooks = ("scene", "scene_narrow", "scene_under", "garland", "strip_mark", "section_mark", "rule_decor",
                 "stars", "finish")
        for name, (h, _) in contents(KEY).items():
            for code, (wide, phone) in drawers.items():
                for night in (False, True):
                    for draw in (lambda: wide(h, night, True), lambda: phone(h, night)):
                        p, pixels = sprites(draw, *hooks)
                        x0, y0, x1, y1 = A.mark_box(p)
                        hits = sorted((x, y) for x, y in pixels if x0 <= x < x1 and y0 <= y < y1 and y >= 6)
                        self.assertEqual(hits[:6], [], (name, code, p.w, night))
                        runs = A.dag_runs(p, 5, p.w - 5)
                        self.assertLessEqual(runs[0][0] + runs[0][1] * A.DAG, x0, (name, code, p.w))
                        self.assertGreaterEqual(runs[1][0], x1, (name, code, p.w))

    def test_as_its_months_design_its_files_keep_their_room_and_their_motion(self):
        """Drawn as its month's design, with the mark, every header of the kit's own lines, the samples and the least
        a page can say is drawn at full weight with its motion at least 1,500 bytes under the budget, and the most a
        page can say, drawn lighter where it must be, still comes within the budget and still moves."""
        held, cap = SET.on(MAY), BUDGET["header"]
        for name in ("kit", "repository", "profile", "least"):
            h, _ = contents(KEY)[name]
            for code in ("H1", "H2", "H3"):
                for theme in (DAY, DARK):
                    for wide, motion in ((True, True), (False, False)):
                        with mock.patch.dict(BUDGET, {"header": 10**9}):
                            svg = held.header(code, h, theme, wide, motion)
                        what = (name, code, theme["name"], wide)
                        self.assertLessEqual(len(svg.encode("utf-8")), cap - 1500, what)
                        self.assertEqual("<animate" in svg, motion, what)
        most, _ = contents(KEY)["most"]
        for code in ("H1", "H2", "H3"):
            for theme in (DAY, DARK):
                svg = held.header(code, most, theme, True, True)
                self.assertLessEqual(len(svg.encode("utf-8")), cap, (code, theme["name"]))
                self.assertIn("<animate", svg, (code, theme["name"]))

    def test_its_phones_lists_stand_the_full_width_under_the_words(self):
        """A phone's H1 stands its lists across the width under the words, at least 48 rows tall wherever the page
        says no more than the samples do."""
        for name in ("kit", "repository", "profile", "least"):
            h, _ = contents(KEY)[name]
            p, pixels = sprites(lambda: SET.h1_narrow(h, False), "scene_narrow")
            xs, ys = [x for x, _ in pixels], [y for _, y in pixels]
            self.assertLessEqual(min(xs), 6, name)
            self.assertGreaterEqual(max(xs), 173, name)
            self.assertGreaterEqual(max(ys) - min(ys) + 1, 48, name)


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

    def test_ordinary_content_is_drawn_at_full_weight(self):
        """The kit's own lines, the samples and the least a page can say fit their budgets as drawn, with their
        motion; only the stress contents are served lighter."""
        for name in ("kit", "repository", "profile", "least"):
            h, f = contents(KEY)[name]
            for night in (False, True):
                for code, draw in (("H1", SET.h1), ("H2", SET.h2), ("H3", SET.h3)):
                    svg = draw(h, night, True).svg("t", "d", still=False)
                    self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"], (name, code, night))
                    self.assertIn("<animate", svg)
                for code, draw in (("H1", SET.h1_narrow), ("H2", SET.h2_narrow), ("H3", SET.h3_narrow)):
                    svg = draw(h, night).svg("t", "d", still=True)
                    self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["header"], (name, code, night, "phone"))
                for code, draw in (("F1", SET.f1), ("F2", SET.f2)):
                    svg = draw(f, night).svg("t", "d", still=True)
                    self.assertLessEqual(len(svg.encode("utf-8")), BUDGET["footer"], (name, code, night))

    def test_text_colours_hold_4_5_on_the_paper_and_every_row_of_the_night(self):
        for night in (False, True):
            k = SET.ink(night)
            p = Pix(415, 200)
            grounds = {SET.bg_at(p, night, y) for y in range(p.h)}
            grounds |= {X["panel_a"], X["panel_b"]} if not night else set(NIGHT_SKY)
            for role in ("title", "body", "muted", "accent"):
                for ground in grounds:
                    self.assertGreaterEqual(contrast(k[role], ground), 4.5, (night, role, ground))
            self.assertGreaterEqual(contrast(k["tag_ink"], k["tag"]), 4.5, (night, "tag"))
            self.assertGreaterEqual(contrast(k["tag_ink"], RAMP["azure"][1]), 4.5, (night, "the favour"))
            fill, _, ink, _ = SET.link_colours(night)
            for tinc in A.LINK_TINCTURES:
                self.assertGreaterEqual(contrast(ink, RAMP[tinc][2 - (1 if night else 0)]), 4.5,
                                        (night, tinc, "a banneret's letters"))

    def test_the_lanterns_light_leaves_every_word_its_contrast(self):
        """The night's brightest band under the lanterns' wash and a hanging lantern's pool together, each at its
        heart, still holds every text colour at 4.5:1; and a hanging lantern with its glow hangs clear of words."""
        from domain.holidays.pixel.shade import luminance
        top = NIGHT_SKY[0]
        glow = RAMP["flame"][2]
        a = 1 - (1 - max(A.WASH)) * (1 - max(A.POOL))
        mix = "#" + "".join(f"{round(int(top[i:i + 2], 16) * (1 - a) + int(glow[i:i + 2], 16) * a):02X}"
                            for i in (1, 3, 5))
        self.assertLess(luminance(mix), 0.05)
        for role in ("title", "body", "muted", "accent"):
            self.assertGreaterEqual(contrast(SET.ink(True)[role], mix), 4.5, role)
        for name, (h, _) in contents(KEY).items():
            for code, drawer in (("H1", SET.h1), ("H2", SET.h2), ("H3", SET.h3)):
                p, pixels = sprites(lambda: drawer(h, True, True), "finish")
                self.assertEqual(off_words(p, pixels)[:6], [], (name, code))

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

    def test_the_rosters_avatars_are_crested_helms_never_initials(self):
        spec = E.describe("roster", next(d for d in ELEMENTS.values() if d["kind"] == "roster"))
        for night in (False, True):
            p = Pix(40, 40)
            before = len(p.words)
            SET.avatar(p, 20, 20, 0, {"initials": "IV", "name": "Imogen Vale"}, night)
            self.assertEqual(len(p.words), before, "no letters")
            self.assertIn(RAMP["steel"][4 - (1 if night else 0)], set(p.layers["base"].values()), "a helm")
        svg = SET.element("roster", spec, DAY, "wide")
        self.assertIn(RAMP["wood"][3], svg, "the bot's quintain")

    def test_the_histogram_stands_lances_with_vamplates(self):
        spec = E.describe("instruments", next(d for d in ELEMENTS.values() if d["kind"] == "instruments"))
        for theme in (DAY, DARK):
            svg = SET.element("instruments", spec, theme, "wide")
            k = -1 if theme is DARK else 0
            self.assertIn(RAMP["steel"][6 + k], svg, (theme["name"], "a vamplate's lit rim"))
            for tinc in ("gules", "azure", "vert", "purpure"):
                self.assertIn(RAMP[tinc][4 + k], svg, (theme["name"], tinc))

    def test_a_card_is_painted_silk_with_its_icon_on_a_shield(self):
        """A schematic's card is a banner of painted silk: a gold cord all round its edge, laid over the layout's
        outline, a band of a tincture at its head cut in dags, and its icon worked in gold on a heater shield of the
        tincture, never a coloured tab down its edge."""
        for night in (False, True):
            k = -1 if night else 0
            p = Pix(120, 40)
            x, y, w, h = 4, 4, 104, 27
            SET.node(p, night, x, y, w, h, {"title": "Probes", "path": "crates/probe", "icon": "grid"}, seed=1)
            cord = "cordn" if night else "cordd"
            rims = [s for s in p.shapes.get("trim", []) if f"url(#{cord})" in s]
            self.assertEqual(len(rims), 4, (night, "the cord all round"))
            self.assertGreater(p.meta["trim"][0], p.meta["base"][0], "laid over the outline")
            T = RAMP[A.LINK_TINCTURES[1]]
            self.assertEqual({p.get(xx, y + 1) for xx in range(x + 1, x + w - 1)}, {T[3 + k]}, "the band at its head")
            self.assertIn(SET.ink(night)["fill"], {p.get(xx, y + 2) for xx in range(x + 1, x + w - 1)}, "cut in dags")
            sy = y + (h - len(A.CARD_SHIELD)) // 2
            self.assertEqual(p.get(x + 7, sy + len(A.CARD_SHIELD) - 1), A.K, "the shield's point")
            shield = {p.get(xx, yy) for xx in range(x + 3, x + 12) for yy in range(sy + 1, sy + 9)}
            self.assertTrue({T[3 + k], G[5 + k]} <= shield, "the icon in gold on the tincture")
            edge = {p.get(x + 1, yy) for yy in range(y + 4, y + h - 2)}
            self.assertFalse(set(T) & edge, "no tab down the card's edge")

    def test_the_dial_is_the_quintain_its_hand_a_lance(self):
        """The dial's face is the quintain's round target painted in quarters of gules and argent, every figure on
        it at 4.5:1; its rim is iron with gold rivets; its hand is a lance, striped, with a vamplate and the coronel
        at its head, and none of the layout's plain hand is left; its hub is the pivot on the head of its post."""
        for night in (False, True):
            k = -1 if night else 0
            face = A.quintain_face(night)
            colours_ = {face(x, y, 50, 40, 30) for x in range(20, 81) for y in range(10, 41)} - {None}
            self.assertEqual(len(colours_), 2, "two tinctures by turns")
            for c in colours_:
                for role in ("body", "muted"):
                    self.assertGreaterEqual(contrast(SET.ink(night)[role], c), 4.5, (night, role, c))
            p = Pix(120, 60)
            SET.dial(p, {"value": 7, "span": 30, "sub": "v1"}, 60, 44, 30, night)
            SET.finish(p, night)
            drawn = set(p.layers["base"].values())
            if not night:
                self.assertNotIn(SET.ink(night)["accent"], drawn, "the plain hand redrawn as a lance")
            self.assertTrue({RAMP["gules"][4 + k], G[5 + k]} <= drawn, "the lance's spiral")
            self.assertIn(RAMP["steel"][5 + k], drawn, "its vamplate and coronel")
            self.assertTrue(colours_ <= drawn and RAMP["steel"][4 + k] in drawn, "the target in its iron rim")
            self.assertIn(RAMP["wood"][4 + k], drawn, "the post's head under the pivot")

    def test_the_seal_is_the_prize_on_its_cushion(self):
        """The seal is the tourney's prize: a gold circlet set with a ruby, a sapphire and an emerald and crowned
        with fleurons, sitting on a cushion of crimson velvet with a gold tassel at each corner; its ribbon is the
        lady's favour."""
        for night in (False, True):
            k = -1 if night else 0
            p = Pix(100, 100)
            A.cushion(p, 50, 45, 23, 31, night)
            drawn = set(p.layers["base"].values())
            self.assertTrue({RAMP["gules"][2 + k], RAMP["gules"][3 + k]} <= drawn, "the crimson velvet")
            for gem in (RAMP["gules"][4 + k], RAMP["azure"][4 + k], RAMP["vert"][4 + k]):
                self.assertIn(gem, drawn, "the circlet's stones")
            crown = [y for (x, y), c in p.layers["base"].items() if c in set(G) and y < 45 - 25]
            self.assertTrue(crown, "fleurons standing over the circlet's rim")
            tassels = [y for (x, y), c in p.layers["base"].items() if c in set(G) and y > 45 + 25]
            self.assertTrue(tassels, "tassels hanging from the cushion's corners")
        svg = SET.element("certificate", E.describe("certificate", ELEMENTS["conformance"]), DAY, "wide")
        self.assertIn(RAMP["azure"][1], svg, "the lady's favour")

    def test_a_placard_is_a_heralds_proclamation_board(self):
        for theme in (DAY, DARK):
            svg = SET.element("placard", E.describe("placard", ELEMENTS["action"]), theme, "wide")
            k = -1 if theme is DARK else 0
            self.assertIn(RAMP["wood"][5 + k], svg, "the board's oak frame")
            self.assertIn('<pattern id="plfp"', svg, "its poles")


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
