# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: LicenseRef-Proprietary
"""The Hall of Fame fits whatever its data says into the room the layout gives it, at the limits the data may reach.

Every run of lettering the sheet sets is recorded with its box on the sheet, and so is every piece, every bar of the
series, every medal and every block of the podium. Each run is held to its room: it meets no other run, no piece and
no bar; it meets a medal or a block only as what is lettered on it, the initials inside a medal and the place on its
block; and nothing leaves the card or the border. Each winner on the podium stands inside their block's width, every
line of a place after it ends short of its wins in each game and of its badge, and a name that fitted is drawn as it
was. The still files are the moving ones at rest: every run stands where the motion leaves it.

The games stand Chess first, then Checkers, Pentago and Tic-Tac, in the series and beside every winner's wins,
each count its own game's though the data lists them in tier order. Every game is named by its own mark, its two
pieces, the house's first: the white king, the white man and the white marble before the black, X before O. Where
the room is short, a mark gives way before its count does.

The data reaches the contract's limits: logins of 39 letters and names of 40, every count at 999,999, so each total
at seven figures, and ten winners and twenty leaders sent for five places and ten. Every limit is set in W or M, the
widest capitals there are."""
from __future__ import annotations

import re
import unittest
from typing import NamedTuple
from unittest import mock

from tests import support

from domain.elements import draw as E
from domain.elements import hall as H
from domain.elements.hall import layout as L
from domain.elements.hall import skins as S
from domain.elements.hall import marks as K
from domain.lettering import Lettering, cap_height, width
from domain.prints import PRINTS, STANDARD

support.install()
TONES = (STANDARD, *sorted(PRINTS))
SHEETS = ("wide", "narrow")
TOL = .05
CEILING = {g: [999_999, 333_333, 333_333, 333_333] for g in H.GAMES}


def logins(letter: str, n: int = 10) -> list[str]:
    """Logins of 39 letters, each its own."""
    return [letter * 39] + [letter * (39 - len(str(i))) + str(i) for i in range(1, n)]


def hall(people, names=None, series=None, leaders=None) -> dict:
    return {"kind": "hall-of-fame", "series": series or CEILING, "people": people, "names": names or {},
            "leaders": leaders or [["tannergolden", 999_999_999, 999_999, [249_999] * 4]]}


def at_limits(letter: str, named: bool) -> dict:
    """Ten winners at every limit, for five places: wins of 999,999 in each game, so 3,999,996 in all, names of 40
    letters or none, so each is named by a login of 39."""
    ws = logins(letter)
    return hall([[w, [999_999 - i] * 4, "28 May", 999_999, 10_000 + i] for i, w in enumerate(ws)],
                {w: letter * 40 for w in ws} if named else None)


HALLS = {
    "W names": at_limits("W", True),
    "M names": at_limits("M", True),
    "W logins": at_limits("W", False),
    "M logins": at_limits("M", False),
    "long names": hall([["christopher-alexander-montgomer", [3, 1, 0, 1], "2 Oct", 12],
                        ["tannergolden", [1, 1, 1, 1], "19 Sep", 7], ["imvale", [0, 2, 0, 1], "27 Sep", 5],
                        ["tokafor", [0, 0, 0, 2], "4 Sep", 6], ["jhalloran", [1, 0, 0, 0], "8 Oct", 3]],
                       {"christopher-alexander-montgomer": "Christopher Alexander Montgomery",
                        "imvale": "Maximilian Wolfgang Wellington-Smythe"},
                       {"tictac": [9, 4, 2, 3], "pentago": [3, 1, 2, 0], "checkers": [5, 2, 2, 1],
                        "chess": [12, 5, 6, 1]}),
}
PEOPLE = hall([["tannergolden", [4, 1, 2, 5], "2 Oct", 29], ["imvale", [1, 1, 0, 2], "19 Sep", 7],
               ["tokafor", [0, 1, 1, 1], "27 Sep", 9], ["wrencastellan", [1, 0, 1, 0], "4 Sep", 6],
               ["jhalloran", [0, 0, 0, 1], "8 Oct", 3]], {"imvale": "Imogen Vale", "tokafor": "Tomas Okafor"},
              {"tictac": [9, 4, 2, 3], "pentago": [3, 1, 2, 0], "checkers": [5, 2, 2, 1],
               "chess": [12, 5, 6, 1]})
