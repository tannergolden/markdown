# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The three games' sheets fit whatever their data says into the room the layout gives it, at the limits the data
may reach, as chess's sheets do (`test_elements_chess_fit`).

Every run of lettering a sheet sets is recorded with its box on the sheet, and each part is held to its room: the
sides' names and logins short of the middle, the note on the turn's row clear of its plate, the last move's words
on a line or two of their own inside the panel, every column of the score sheet clear of the next, and each game's
count inside the panel. Nothing meets anything else, and nothing leaves the card or the drawing's border.

The data reaches the contract's limits: a game, a move, the players and the score sheet's rows at nine digits,
logins of 39 letters set in W and M, the widest capitals there are, a move's words of 80, the longest moves (a jump
of twelve men, and a Pentago move turned anticlockwise that won), every stage of the Ghost Rule with its ghosts' row,
the most boards a side can win in Tic-Tac, six, each side's full rack of marbles and its empty one, the most kings,
and each finished plate's longest way of ending, both ways round."""
from __future__ import annotations

import re
import unittest
from typing import NamedTuple
from unittest import mock

from tests import support

from domain.canvas import BUDGET
from domain.elements import draw as E
from domain.elements.games.skin import Print, Standard
from domain.lettering import Lettering, cap_height, width
from domain.prints import PRINTS, STANDARD
from tests.unit import test_elements_games as G

support.install()
TONES = (STANDARD, *sorted(PRINTS))
SHEETS = ("wide", "narrow")
PAD, GAP, LEAD = 20, 8, 14
TOL = .05
W39, M39 = "W" * 39, "M" * 39
MOST = 999_999_999
WORDS80 = ("WWWWWWW " * 10).strip()
JUMP = "1x10x19x28x19x10x1x10x19x28x19x10x1"          # twelve men taken, the most a jump can take


def limits(d: dict, **more) -> dict:
    """`d` with every field the sheet letters at its widest: the numbers, the logins and the last move's words. The
    ghosts' row keeps its G."""
    rows = d["history"]
    history = [[n if n == "G" else MOST - (len(rows) - 1 - i), a, b,
                ("@" + (W39 if i % 2 else M39)) if (a and b) or who else who]
               for i, (n, a, b, who) in enumerate(rows)]
    out = dict(d, game=MOST, move=MOST, players=MOST, history=history)
    if d.get("last"):
        out["last"] = dict(d["last"], words=WORDS80, by="@" + W39, when="28 May")
    if not d.get("result"):
        out["due"] = "28 May"
    else:
        out["next"] = "28 May"
    return {**out, **more}


# Game 13 of Tic-Tac: GitHub won its sixth board, and three in a row, the most boards a side can win.
TT_SIX = {
    "kind": "tictac", "places": "github", "opens": "house", "game": 13, "move": 29, "players": 3,
    "board": "...XOOOX./.X.OXO.O./OOOXXOX.O/XXXXOOXOO/GXXOOXOOX/.G.OXOXO./X....OXX./OX..XOOXX/O.XX.O.X.",
    "next": "20 Nov", "result": {"winner": "github", "how": "three boards in a row"}, "line": ["a3", "b3", "c3"],
    "history": [[27, "Xe8", "Of6", "@devonaraki"], [28, "Xh1", "Of7#", "@hollyfenwick"], [29, "", "", ""]],
    "last": {"move": "Of7#", "words": "O takes the lower right corner of the top board", "by": "@hollyfenwick",
             "when": "18 Nov"},
    "note": G.over("tictac", 13, "20 Nov", "17:52")}
# The widest moves a Pentago score sheet writes: each turned anticlockwise, the last of them the move that won.
WIDEST = [[MOST - 2, "e5-ur-acw", "d4-lr-acw", "@" + W39], [MOST - 1, "e5-ul-acw", "b2-ll-acw", "@" + M39],
          [MOST, "e5-ur-acw#", "", "@" + W39]]

