# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The games on @tannergolden's profile and their Hall of Fame in every pixel set: while a holiday's set or a
collection's design is up, it draws all four boards and the Hall in its own pixels, every file of one or none.

Every file is the kit's, by name and width, well formed, within its lint and its budget, in the set's palette with the
two sides' ivory and ebony and the trophies' metals, and the same every time. A moving file plays as it opens and its
still twin never moves. Every word is lettered in the set's own inks, a collection's in its hand's two, and keeps to
the room the set's frame leaves, meeting no other word and no piece, at the limits the data may reach. A game the set
cannot letter, or draw within its budget, is drawn whole in the page's own look, and chess's own Hall keeps it
always. Every board is built, and every podium cut, of stuffs the set names in its own palette, no two sets of a year
stand their winners on the same podium, and every tag on a game's sheet is the set's own, never a certificate's
ribbon. Nothing on a set's board helps a player choose, Tic-Tac counts the boards each side has won and Pentago each
side's marbles left, a move's words run to a second line after their comma, and a Pentago move's, with its turn, to a
third, every word whole."""
from __future__ import annotations

import re
import unittest
import xml.dom.minidom as minidom
from unittest import mock

from tests import support

from domain import KIT, KIT_VERSION, collections, holidays, pixelsets
from domain.canvas import BUDGET, lint
from domain.elements import data as ED
from domain.elements import draw as E
from domain.holidays.designs import boards as B
from domain.holidays.designs import games as G
from domain.holidays.designs import hall as HL
from domain.holidays.designs import materials as MT
from domain.holidays.designs import pieces as PC
from domain.holidays.designs.trophies import METALS
from domain.holidays.pixel import MISSING, Pix
from infra.yaml_reader import loads
from tests.unit import test_elements_games as SAMPLES

support.install()
SETS = [k for k in holidays.KEYS if k in holidays.SETS] + list(collections.COLLECTIONS["medieval"].keys)
DASHES = ("–", "—", "―")
# Two sets every file of which is drawn twice and pushed to the data's limits: a holiday's and a collection's month.
TWO = ("halloween", "medieval-chessmen:2026-02-01")


def fixtures() -> dict:
    """The elements of the profile's fixtures, each game's and both Halls, by id, as a run merges them."""
    out = {}
    for kind in ("chess", "checkers", "pentago", "tictac", "hall-of-fame"):
        spec = loads((support.ROOT / "tests" / "fixtures" / f"{kind}.yaml").read_text(encoding="utf-8"))
        out.update(ED.merged(ED.check(spec["elements"]), {}, subject="tannergolden", today="2026-09-25"))
    return out


ELEMENTS = fixtures()
GAMES = {d["kind"]: E.describe(d["kind"], d) for d in ELEMENTS.values() if d["kind"] in ED.GAMES}
DRAWN: dict = {}


def draw(key: str) -> dict:
    """Every file the set draws for every game, {(kind, variant, theme): (svg, inks)}: with each the inks its words are
    set in, aside from what the set letters as its own art, its titles and the initials on its people."""
    held = pixelsets.drawn_by(key)
    inks: list = []
    art = [0]
    text, title, avatar = Pix.text, type(held).game_title, type(held).avatar

    def recorded(self, x, y, s, c, *a, **k):
        if not art[0]:
            inks.append(c)
        return text(self, x, y, s, c, *a, **k)

    def own(hook):
        def drawn(self, *a, **k):
            art[0] += 1
            try:
                return hook(self, *a, **k)
            finally:
                art[0] -= 1
        return drawn
    files = {}
    with mock.patch.object(Pix, "text", recorded), mock.patch.object(type(held), "game_title", own(title)), \
            mock.patch.object(type(held), "avatar", own(avatar)):
        for kind, d in GAMES.items():
            for variant in E.variants(kind, d):
                for theme in ("day", "dark"):
                    inks.clear()
                    files[(kind, variant, theme)] = (held.game(kind, d, E.THEMES[theme], variant), frozenset(inks))
    return files


def drawn(key: str) -> dict:
    """`draw`, once per set for every test that only reads the files."""
    if key not in DRAWN:
        DRAWN[key] = draw(key)
    return DRAWN[key]


class EverySet(unittest.TestCase):
    def test_every_set_draws_every_file_of_every_game_and_signs_it(self):
        for key in SETS:
            for (kind, variant, theme), (svg, _) in drawn(key).items():
                where = (key, kind, variant, theme)
                self.assertIsNotNone(svg, where)
                minidom.parseString(svg)
                self.assertIn(f"<!--{KIT} v{KIT_VERSION} {key} elements {kind} {variant} {theme}-->", svg, where)
                self.assertNotIn("<text", svg, where)
                for ch in DASHES:
                    self.assertNotIn(ch, svg, where)

    def test_every_file_lints_within_its_budget_and_the_sets_palette(self):
        for key in SETS:
            held = pixelsets.drawn_by(key)
            self.assertLessEqual(held.tokens, held.game_tokens)
            for (kind, variant, theme), (svg, _) in drawn(key).items():
                self.assertEqual(lint(svg, budget=BUDGET["board"], tokens=held.game_tokens), [],
                                 (key, kind, variant, theme))

    def test_every_file_is_the_kits_width_and_a_still_one_its_moving_twins_size(self):
        for key in SETS:
            files = drawn(key)
            for (kind, variant, theme), (svg, _) in files.items():
                w, h = map(int, re.search(r'<svg[^>]* width="(\d+)" height="(\d+)"', svg).groups())
                if variant.startswith("badge-"):
                    self.assertEqual(h, 28, (key, variant))
                else:
                    self.assertEqual(w, 360 if variant.startswith("narrow") else 830, (key, kind, variant))
                if variant.endswith("still"):
                    twin = files[(kind, variant[:-len("-still")] if variant != "still" else "wide", theme)][0]
                    self.assertEqual(re.search(r'width="\d+" height="\d+"', svg)[0],
                                     re.search(r'width="\d+" height="\d+"', twin)[0], (key, kind, variant))

    def test_a_moving_file_plays_as_it_opens_and_its_still_twin_never_moves(self):
        for key in SETS:
            for (kind, variant, theme), (svg, _) in drawn(key).items():
                where = (key, kind, variant, theme)
                if variant.endswith("still") or variant in ("badge-2", "badge-3", "badge-4", "badge-5"):
                    self.assertNotIn("<animate", svg, where)
                elif variant.startswith("badge-"):
                    self.assertIn("<animate", svg, where)
                else:
                    self.assertIn('fill="freeze"', svg, where)

    def test_every_word_is_lettered_in_the_sets_own_inks(self):
        # Words in the set's inks; labels on what they are set on: a tag's in its ink, a finished game's message on
        # the set's red, a square's number on the board and a place's on its block, in its metal.
        for key in SETS:
            held = pixelsets.drawn_by(key)
            for night, theme in ((False, "day"), (True, "dark")):
                k = held.ink(night)
                own = {k[role] for role in ("title", "body", "muted", "accent", "tag_ink")}
                labels = {held.badge_states()["red"][1], held.game_board(night)["shade"]} | {m[0] for m in METALS.values()}
                for (kind, variant, t), (_, inks) in drawn(key).items():
                    if t == theme and not variant.startswith("badge-"):
                        self.assertLessEqual(inks, own | labels, (key, kind, variant, theme))

    def test_a_set_draws_nothing_that_helps_a_choice_and_counts_the_boards_won_and_the_marbles_left(self):
        # As in every look: no square or hole to block and no word of perfect play, and where chess counts what each
        # side took, Tic-Tac counts the boards each side has won and Pentago each side's marbles left.
        said: list = []
        text = Pix.text

        def recorded(self, x, y, s, c, *a, **k):
            said.append(str(s))
            return text(self, x, y, s, c, *a, **k)
        for key in TWO:
            held = pixelsets.drawn_by(key)
            for kind in ("tictac", "pentago"):
                for variant in ("wide", "narrow"):
                    said.clear()
                    with mock.patch.object(Pix, "text", recorded):
                        held.game(kind, GAMES[kind], E.THEMES["day"], variant)
                    words = " ".join(said).upper()
                    for hint in ("BLOCK", "PERFECT PLAY", "WINS NEXT", "FROM HERE", "BEST PLAY"):
                        self.assertNotIn(hint, words, (key, kind, variant))
                    self.assertIn("BOARDS WON" if kind == "tictac" else "MARBLES LEFT", words, (key, kind, variant))

    def test_a_moves_words_run_to_a_second_line_after_their_comma_leaving_no_number_alone(self):
        # Checkers' words take two lines on a phone: "landing on 11" stays whole on the second where `wrap` would
        # leave the 11 alone, and where no comma lets both lines fit they come out even.
        said: list = []
        text = Pix.text

        def recorded(self, x, y, s, c, *a, **k):
            said.append(str(s))
            return text(self, x, y, s, c, *a, **k)
        for key in TWO:
            held = pixelsets.drawn_by(key)
            for kind, variant in (("checkers", "narrow"),):
                said.clear()
                with mock.patch.object(Pix, "text", recorded):
                    held.game(kind, GAMES[kind], E.THEMES["day"], variant)
                head, tail = GAMES[kind]["last"]["words"].split(", ")
                self.assertIn(head + ",", said, (key, kind, variant))
                self.assertIn(tail, said, (key, kind, variant))
        self.assertEqual(G.wrap("Man from 20 jumps 16, landing on 11", 172, "57")[1], "11")
        self.assertEqual(G.phrased("Man from 20 jumps 16, landing on 11", 172),
                         ["Man from 20 jumps 16,", "landing on 11"])

    def test_a_pentago_moves_words_run_to_a_third_line_with_its_turn_every_word_whole(self):
        # A marble and its quarter's turn take three lines on every sheet, the longest the engine writes too, and
        # none is cut short: a move's words reach a third line before they are clipped.
        said: list = []
        text = Pix.text

        def recorded(self, x, y, s, c, *a, **k):
            said.append(str(s))
            return text(self, x, y, s, c, *a, **k)
        for key in TWO:
            held = pixelsets.drawn_by(key)
            for words in (GAMES["pentago"]["last"]["words"],
                          "A white marble on e4, then the upper right quarter turns anticlockwise"):
                d = dict(GAMES["pentago"], last=dict(GAMES["pentago"]["last"], words=words))
                for variant in ("wide", "narrow"):
                    said.clear()
                    with mock.patch.object(Pix, "text", recorded):
                        held.game("pentago", d, E.THEMES["day"], variant)
                    # the words as the sheet letters them, one line after another under the move
                    at = said.index(next(s for s in said if len(s) > 2 and words.startswith(s)))
                    self.assertEqual(" ".join(said[at:at + 3]), words, (key, words[:24], variant))

    def test_a_collections_design_letters_its_games_in_its_hands_two_inks(self):
        for key in collections.COLLECTIONS["medieval"].keys:
            held = pixelsets.drawn_by(key)
            for night in (False, True):
                k = held.ink(night)
                self.assertEqual((k["body"], k["muted"]), (held.hand.body[night], held.hand.muted[night]), key)

    def test_the_leaders_badge_glints_on_the_sets_period_a_collections_on_its_hands(self):
        for key in ("halloween", "medieval-forge"):
            held = pixelsets.drawn_by(key)
            svg = drawn(key)[("hall-of-fame", "badge-1", "day")][0]
            self.assertIn(f'dur="{held._glint_period():g}s"', svg, key)
        self.assertEqual(pixelsets.drawn_by("medieval-forge")._glint_period(),
                         pixelsets.drawn_by("medieval-forge").hand.glint)


class TheirStuff(unittest.TestCase):
    def test_every_set_builds_its_boards_and_its_podium_of_its_own_stuffs(self):
        # What a board's squares are made of, how it is framed, and what the Hall's podium is cut from and trimmed in:
        # named in the set's own palette, of grains, frames and podiums the kit knows; a collection's design never of
        # the colours its hand lends every design alike.
        for key in SETS:
            held = pixelsets.drawn_by(key)
            hand = {t.upper() for t in held.hand.tokens} if getattr(held, "hand", None) else set()
            for night in (False, True):
                where = (key, night)
                b, pod = held.game_board(night), held.game_podium(night)
                self.assertIsInstance(pod, MT.Podium, where)
                self.assertIn(b["style"], MT.FRAMES, where)
                self.assertIn(pod.style, MT.PODIUMS, where)
                for s in (b["light_stuff"], b["dark_stuff"], b["frame"], pod.stuff, *([pod.trim] if pod.trim else [])):
                    self.assertIn(s.grain, MT.GRAINS, where)
                    self.assertLessEqual(s.tokens, held.game_tokens, (where, s.base))
                for s in (b["light_stuff"], b["dark_stuff"], pod.stuff):
                    self.assertNotIn(s.base.upper(), hand, where)

    def test_a_tag_low_on_a_games_sheet_is_the_sets_own_tag_never_a_certificates_ribbon(self):
        # A set dresses the one tag set low on its sheet as the ribbon under a certificate's seal; a game's panel sets
        # its tags low all down its sheet, and every one is the tag the set heads its sheets with.
        for key in SETS:
            held = pixelsets.drawn_by(key)
            for night in (False, True):
                for wide in (415, 180):
                    head, low = held.game_canvas(wide, 300), held.game_canvas(wide, 300)
                    held.tag(head, 20, 8, 30, 9, night)
                    held.tag(low, 20, 108, 30, 9, night)
                    for name in set(head.layers) | set(low.layers):
                        shifted = {(x, y + 100): c for (x, y), c in head.layers.get(name, {}).items()}
                        self.assertEqual(low.layers.get(name, {}), shifted, (key, night, wide, name))

    def test_the_square_a_move_landed_on_is_lit_in_the_trophies_gold_in_every_set(self):
        # Washed in the set's accent, an ink for words, a square was shaded rather than lit; the trophies' light gold
        # lights it on any square of any set, by day and by night, framed in the set's own accent.
        for key in SETS:
            held = pixelsets.drawn_by(key)
            for theme, night in (("day", False), ("dark", True)):
                marks = held.game_marks(night)
                self.assertEqual(marks["glow"], METALS[3][4], (key, theme))
                self.assertIn(f'"{marks["glow"].upper()}"', drawn(key)[("chess", "still", theme)][0].upper(), (key, theme))

    def test_no_two_sets_of_a_year_stand_their_winners_on_the_same_podium(self):
        for year in ([k for k in SETS if not k.startswith("medieval-")], [k for k in SETS if k.startswith("medieval-")]):
            seen: dict = {}
            for key in year:
                pod = pixelsets.drawn_by(key).game_podium(False)
                look = (pod.stuff.base, pod.stuff.grain, pod.style)
                self.assertNotIn(look, seen, (key, seen.get(look)))
                seen[look] = key

    def test_every_podium_is_cut_from_its_stuff_with_a_plaque_of_every_places_metal(self):
        for key in SETS:
            held = pixelsets.drawn_by(key)
            for theme, night in (("day", False), ("dark", True)):
                svg = drawn(key)[("hall-of-fame", "still", theme)][0].upper()
                self.assertIn(held.game_podium(night).stuff.base.upper(), svg, (key, theme))
                for metal in (3, 2, 1):
                    self.assertIn(METALS[metal][3].upper(), svg, (key, theme, metal))


class TheirMarks(unittest.TestCase):
    """What a pixel set's Tic-Tac and Pentago boards mark, and how, in every set alike."""

    def test_what_the_rules_point_to_and_what_wins_is_in_the_trophies_gold(self):
        # The board a Tic-Tac mark is sent to, a line of three boards and a Pentago five, in gilt, outlined in the
        # gold's darkest, the same in every set, where a set's own accent could be its board's own colour; and only
        # there: a board with no board to send a mark to and nothing won carries none.
        darkest = METALS[3][0].upper()
        sent = GAMES["tictac"]
        won = {"tictac": E.describe("tictac", dict(SAMPLES.TT_WON)),
               "pentago": E.describe("pentago", dict(SAMPLES.PG_WON))}
        plain = {"tictac": E.describe("tictac", dict(SAMPLES.TT_DRAWN)), "pentago": GAMES["pentago"]}
        for key in TWO:
            held = pixelsets.drawn_by(key)
            for theme in ("day", "dark"):
                for kind, d, gold in (("tictac", sent, True), ("tictac", won["tictac"], True),
                                      ("pentago", won["pentago"], True), ("tictac", plain["tictac"], False),
                                      ("pentago", plain["pentago"], False)):
                    svg = held.game(kind, d, E.THEMES[theme], "wide").upper()
                    self.assertEqual(darkest in svg, gold, (key, theme, kind, d["game"]))

    def test_tic_tacs_nine_boards_are_a_chequer_of_the_sets_two_stuffs(self):
        # As chess's squares are: the four edge boards in the dark stuff a tone up, the corners and the centre in the
        # light, so the board of boards reads at a glance and every set's world is seen at board size.
        laid: list = []
        lay = MT.lay

        def recorded(p, s, *a, **k):
            if k.get("L") == "cells":
                laid.append(s.key)
            return lay(p, s, *a, **k)
        for key in TWO:
            held = pixelsets.drawn_by(key)
            for theme, night in (("day", False), ("dark", True)):
                b = held.game_board(night)
                dark = b["dark_stuff"]
                deep = MT.Stuff(dark.ramp, min(len(dark.ramp) - 1, dark.at + 1), dark.grain, dark.fleck)
                laid.clear()
                with mock.patch.object(MT, "lay", recorded):
                    held.game("tictac", GAMES["tictac"], E.THEMES[theme], "wide")
                self.assertEqual((laid.count(b["light_stuff"].key), laid.count(deep.key)), (45, 36), (key, theme))

    def test_an_empty_pentago_hole_never_reads_as_a_white_marble(self):
        # A hole's floor is the light stuff in the hole's shadow, far from a White marble's ivory and a Black one's
        # ebony, in every set by day and by night: the light stuff itself is as light as ivory in most sets.
        for key in SETS:
            held = pixelsets.drawn_by(key)
            for night in (False, True):
                floor = B.Pentago.floor(held.game_board(night), night)
                self.assertGreaterEqual(G._delta(floor.base, PC.IVORY[4]), 20, (key, night, floor.base))
                self.assertGreaterEqual(G._delta(floor.base, PC.EBONY[2]), 20, (key, night, floor.base))
                self.assertIn(floor.base.upper(), held.game_tokens, (key, night))

    def test_pentagos_plates_lie_in_a_bed_inside_the_frame_and_turn_clear_of_it(self):
        # The plates stop short of the board's box, so the bed shows all round them and between them, as a real
        # board's, and a quarter turning its quarter turn sweeps over the bed, never the frame.
        seen: list = []
        geometry = B.Pentago.geometry

        def measured(box, small):
            g = geometry(box, small)
            seen.append((box, g))
            return g
        held = pixelsets.drawn_by(TWO[0])
        for variant in ("wide", "narrow"):
            seen.clear()
            with mock.patch.object(B.Pentago, "geometry", staticmethod(measured)):
                held.game("pentago", GAMES["pentago"], E.THEMES["day"], variant)
            self.assertTrue(seen, variant)
            for (x0, y0, n), g in seen:
                reach = 2 * g["q"] + g["gap"]
                self.assertGreaterEqual(min(g["x"] - x0, g["y"] - y0), 2, variant)
                self.assertLessEqual(g["x"] + reach, x0 + n - 2, variant)
                self.assertLessEqual(g["y"] + reach, y0 + n - 2, variant)

    def test_every_board_is_framed_pentagos_as_chesss_is(self):
        framed: list = []
        frame = B.framed

        def recorded(h, p, *a, **k):
            framed.append(a)
            return frame(h, p, *a, **k)
        for key in TWO:
            held = pixelsets.drawn_by(key)
            for kind in ("chess", "tictac", "pentago"):
                framed.clear()
                with mock.patch.object(B, "framed", recorded):
                    held.game(kind, GAMES[kind], E.THEMES["day"], "wide")
                self.assertEqual(len(framed), 1, (key, kind))

    def test_the_houses_x_is_as_heavy_as_githubs_o_and_its_ivory_bevelled(self):
        # Ivory's light tones alone lost the X on a set's light squares: it reaches as far as the O and is as heavy,
        # and its bars are lit along one flank and shaded along the other, at every size a sheet sets it.
        def span(cells):
            return max(x for x, _ in cells) - min(x for x, _ in cells)
        for size in (7, 9, 12, 13, 15, 16, 40, 46, 48):
            x, o = PC.pen("X", "light", size), PC.pen("O", "dark", size)
            xs, os_ = [xy for xy, _ in x[0]], [xy for xy, _ in o[0]]
            tones = {colour for _, colour in x[0]}
            self.assertGreaterEqual(span(xs), span(os_), size)
            self.assertGreaterEqual(len(xs), len(os_), size)
            self.assertTrue(tones & {PC.IVORY[2], PC.IVORY[3]}, size)
            self.assertTrue(tones & {PC.IVORY[5], PC.IVORY[6]}, size)