EMPTY = hall([], series={g: [0, 0, 0, 0] for g in H.GAMES})


class Run(NamedTuple):
    """A run of lettering and its box on the sheet: from x0 to x1, from its capitals' top to its baseline."""
    s: str
    x0: float
    x1: float
    top: float
    base: float
    size: float

    @property
    def bottom(self) -> float:
        """How far below the baseline its letters reach: a descender, a comma, an @."""
        return self.base + (self.size * .22 if any(ch.islower() or ch in ",;()@" for ch in self.s) else 0)


class Box(NamedTuple):
    what: str
    x0: float
    y0: float
    x1: float
    y1: float


def meets(r: Run, b: Box) -> bool:
    return min(r.x1, b.x1) - max(r.x0, b.x0) > TOL and min(r.bottom, b.y1) - max(r.top, b.y0) > TOL


def inside(r: Run, b: Box) -> bool:
    return b.x0 - TOL <= r.x0 and r.x1 <= b.x1 + TOL and b.y0 - TOL <= r.top and r.base <= b.y1 + TOL


class Drawn(NamedTuple):
    svg: str
    runs: list
    pieces: list
    bars: list
    blocks: list
    medals: list


def drawn(d: dict, tone: str, variant: str = "wide", theme: str = "day") -> Drawn:
    """A file, drawn as a run draws it (the kit's lint and budget, or it raises), and every run of lettering, piece,
    bar, medal and block in it."""
    runs, pieces, bars, blocks, medals = [], [], [], [], []
    text, piece = Lettering.text, S.Pieces.piece
    faces = {cls: (cls.face, cls.medallion, cls.vacant, cls.podium, cls.track) for cls in (S.Standard, S.Print)}

    def record(self, s, *, face="meta", size=12, x=0, y=0, anchor="start", ls=0, **k):
        if s:
            w = width(s, face, size, ls)
            x0 = x - w / 2 if anchor == "middle" else x - w if anchor == "end" else x
            runs.append(Run(s, x0, x0 + w, y - cap_height(face, size), y, size))
        return text(self, s, face=face, size=size, x=x, y=y, anchor=anchor, ls=ls, **k)

    def placed(self, cv, game, material, x, y, size, **k):
        # the union of every piece's outline in its 45-unit box: a man is the widest, a king the tallest
        pieces.append(Box(f"{game} {material}", x + size * 5.5 / 45, y + size * 3 / 45, x + size * 39.6 / 45,
                          y + size * 39.4 / 45))
        return piece(self, cv, game, material, x, y, size, **k)

    def patched(cls):
        face, medallion, vacant, podium, track = faces[cls]

        def tracked(self, cv, x, y, w, h):
            bars.append(Box("bar", x, y - 3, x + w, y + h + 3))   # the bar, with the tick across its middle
            return track(self, cv, x, y, w, h)

        def on_face(self, cv, cx, cy, r, p, i, medal=None, glint=False):
            rr = r + 4.5 + 1.8 if medal is not None else r
            medals.append(Box("medal", cx - rr, cy - rr, cx + rr, cy + rr))
            return face(self, cv, cx, cy, r, p, i, medal, glint)

        def on_medallion(self, cv, cx, cy, r, side):
            medals.append(Box("medallion", cx - r, cy - r, cx + r, cy + r))
            return medallion(self, cv, cx, cy, r, side)

        def on_vacant(self, cv, cx, cy, r, i):
            rr = r + 4.5 + 1
            medals.append(Box("vacant", cx - rr, cy - rr, cx + rr, cy + rr))
            return vacant(self, cv, cx, cy, r, i)

        def on_podium(self, cv, steps, ground, size):
            blocks.extend(Box(f"block {place + 1}", x, ground - h, x + w, ground) for x, w, h, place in steps)
            return podium(self, cv, steps, ground, size)
        return [mock.patch.object(cls, "face", on_face), mock.patch.object(cls, "medallion", on_medallion),
                mock.patch.object(cls, "vacant", on_vacant), mock.patch.object(cls, "podium", on_podium),
                mock.patch.object(cls, "track", tracked)]

    patches = [mock.patch.object(Lettering, "text", record), mock.patch.object(S.Pieces, "piece", placed),
               *patched(S.Standard), *patched(S.Print)]
    for p in patches:
        p.start()
    try:
        svg = E.draw("hall-of-fame", d, tone, theme, variant)
    finally:
        for p in reversed(patches):
            p.stop()
    return Drawn(svg, runs, pieces, bars, blocks, medals)