BOARDS = {
    # each turn's plate (sent to a board, any board, a ghost to place), the ghosts' row, and the fullest racks
    "tictac": [limits(G.TT_GITHUB), limits(G.TT_HOUSE), limits(G.TT_FRESH), limits(G.TT_GHOSTS), limits(G.TT_WON),
               limits(G.TT_DRAWN), limits(TT_SIX)],
    # each side's turn, a ghost the Arbiter set, the widest moves, a marble that won unturned, the empty racks
    "pentago": [limits(G.PG_GITHUB), limits(G.PG_HOUSE), limits(G.PG_FRESH), limits(G.PG_GHOST),
                limits(G.PG_WON, history=WIDEST), limits(G.PG_WON_GITHUB), limits(G.PG_FULL)],
    "checkers": [limits(G.CK_GITHUB, history=[[MOST - 2, JUMP, JUMP, "@" + W39], [MOST - 1, "11x18", JUMP, "@" + M39],
                                              [MOST, "", "", ""]]),
                 # the most kings and the most men taken: twelve Black kings, and White down to one
                 limits(G.CK_GITHUB, fen="W:WK29:BK1,K2,K3,K4,K5,K6,K7,K8,K9,K10,K11,K12", alert="", moves=[],
                        kings={"house": 12, "github": 12},
                        last=dict(G.CK_GITHUB["last"], move="16-12", words="King from 16 to 12")),
                 limits(dict(G.CK_OPENING, last={"move": "9-13", "words": "x", "by": "x", "when": "1 Oct"},
                             fen="W:W21,22,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,10,11,12,13",
                             history=[[1, "9-13", "", ""]], moves=[])),
                 limits(G.CK_WON), limits(G.CK_DRAWN)],
}
# Every finished plate's longest way of ending, each winner and each draw, at the limits.
ENDED = {
    "tictac": [limits(G.TT_WON), limits(G.TT_WON_GITHUB), limits(G.TT_DRAWN)],
    "pentago": [limits(G.PG_WON), limits(G.PG_GIVEN), limits(G.PG_FULL), limits(G.PG_BOTH)],
    "checkers": [limits(G.CK_WON), limits(G.CK_DRAWN),
                 limits(G.CK_DRAWN, result={"winner": None, "how": "repetition"})],
}


class Run(NamedTuple):
    """A run of lettering and its box on the sheet: from x0 to x1, from its capitals' top to its baseline."""
    s: str
    x0: float
    x1: float
    top: float
    base: float
    size: float
    face: str

    @property
    def bottom(self) -> float:
        """How far below the baseline its letters reach: a descender, a comma, an @."""
        return self.base + (self.size * .22 if any(ch.islower() or ch in ",;()@" for ch in self.s) else 0)


def drawn(kind: str, d: dict, tone: str, variant: str = "wide", theme: str = "day") -> tuple[str, list[Run]]:
    """A file, drawn as a run draws it (the kit's lint and budget, or it raises), and every run of lettering in it."""
    runs = []
    text = Lettering.text

    def record(self, s, *, face="meta", size=12, x=0, y=0, anchor="start", ls=0, **k):
        if s:
            w = width(s, face, size, ls)
            x0 = x - w / 2 if anchor == "middle" else x - w if anchor == "end" else x
            runs.append(Run(s, x0, x0 + w, y - cap_height(face, size), y, size, face))
        return text(self, s, face=face, size=size, x=x, y=y, anchor=anchor, ls=ls, **k)
    with mock.patch.object(Lettering, "text", record):
        svg = E.draw(kind, d, tone, theme, variant)
    return svg, runs


def size_of(svg: str) -> tuple[int, int]:
    w, h = re.match(r'<svg[^>]* width="(\d+)" height="(\d+)"', svg).groups()
    return int(w), int(h)


def skin(tone: str, theme: str = "day"):
    return Standard(theme) if tone == STANDARD else Print(theme, tone)


def panel(svg: str, variant: str) -> tuple[float, float]:
    """The board's panel, from its left to the sheet's margin: beside the board, or under it on a phone."""
    W, _ = size_of(svg)
    return (PAD + 18 + 368 + 32 if variant.startswith("wide") or variant == "still" else PAD), W - PAD