class TheSame(unittest.TestCase):
    def test_every_file_is_the_same_every_time(self):
        for key in TWO:
            self.assertEqual(draw(key), drawn(key), key)


class AtTheLimits(unittest.TestCase):
    """Every word keeps to the room the set's frame leaves and meets no other word and no piece, wide and on a phone,
    by day and by night, for boards and Halls at the limits the data may reach."""

    def samples(self) -> list:
        from tests.unit import test_elements_chess_fit as CF
        from tests.unit import test_elements_games_fit as GF
        from tests.unit import test_elements_hall_fit as HF
        out = [(kind, ds[0]) for kind, ds in GF.BOARDS.items()] + [(kind, ds[0]) for kind, ds in GF.ENDED.items()]
        out += [("chess", CF.LIMITS), ("chess", CF.GAME)]
        out += [("hall-of-fame", HF.HALLS[name]) for name in ("W names", "M logins", "long names")]
        return out + [("hall-of-fame", HF.EMPTY)]

    def test_every_word_keeps_its_room_and_meets_no_other_word_nor_piece(self):
        put = B.put

        def placed(p, drawing, key, x, y, L="base"):
            p.__dict__.setdefault("pieces", []).append((x, y, x + drawing[1], y + drawing[2]))
            return put(p, drawing, key, x, y, L)
        with mock.patch.object(B, "put", placed), mock.patch.object(HL, "put", placed):
            for key in TWO:
                held = pixelsets.drawn_by(key)
                for kind, d in self.samples():
                    d = E.describe(kind, d)
                    for wide in (True, False):
                        for night in (False, True):
                            where = (key, kind, wide, night)
                            if kind == "hall-of-fame":
                                p = HL.sheet(held, HL.state(d), night, wide, True)
                            else:
                                g = B.GAMES[kind]
                                p = held.board_sheet(g, g.state(d), night, wide, True)
                            self.assertLessEqual(len(p.svg("t", "d", still=False).encode("utf-8")), BUDGET["board"],
                                                 where)
                            self.assertClear(held, p, where)

    def assertClear(self, held, p, where):
        room = held._trophy_room(p)

        def inside(x, y):
            corner = (x < room.corner or x >= p.w - room.corner) and (y < room.corner or y >= p.h - room.corner)
            return room.x0 <= x < room.x1 and room.y0 <= y < room.y1 and not corner
        words = p.words
        for x0, y0, x1, y1 in words:
            self.assertTrue(all(inside(x, y) for x in (x0, x1 - 1) for y in (y0, y1 - 1)), (where, (x0, y0, x1, y1)))
        # A word's box keeps a unit all round it, so two words a unit apart touch: they meet only past it.
        inner = [(x0 + 1, y0 + 1, x1 - 1, y1 - 1) for x0, y0, x1, y1 in words]
        for i, a in enumerate(inner):
            for b in inner[i + 1:]:
                self.assertFalse(a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3], (where, a, b))
            for b in p.__dict__.get("pieces", []):
                self.assertFalse(a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3], (where, a, b))