def size_of(svg: str) -> tuple[int, int]:
    w, h = re.match(r'<svg[^>]* width="(\d+)" height="(\d+)"', svg).groups()
    return int(w), int(h)


def one(runs: list[Run], s: str) -> Run:
    """The one run that says `s`, in any case."""
    found = [r for r in runs if r.s.upper() == s.upper()]
    assert len(found) == 1, (s, [r.s for r in runs])
    return found[0]


class Clear(unittest.TestCase):
    """Nothing the sheet letters at the limits meets anything else it draws, nor leaves the card or the border."""

    def assertClear(self, f: Drawn, tone: str, what):
        W, H_ = size_of(f.svg)
        edge = 1 if tone == STANDARD else (10 if W < 400 else 12) + 1.6   # the card's edge, or the border's inside
        for r in f.runs:
            self.assertTrue(edge - TOL <= r.x0 and r.x1 <= W - edge + TOL and edge <= r.top and r.bottom <= H_ - edge,
                            (what, r))
        for i, a in enumerate(f.runs):
            for b in f.runs[i + 1:]:
                across = min(a.x1, b.x1) - max(a.x0, b.x0)
                down = min(a.bottom, b.bottom) - max(a.top, b.top)
                self.assertFalse(across > TOL and down > TOL, (what, a, b))
        for r in f.runs:
            for b in f.pieces + f.bars:
                self.assertFalse(meets(r, b), (what, r, b))
            for b in f.blocks + f.medals:
                self.assertTrue(not meets(r, b) or inside(r, b), (what, r, b))

    def test_a_hall_at_every_limit_is_lettered_clear_of_everything_it_draws_in_every_theme(self):
        for name, d in (*HALLS.items(), ("people", PEOPLE), ("empty", EMPTY)):
            self.assertEqual(H.check(d), [], name)
            for tone in TONES:
                for variant in SHEETS:
                    f = drawn(d, tone, variant)
                    with self.subTest(hall=name, tone=tone, variant=variant):
                        self.assertClear(f, tone, (name, tone, variant))
                        self.assertNotIn("<text", f.svg)

    def test_the_files_at_the_limits_are_well_formed_within_budget_and_deterministic_by_day_and_night(self):
        for name in ("W names", "M logins"):
            d = HALLS[name]
            for tone in TONES:
                for variant in E.variants("hall-of-fame", d):
                    for theme in ("day", "dark"):
                        svg = E.draw("hall-of-fame", d, tone, theme, variant)  # the kit's lint and budget, or it raises
                        with self.subTest(hall=name, tone=tone, variant=variant, theme=theme):
                            self.assertNotIn("<text", svg)
                            self.assertEqual(svg, E.draw("hall-of-fame", d, tone, theme, variant))


class Series(unittest.TestCase):
    """Each count of the series stands at its end of its bar, the house's ending short of it and GitHub's after it
    inside the margin, and a row's name keeps its whole word: the counts give way first."""

    def test_every_count_stands_at_its_end_of_its_bar_inside_the_margin(self):
        for name, d in (("W logins", HALLS["W logins"]), ("people", PEOPLE)):
            for tone in TONES:
                for variant in SHEETS:
                    f = drawn(d, tone, variant)
                    W, _ = size_of(f.svg)
                    with self.subTest(hall=name, tone=tone, variant=variant):
                        self.assertEqual(len(f.bars), 5, "all four games together, then each")
                        if variant == "narrow":   # a phone sets the totals over their bar, either side of VS
                            vs = one(f.runs, "vs")
                            totals = [r for r in f.runs if r.s.isdigit() and abs(r.base - vs.base) < 9]
                            self.assertEqual(len(totals), 2)
                            self.assertLessEqual(totals[0].x1, vs.x0 - 8)
                            self.assertGreaterEqual(totals[1].x0, vs.x1 + 8)
                        for bar in f.bars[variant == "narrow":]:
                            beside = [r for r in f.runs if r.s.isdigit() and r.top < bar.y1 and r.bottom > bar.y0
                                      and (r.x1 <= bar.x0 + TOL or r.x0 >= bar.x1 - TOL)]
                            left = [r for r in beside if r.x1 <= bar.x0 + TOL]
                            right = [r for r in beside if r.x0 >= bar.x1 - TOL]
                            self.assertEqual((len(left), len(right)), (1, 1), (bar, beside))
                            self.assertLessEqual(left[0].x1, bar.x0 - 8 + TOL)
                            self.assertGreaterEqual(right[0].x0, bar.x1 + 8 - TOL)
                            self.assertLessEqual(right[0].x1, W - L.PAD + TOL)

    def test_a_game_is_named_whole_whatever_its_counts_chess_first(self):
        for tone in TONES:
            for variant in SHEETS:
                runs = drawn(HALLS["M logins"], tone, variant).runs
                with self.subTest(tone=tone, variant=variant):
                    for title in [H.TITLES[g] for g in H.ORDER] + (["all four games"] if variant == "wide" else []):
                        self.assertEqual(len([r for r in runs if r.s.upper() == title.upper()]), 1, title)
                    tops = [one(runs, H.TITLES[g]).top for g in H.ORDER]
                    self.assertEqual(tops, sorted(tops), "Chess, Checkers, Pentago, Tic-Tac, top to bottom")

    def test_a_series_that_fits_is_set_as_it_was(self):
        runs = drawn(PEOPLE, STANDARD).runs
        self.assertEqual([r.size for r in runs if r.s == "12"], [26, 26, 20], "the totals, big, and the house's wins")
        self.assertEqual(one(runs, "tic-tac").size, 10)
        self.assertEqual(one(runs, "9 games  ·  3 drawn").size, 6.5)
        phone = drawn(PEOPLE, STANDARD, "narrow").runs
        self.assertEqual([r.size for r in phone if r.s == "12"][:2], [24, 24])