def every(kind: str = ""):
    for k, boards in BOARDS.items():
        if kind and k != kind:
            continue
        for d in boards:
            yield k, d


class Clear(unittest.TestCase):
    """Nothing a sheet letters at the limits meets anything else it letters, nor leaves the card or the border."""

    def assertClear(self, svg: str, runs: list[Run], tone: str, what):
        W, H = size_of(svg)
        edge = 1 if tone == STANDARD else (10 if W < 400 else 12) + 1.6   # the card's edge, or the border's inside
        for r in runs:
            self.assertTrue(edge - TOL <= r.x0 and r.x1 <= W - edge + TOL and edge <= r.top and r.bottom <= H - edge,
                            (what, r))
        for i, a in enumerate(runs):
            for b in runs[i + 1:]:
                across = min(a.x1, b.x1) - max(a.x0, b.x0)
                down = min(a.bottom, b.bottom) - max(a.top, b.top)
                self.assertFalse(across > TOL and down > TOL, (what, a, b))

    def test_the_densest_boards_the_data_allows_are_lettered_without_a_clash_in_every_theme(self):
        for kind, d in every():
            self.assertEqual(G.GAMES[kind][0].check(d), [], (kind, d.get("board") or d.get("fen")))
            for tone in TONES:
                for variant in (*SHEETS, "narrow-still"):
                    svg, runs = drawn(kind, d, tone, variant)
                    with self.subTest(kind=kind, board=d.get("board") or d.get("fen"), tone=tone, variant=variant):
                        self.assertClear(svg, runs, tone, (kind, tone, variant))
                        self.assertNotIn("<text", svg)

    def test_every_finished_plate_at_the_limits_says_who_won_how_and_when_without_a_clash(self):
        for kind, boards in ENDED.items():
            for d in boards:
                self.assertEqual(G.GAMES[kind][0].check(d), [], (kind, d["result"]))
                for tone in TONES:
                    for variant in SHEETS:
                        svg, runs = drawn(kind, d, tone, variant)
                        said = {r.s.upper() for r in runs}
                        with self.subTest(kind=kind, result=d["result"], tone=tone, variant=variant):
                            self.assertClear(svg, runs, tone, (kind, d["result"], tone, variant))
                            self.assertIn(d["result"]["how"].upper(), said)
                            self.assertTrue({"NEXT GAME 28 MAY", "NEXT 28 MAY"} & said, "the day, never cut")

    def test_the_files_at_the_limits_are_well_formed_within_budget_and_deterministic_by_day_and_night(self):
        for kind, d in every():
            for tone in TONES:
                for variant in E.variants(kind, d):
                    for theme in ("day", "dark"):
                        svg = E.draw(kind, d, tone, theme, variant)    # the kit's lint and budget, or it raises
                        with self.subTest(kind=kind, tone=tone, variant=variant, theme=theme):
                            self.assertNotIn("<text", svg)
                            self.assertEqual(svg, E.draw(kind, d, tone, theme, variant))
                            # a board over budget fails the whole run, so the densest keeps well clear of it
                            self.assertLess(len(svg.encode()), BUDGET["board"] * .97)


class Still(unittest.TestCase):
    def test_a_still_file_letters_what_its_moving_file_does_where_it_does(self):
        # the moving file comes to rest on the still one: the same words, at the same size, in the same places
        for kind, d in every():
            for tone in TONES:
                for moving, still in (("wide", "still"), ("narrow", "narrow-still")):
                    (one, runs), (two, at_rest) = drawn(kind, d, tone, moving), drawn(kind, d, tone, still)
                    with self.subTest(kind=kind, board=G.name(d), tone=tone, variant=moving):
                        self.assertTrue(runs)
                        self.assertEqual(runs, at_rest)
                        self.assertEqual(size_of(one), size_of(two))


