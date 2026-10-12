# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The games on @tannergolden's profile and their Hall of Fame in every pixel set: while a holiday's set or a
collection's design is up, it draws all four boards and the Hall in its own pixels, every file of one or none.

Every file is the kit's, by name and width, well formed, within its lint and its budget, in the set's palette with the
two sides' ivory and ebony and the trophies' metals, and the same every time. A moving file plays as it opens and its
still twin never moves. Every word is lettered in the set's own inks, a collection's in its hand's two, and keeps to
the room the set's frame leaves, meeting no other word and no piece, at the limits the data may reach. A game the set
cannot letter, or draw within its budget, is drawn whole in the page's own look, and chess's own Hall keeps it
always. Every board is built, and every podium cut, of stuffs the set names in its own palette, and no two sets of a
year stand their winners on the same podium."""
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
from domain.holidays.designs import hall as HL
from domain.holidays.designs import materials as MT
from domain.holidays.designs.trophies import METALS
from domain.holidays.pixel import MISSING, Pix
from infra.yaml_reader import loads

support.install()
SETS = [k for k in holidays.KEYS if k in holidays.SETS] + list(collections.COLLECTIONS["medieval"].keys)
DASHES = ("–", "—", "―")
# Two sets every file of which is drawn twice and pushed to the data's limits: a holiday's and a collection's month.
TWO = ("halloween", "medieval-chessmen:2026-02-01")


def fixtures() -> dict:
    """The elements of the profile's fixtures, each game's and both Halls, by id, as a run merges them."""
    out = {}
    for kind in ("chess", "checkers", "connectfour", "tictactoe", "hall-of-fame"):
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
        d = GAMES["connectfour"]
        full = held.game("connectfour", d, E.THEMES["dark"], "wide")
        with mock.patch.dict(BUDGET, {"board": len(full.encode("utf-8")) - 1}):
            lighter = held.game("connectfour", d, E.THEMES["dark"], "wide")
            self.assertLess(len(lighter), len(full))
            self.assertIn("christmas elements connectfour wide dark-->", lighter)
        self.assertFalse(held._lite, "the set is left drawing lighter")
        with mock.patch.dict(BUDGET, {"board": 1000}):
            self.assertIsNone(ED.held_game(held, "connectfour", "connectfour", ELEMENTS["connectfour"]))


if __name__ == "__main__":
    unittest.main()