class Podium(unittest.TestCase):
    """Each of the three leading winners stands inside the width of their own block, over it; the first's block is
    the tallest and stands in the middle; the place is lettered on each block; and a name that fitted is drawn as it
    was."""

    def test_each_winner_stands_over_their_own_block_and_inside_its_width(self):
        for name, d in (*HALLS.items(), ("people", PEOPLE), ("empty", EMPTY)):
            for tone in TONES:
                for variant in SHEETS:
                    f = drawn(d, tone, variant)
                    with self.subTest(hall=name, tone=tone, variant=variant):
                        self.assertEqual([b.what for b in f.blocks], ["block 2", "block 1", "block 3"])
                        second, first, third = f.blocks
                        self.assertLess(first.y0, second.y0)
                        self.assertLess(second.y0, third.y0)
                        for b in f.blocks:
                            place = b.what.split()[1]
                            on = [r for r in f.runs if meets(r, b)]
                            self.assertEqual([r.s for r in on], [place], "the place, lettered on its block")
                            over = [r for r in f.runs if b.x0 - TOL <= (r.x0 + r.x1) / 2 <= b.x1 + TOL
                                    and r.base <= b.y0 and r.base > b.y0 - 140]
                            self.assertTrue(over, b)
                            for r in over:
                                self.assertTrue(b.x0 + 2 - TOL <= r.x0 and r.x1 <= b.x1 - 2 + TOL, (b, r))

    def test_the_house_reads_as_the_house_wherever_it_stands(self):
        for name in ("long names", "people"):
            d = HALLS.get(name, PEOPLE)
            for tone in (STANDARD, "blackprint"):
                runs = drawn(d, tone).runs
                with self.subTest(hall=name, tone=tone):
                    self.assertEqual(len([r for r in runs if r.s.upper() == "@TANNERGOLDEN"]), 2,
                                     "on its side of the match and on the podium")
                    self.assertEqual(len([r for r in runs if r.s.upper() == "THE HOUSE"]), 2)
                    self.assertFalse([r for r in runs if r.s == "TA"], "the house wears its king, never initials")

    def test_a_place_nobody_has_taken_yet_says_so_whole(self):
        # An empty Hall is the first one the profile shows, so every word on it is whole, a phone's narrow places
        # setting a line on two rather than cutting it short.
        first = hall([["tannergolden", [1, 0, 0, 0], "12 Oct", 1]],
                     series={**EMPTY["series"], "tictac": [1, 1, 0, 0]})
        for d in (EMPTY, first):
            for tone in TONES:
                for variant in SHEETS:
                    runs = drawn(d, tone, variant).runs
                    with self.subTest(winners=len(d["people"]), tone=tone, variant=variant):
                        self.assertFalse([r.s for r in runs if r.s.endswith("…")])
                        said = " ".join(r.s.upper() for r in sorted(runs, key=lambda r: (r.base, r.x0))
                                        if r.s.upper() in ("THE NEXT TO WIN STANDS HERE", "THE NEXT TO WIN",
                                                           "STANDS HERE"))
                        self.assertEqual(said, "" if d["people"] else "THE NEXT TO WIN STANDS HERE")
                        self.assertEqual(len([r for r in runs if r.s.upper() == "A PLACE ON THE PODIUM"]), 2)

    def test_a_name_that_fits_is_drawn_as_it_was_and_the_longest_are_cut_short(self):
        runs = drawn(PEOPLE, STANDARD).runs
        self.assertEqual(one(runs, "IMOGEN VALE").size, 10.5)
        self.assertEqual(one(runs, "@imvale").size, 7.5)
        phone = drawn(PEOPLE, STANDARD, "narrow").runs
        self.assertAlmostEqual(one(phone, "IMOGEN VALE").size, 10.5 * .82)
        for tone in TONES:
            for variant in SHEETS:
                runs = drawn(HALLS["W names"], tone, variant).runs
                names = [r for r in runs if r.s.startswith("WWW")]
                with self.subTest(tone=tone, variant=variant):
                    self.assertEqual(len(names), 5)
                    for r in names:     # whole, or cut short with an ellipsis: never cut without one
                        self.assertTrue(r.s == "W" * 40 or r.s.endswith("…") and r.s.count("W") < 40, r.s)
                    self.assertEqual(len([r for r in runs if r.s.upper().startswith("@WWW")]), 5, "and their handles")