class Words(unittest.TestCase):
    """The last move's words stand on a line or two of their own under the move, inside the panel, as chess's do: an
    engine's sentence keeps its size and every word, and only words two lines cannot hold end in an ellipsis."""

    SAID = ("A white marble on e4, then the upper right quarter turns anticlockwise",
            "King from 19 jumps 15, 6, 10 and 14, landing on 23, crowned and safe",
            "A ghost locks the upper right corner of the upper right board")
    BOARDS = {"tictac": G.TT_GITHUB, "pentago": G.PG_GITHUB, "checkers": G.CK_GITHUB}

    def lines(self, kind: str, d: dict, tone: str, variant: str):
        """The file, the runs that say the last move's words, and the panel: the words stand at the panel's left
        and are set from 11 points down to their floor, which nothing else there is."""
        svg, runs = drawn(kind, d, tone, variant)
        said = d["last"]["words"].upper()
        px0, px1 = panel(svg, variant)
        k = 1 if tone == STANDARD else Print.K
        lines = [r for r in runs if abs(r.x0 - px0) < TOL and 8.5 * k - TOL <= r.size <= 11 * k + TOL
                 and len(r.s) > 1 and r.s.upper().rstrip("…") in said]
        return svg, lines, (px0, px1)

    def test_the_words_stand_under_the_move_inside_the_panel_in_every_theme(self):
        for kind, d in self.BOARDS.items():
            for words in self.SAID + (WORDS80, "W" * 80):
                board = dict(d, last=dict(d["last"], words=words))
                for tone in TONES:
                    for variant in SHEETS:
                        svg, lines, (px0, px1) = self.lines(kind, board, tone, variant)
                        with self.subTest(kind=kind, words=words[:16], tone=tone, variant=variant):
                            self.assertIn(len(lines), (1, 2))
                            for line in lines:
                                self.assertAlmostEqual(line.x0, px0, delta=TOL)
                                self.assertLessEqual(line.x1, px1 + TOL)

    def test_an_engines_sentence_keeps_its_size_and_every_word(self):
        for kind, d in self.BOARDS.items():
            for words in self.SAID:
                board = dict(d, last=dict(d["last"], words=words))
                for tone in TONES:
                    for variant, size in (("wide", 11), ("narrow", 10.5)):
                        _, lines, _ = self.lines(kind, board, tone, variant)
                        with self.subTest(kind=kind, words=words[:16], tone=tone, variant=variant):
                            self.assertEqual(" ".join(r.s for r in lines).upper(), words.upper())
                            self.assertEqual({r.size for r in lines}, {size * (1 if tone == STANDARD else Print.K)})

    def test_only_words_two_lines_cannot_hold_end_in_an_ellipsis(self):
        for kind, d in self.BOARDS.items():
            board = dict(d, last=dict(d["last"], words="W" * 80))
            for tone in TONES:
                for variant in SHEETS:
                    _, lines, _ = self.lines(kind, board, tone, variant)
                    with self.subTest(kind=kind, tone=tone, variant=variant):
                        self.assertTrue(lines[-1].s.endswith("…"))

    def test_a_sheet_grows_by_a_line_for_words_that_take_two_and_stands_the_same_in_every_theme(self):
        for kind, d in self.BOARDS.items():
            short = dict(d, last=dict(d["last"], words="A move"))
            long = dict(d, last=dict(d["last"], words=self.SAID[1]))
            heights = {(tone, which): size_of(E.draw(kind, b, tone, "day", "narrow"))[1]
                       for tone in TONES for which, b in (("short", short), ("long", long))}
            with self.subTest(kind=kind):
                for tone in TONES:
                    self.assertEqual(heights[tone, "short"], heights[STANDARD, "short"])
                    self.assertEqual(heights[tone, "long"], heights[STANDARD, "short"] + LEAD)