class TheKit(unittest.TestCase):
    def test_a_page_hands_every_game_to_the_set_whole_and_keeps_chesss_own_hall(self):
        self.assertIn("chess-hall", {d["kind"] for d in ELEMENTS.values()})
        own = ED.render(ELEMENTS, "standard")
        for key in TWO:
            files = ED.render(ELEMENTS, "standard", key)
            self.assertEqual(set(files), set(own), key)
            for name, svg in files.items():
                if name.startswith("chess-hall"):
                    self.assertEqual(svg, own[name], name)
                else:
                    self.assertIn(f" {key.split(':')[0]} elements ", svg.split("-->")[0], name)

    def test_a_game_the_set_cannot_letter_is_drawn_whole_in_the_pages_own_look(self):
        d = dict(next(d for d in ELEMENTS.values() if d["kind"] == "hall-of-fame"))
        d["names"] = {**(d.get("names") or {}), d["people"][1][0]: "日本"}
        elements = {"hall-of-fame": d}
        self.assertEqual(ED.render(elements, "blackprint", "halloween"), ED.render(elements, "blackprint"))
        self.assertFalse(MISSING)

    def test_a_file_too_heavy_is_drawn_lighter_and_one_that_cannot_be_is_the_pages(self):
        held = pixelsets.drawn_by("christmas")
        d = GAMES["pentago"]
        full = held.game("pentago", d, E.THEMES["dark"], "wide")
        with mock.patch.dict(BUDGET, {"board": len(full.encode("utf-8")) - 1}):
            lighter = held.game("pentago", d, E.THEMES["dark"], "wide")
            self.assertLess(len(lighter), len(full))
            self.assertIn("christmas elements pentago wide dark-->", lighter)
        self.assertFalse(held._lite, "the set is left drawing lighter")
        with mock.patch.dict(BUDGET, {"board": 1000}):
            self.assertIsNone(ED.held_game(held, "pentago", "pentago", ELEMENTS["pentago"]))


if __name__ == "__main__":
    unittest.main()