class Places(unittest.TestCase):
    """After the podium, a place's name and handle end short of its badge; wide, where its wins in each game share
    their line, short of those too, and they short of the badge. On a phone they stand on a line under the name."""

    def test_a_places_name_and_handle_end_short_of_its_wins_in_each_game_and_its_badge(self):
        for name, d in (*HALLS.items(), ("people", PEOPLE)):
            for tone in TONES:
                for variant in SHEETS:
                    f = drawn(d, tone, variant)
                    badges = sorted((r for r in f.runs if r.s.upper() == "WINS" and r.size == 7.5 * (
                        1 if tone == STANDARD else 1.04)), key=lambda r: (r.base, r.x0))[-2:]
                    with self.subTest(hall=name, tone=tone, variant=variant):
                        self.assertEqual(len(badges), 2)
                        for badge in badges:
                            W, _ = size_of(f.svg)
                            start = L.PAD + (W - 2 * L.PAD) / 2 * (variant == "wide" and badge.x0 > W / 2)
                            row = [r for r in f.runs if -8 < r.base - badge.base < 14 and r.x1 <= badge.x0 + TOL
                                   and r.x0 >= start - TOL and not r.s.isdigit()]
                            column = min(r.x0 for r in row)
                            beside = [r for r in row if abs(r.x0 - column) < TOL]
                            self.assertEqual(len(beside), 2, ("the name and the handle", row))
                            # wide, the marks stand on the name's line, short of the badge; on a phone, on a
                            # line of their own under the name and the badge
                            games = [p for p in f.pieces if column <= p.x0 and -20 < p.y0 - badge.top < 30
                                     and (variant == "narrow" or p.x1 <= badge.x0 + TOL)]
                            self.assertEqual(len(games), 8, "the wins in each game, beside its two pieces")
                            for r in beside:
                                self.assertLessEqual(r.x1, badge.x0 - 8 + TOL, r.s)
                                if variant == "wide":
                                    self.assertLessEqual(r.x1, min(p.x0 for p in games) + TOL, r.s)