class TurnRow(unittest.TestCase):
    """The note across from the turn's plate, the day the move is due by (a game's first move's too, since every
    turn has its clock), or on a finished board the day the fresh one comes, keeps clear of the plate in every state
    of the row, said in full where there is room and short where there is not, never cut."""

    NOTES = ("due by 28 may", "by 28 may", "next game 28 may", "next 28 may")

    def states(self):
        for kind, (pkg, boards) in G.GAMES.items():
            for d in boards:
                yield kind, dict(d, next="28 May") if d.get("result") else dict(d, due="28 May")

    def test_the_note_keeps_clear_of_the_plate(self):
        for kind, d in self.states():
            for tone in TONES:
                for variant in SHEETS:
                    svg, runs = drawn(kind, d, tone, variant)
                    px0, px1 = panel(svg, variant)
                    note = [r for r in runs if r.s.lower() in self.NOTES]
                    with self.subTest(kind=kind, board=G.name(d), tone=tone, variant=variant):
                        self.assertEqual(len(note), 1, [r.s for r in runs][:12])
                        row = [r for r in runs if abs(r.base - note[0].base) < 9 and r is not note[0]
                               and r.x0 >= px0 - TOL]
                        for r in row:     # the plate's words, beside the note across the row
                            self.assertTrue(r.x1 + GAP - TOL <= note[0].x0 or note[0].x1 + GAP - TOL <= r.x0,
                                            (note[0], r))
                        self.assertGreaterEqual(note[0].x0, px0 - TOL)
                        self.assertLessEqual(note[0].x1, px1 + TOL)


class Panel(unittest.TestCase):
    """The score sheet's columns, the sides' names and each game's count stay in the panel at the data's limits."""

    def test_every_column_of_the_score_sheet_clears_the_next_at_the_longest_numbers_moves_and_logins(self):
        for kind, d in every():
            for tone in TONES:
                for variant in SHEETS:
                    svg, runs = drawn(kind, d, tone, variant)
                    px0, px1 = panel(svg, variant)
                    for n, *_ in d["history"][-2 if variant == "narrow" else -3:]:
                        number = [r for r in runs if r.s == f"{n}."]
                        with self.subTest(kind=kind, tone=tone, variant=variant, row=n):
                            self.assertEqual(len(number), 1)
                            row = sorted((r for r in runs if abs(r.base - number[0].base) < TOL), key=lambda r: r.x0)
                            self.assertEqual(row[0], number[0])
                            for a, b in zip(row, row[1:]):
                                self.assertLessEqual(a.x1 + 4, b.x0 + TOL, (a.s, b.s))
                            self.assertLessEqual(row[-1].x1, px1 + TOL)

    def test_the_sides_names_keep_short_of_the_middle_of_the_row(self):
        for kind, d in every():
            for tone in TONES:
                for variant in SHEETS:
                    svg, runs = drawn(kind, d, tone, variant)
                    px0, px1 = panel(svg, variant)
                    mid = (px0 + px1) / 2
                    sides = [r for r in runs if r.s.upper() in ("@TANNERGOLDEN", "GITHUB")]
                    with self.subTest(kind=kind, tone=tone, variant=variant):
                        self.assertEqual(len(sides), 2)
                        house, github = sorted(sides, key=lambda r: r.x0)
                        self.assertLess(house.x1, mid)
                        self.assertGreater(github.x0, mid)

    def test_everything_the_panel_draws_stays_within_its_margin(self):
        for kind, d in every():
            for tone in TONES:
                for variant in SHEETS:
                    svg, runs = drawn(kind, d, tone, variant)
                    px0, px1 = panel(svg, variant)
                    top = min(r.top for r in runs if r.s.upper() == "@TANNERGOLDEN") - 20   # the panel's first row
                    shapes = [(float(x), float(y), float(w)) for x, y, w in
                              re.findall(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)"', svg)]
                    with self.subTest(kind=kind, tone=tone, variant=variant):
                        for x, y, w in shapes:
                            if y > top and x >= px0 - 10:      # a plate, a tray, a chip or a row's mark
                                self.assertLessEqual(x + w, px1 + 2 + TOL, (x, y, w))


if __name__ == "__main__":
    unittest.main()