class Marks(unittest.TestCase):
    """Every game is named by its own mark, its two pieces, the house's on the left in front of GitHub's: the white
    king, the white man and the white marble before the black, X before O, each side's own whoever moved first. The
    same mark heads its row of the series and stands beside every winner's wins in that game, Chess first, each count
    its own game's. Where the room is short the mark gives way before its count does."""

    def emblems(self, f: Drawn) -> list[tuple[str, str, str, Box, Box]]:
        """The marks a file draws, in order, each (game, the front piece's material, the one behind's, and the two
        pieces' boxes): a mark draws GitHub's piece, behind, and then the house's, in front on the left."""
        self.assertEqual(len(f.pieces) % 2, 0, "every piece is one of a pair")
        out = []
        for behind, front in zip(f.pieces[::2], f.pieces[1::2]):
            (game, second), (game2, first) = behind.what.split(), front.what.split()
            self.assertEqual(game, game2)
            self.assertLess(front.x0, behind.x0, "the house's piece on the left")
            out.append((game, first, second, front, behind))
        return out

    def test_every_game_is_named_by_its_two_pieces_the_houses_first(self):
        self.assertEqual((K.HOUSE, K.GITHUB), ("light", "dark"))
        self.assertEqual((S.KING[K.HOUSE], K.MARKS[K.HOUSE]), ("white", "X"), "the house plays White, and X")
        named = [(g, K.HOUSE, K.GITHUB) for g in H.ORDER]
        for tone in TONES:
            for variant in SHEETS:
                marks = [m[:3] for m in self.emblems(drawn(PEOPLE, tone, variant))]
                with self.subTest(tone=tone, variant=variant):
                    # the series' four rows, Chess first, then four marks for each of the five winners
                    self.assertEqual(marks, named * (1 + len(PEOPLE["people"])))

    def test_beside_each_mark_stands_its_own_games_count(self):
        # The data lists each winner's wins in tier order; the sheet reads each count by its game, Chess first.
        wanted = {tuple(dict(zip(H.GAMES, row[1]))[g] for g in H.ORDER) for row in PEOPLE["people"]}
        self.assertEqual(len(wanted), len(PEOPLE["people"]), "every winner's counts their own")
        for tone in TONES:
            for variant in SHEETS:
                f = drawn(PEOPLE, tone, variant)
                marks = self.emblems(f)[len(H.ORDER):]   # each winner's, after the series' rows
                digits = [r for r in f.runs if r.s.isdigit()]
                read = set()
                for i in range(0, len(marks), len(H.ORDER)):
                    counts = []
                    for _, _, _, front, behind in marks[i:i + len(H.ORDER)]:
                        beside = [r for r in digits if behind.x1 - TOL <= r.x0 < behind.x1 + 12
                                  and r.top < front.y1 and r.base > front.y0]
                        self.assertTrue(beside, (tone, variant, front))
                        counts.append(int(min(beside, key=lambda r: r.x0).s))
                    read.add(tuple(counts))
                with self.subTest(tone=tone, variant=variant):
                    self.assertEqual(read, wanted)

    def test_a_game_a_winner_has_yet_to_win_is_marked_faint(self):
        zeros = sum(row[1].count(0) for row in PEOPLE["people"])
        for tone in (STANDARD, "blackprint"):
            for variant in ("still", "narrow-still"):
                with self.subTest(tone=tone, variant=variant):
                    self.assertEqual(E.draw("hall-of-fame", PEOPLE, tone, "day", variant).count('<g opacity=".38">'),
                                     zeros)

    def test_where_the_room_is_short_a_mark_gives_way_before_its_count(self):
        # Drawn with each mark one piece wide, as a game named by a single piece would be, every count is set as
        # large as it is beside the two pieces, at the densest the data allows.
        for name in ("W names", "M logins"):
            for tone in TONES:
                for variant in SHEETS:
                    paired = drawn(HALLS[name], tone, variant).runs
                    with mock.patch.object(L, "STEP", 0):
                        single = drawn(HALLS[name], tone, variant).runs
                    sizes = {}
                    for r in single:
                        sizes.setdefault((r.s, r.base), []).append(r.size)
                    counts = [r for r in paired if r.s.isdigit()]
                    with self.subTest(hall=name, tone=tone, variant=variant):
                        self.assertTrue(counts)
                        for r in counts:
                            self.assertGreaterEqual(r.size + TOL, min(sizes[r.s, r.base]), r)


class Motion(unittest.TestCase):
    """The still files are the moving ones at rest: every run of lettering, piece and block stands where the motion
    leaves it."""

    def test_the_still_files_are_the_moving_ones_at_rest(self):
        for tone in TONES:
            for moving, still in (("wide", "still"), ("narrow", "narrow-still")):
                a, b = drawn(PEOPLE, tone, moving), drawn(PEOPLE, tone, still)
                with self.subTest(tone=tone, variant=moving):
                    self.assertEqual((a.runs, a.pieces, a.bars, a.blocks), (b.runs, b.pieces, b.bars, b.blocks))
                    self.assertIn("<animate", a.svg)
                    self.assertNotIn("<animate", b.svg)


if __name__ == "__main__":
    unittest.main()
