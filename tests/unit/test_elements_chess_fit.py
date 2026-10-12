# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""The chess sheets fit whatever their data says into the room the layout gives it, at the limits the data may reach.

Every run of lettering a sheet sets is recorded with its box on the sheet, and each part is held to its room: the
last move's words on a line or two of their own inside the panel, the note on the turn's row clear of its badge, a
winner's name and handle short of the rule, the count or the badge beside them, and every number at its longest
clear of the next column. What fitted before is drawn as it was. The motion is held to the board: a pawn taken en
passant fades on the square it stood on, a castling king brings its rook, and the still files stand still.

The data reaches the contract's limits: a game, a move and the players at nine digits, a move number and a score
sheet's rows at 99,999, the Hall's counts at 999,999, logins of 39 letters and names of 40, a move's words of 80,
and fifteen pieces taken. Every limit is set in W or M, the widest capitals there are."""
from __future__ import annotations

import re
import unittest
from typing import NamedTuple
from unittest import mock

from tests import support

from domain.elements import chess as C
from domain.elements import draw as E
from domain.elements.chess import layout as L
from domain.elements.chess import motion as M
from domain.elements.chess.skins import Print, Standard
from domain.lettering import Lettering, cap_height, f1, fx, width
from domain.prints import PRINTS, STANDARD

support.install()
TONES = (STANDARD, *sorted(PRINTS))
SHEETS = ("wide", "narrow")
TOL = .05
W39, M39 = "W" * 39, "M" * 39
LINK = ("https://github.com/tannergolden/play/issues/new?template=move.yml&title=chess%3A%20c7d6%20%C2%B7%20game%2013"
        "%20%C2%B7%20move%2042")
# GitHub to move and in check after 21. Nd6+, and the house to move after 21... cxd6: the game the sheets were drawn
# from. The data each test needs is built from these.
GAME = {
    "kind": "chess", "fen": "2kr4/ppp4p/2nNp3/2b1q3/2p3P1/2PrR3/PP1B1P1P/R4QK1 b - - 3 21",
    "game": 13, "move": 21, "players": 9, "due": "18 Oct", "check": "c8",
    "last": {"san": "Nd6+", "from": "e4", "to": "d6", "piece": "knight", "captured": "",
             "words": "Knight from e4 to d6, check", "by": "@tannergolden", "when": "11 Oct"},
    "taken": {"white": "bpp", "black": "nbp"},
    "history": [[19, "Bxd2", "Qxg7", "@imvale"], [20, "Re3", "Qe5", "@jhalloran"], [21, "Nd6+", "", ""]],
    "moves": [{"piece": "king", "list": [["🏰", "The Royal Retreat", "Kb8", "King from c8 to b8", LINK]]}],
}
HOUSE = dict(GAME, fen="2kr4/pp5p/2npp3/2b1q3/2p3P1/2PrR3/PP1B1P1P/R4QK1 w - - 0 22", move=22, players=10,
             due="19 Oct", check="", taken={"white": "bpp", "black": "nbpn"},
             last={"san": "cxd6", "from": "c7", "to": "d6", "piece": "pawn", "captured": "knight",
                   "words": "Pawn from c7 takes the knight on d6", "by": "@wrencastellan", "when": "12 Oct"},
             history=[[20, "Re3", "Qe5", "@jhalloran"], [21, "Nd6+", "cxd6", "@wrencastellan"], [22, "", "", ""]])
OPENING = {"kind": "chess", "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "game": 1, "move": 1}
# Every field of the board at its widest at once: the densest panel the data allows.
LIMITS = dict(GAME, fen=GAME["fen"].rsplit(" ", 1)[0] + " 99999", game=999_999_999, move=999_999_999,
              players=999_999_999, due="28 May", taken={"white": "qrrbbnnpppppppp", "black": ""},
              last=dict(GAME["last"], san="exd8=Q+", words=("WWWWWWW " * 10).strip(), by="@" + W39, when="28 May"),
              history=[[99_997, "Qa1xb2+", "exd8=Q#", "@" + W39], [99_998, "O-O-O+", "Nb1xc3+", "@" + M39],
                       [99_999, "Rh8xg7#", "", ""]])


def hall(people, names=None, house=333_333, world=333_333, draws=333_333) -> dict:
    return {"kind": "chess-hall", "games": house + world + draws, "house": house, "world": world, "draws": draws,
            "people": people, "names": names or {}}


def logins(letter: str) -> list[str]:
    """Five logins of 39 letters, each its own."""
    return [letter * 39] + [letter * (39 - len(str(i))) + str(i) for i in range(1, 5)]


# Five winners at every limit: names of 40 letters, or none, so each is named by a login of 39; counts of 999,999.
HALLS = {
    "W names": hall([[n, 999_999 - i, "28 May", 999_999] for i, n in enumerate(logins("W"))],
                    {n: "W" * 40 for n in logins("W")}),
    "M names": hall([[n, 999_999 - i, "28 May", 999_999] for i, n in enumerate(logins("M"))],
                    {n: "M" * 40 for n in logins("M")}),
    "W logins": hall([[n, 999_999 - i, "28 May", 999_999] for i, n in enumerate(logins("W"))]),
    "M logins": hall([[n, 999_999 - i, "28 May", 999_999] for i, n in enumerate(logins("M"))]),
    "long names": hall([["christopher-alexander-montgomer", 5, "2 Oct", 12], ["imvale", 2, "19 Sep", 7],
                        ["tokafor", 2, "27 Sep", 5], ["wrencastellan", 1, "4 Sep", 6], ["jhalloran", 1, "8 Oct", 3]],
                       {"imvale": "Christopher Alexander Montgomery", "tokafor": "Tomas Okafor"}, 5, 6, 1),
}
PEOPLE = hall([["tannergolden", 5, "2 Oct", 12], ["imvale", 2, "19 Sep", 7], ["tokafor", 2, "27 Sep", 5],
               ["wrencastellan", 1, "4 Sep", 6], ["jhalloran", 1, "8 Oct", 3]],
              {"imvale": "Imogen Vale", "tokafor": "Tomas Okafor"}, 5, 6, 1)


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


def one(runs: list[Run], s: str) -> Run:
    """The one run that says `s`, in any case."""
    found = [r for r in runs if r.s.upper() == s.upper()]
    assert len(found) == 1, (s, [r.s for r in runs])
    return found[0]


def panel(runs: list[Run], W: int) -> tuple[float, float]:
    """The board's panel, from the left of its headings to the sheet's margin."""
    return one(runs, "moves").x0, W - L.PAD


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

    def test_the_densest_board_the_data_allows_is_lettered_without_a_clash_in_every_theme(self):
        for tone in TONES:
            for variant in (*SHEETS, "narrow-still"):
                svg, runs = drawn("chess", LIMITS, tone, variant)
                with self.subTest(tone=tone, variant=variant):
                    self.assertClear(svg, runs, tone, (tone, variant))
                    self.assertNotIn("<text", svg)

    def test_a_hall_of_the_longest_names_and_logins_is_lettered_without_a_clash_in_every_theme(self):
        for name, h in HALLS.items():
            for tone in TONES:
                for variant in SHEETS:
                    svg, runs = drawn("chess-hall", h, tone, variant)
                    with self.subTest(hall=name, tone=tone, variant=variant):
                        self.assertClear(svg, runs, tone, (name, tone, variant))

    def test_the_files_at_the_limits_are_well_formed_within_budget_and_deterministic_by_day_and_night(self):
        for kind, d in (("chess", LIMITS), ("chess-hall", HALLS["W names"]), ("chess-hall", HALLS["M logins"])):
            for tone in TONES:
                for variant in E.variants(kind, d):
                    for theme in ("day", "dark"):
                        svg = E.draw(kind, d, tone, theme, variant)    # the kit's lint and budget, or it raises
                        with self.subTest(kind=kind, tone=tone, variant=variant, theme=theme):
                            self.assertNotIn("<text", svg)
                            self.assertEqual(svg, E.draw(kind, d, tone, theme, variant))


class Words(unittest.TestCase):
    """The last move's words stand on a line or two of their own under the move, inside the panel: an engine's
    sentence keeps its size and every word, and only words two lines cannot hold at the floor end in an ellipsis."""

    SAID = ("Queen from e5 takes the knight on d6, check",                        # cut at "d6, c" on a phone before
            "Pawn from b7 takes the knight on a8, becoming a knight, checkmate")  # the longest an engine writes
    WIDEST = (("WWWWWWW " * 10).strip(), "W" * 80)                                # the limit, in the widest letter

    def lines(self, d: dict, tone: str, variant: str) -> tuple[Run, list[Run], tuple[float, float], list[Run]]:
        """The move as notation, its words line by line, the panel, and every run on the sheet."""
        svg, runs = drawn("chess", d, tone, variant)
        san = next(r for r in runs if r.s.endswith(d["last"]["san"]))
        said = d["last"]["words"].upper()
        lines = [r for r in runs if r.base > san.base and r.s.upper().rstrip("…") in said and len(r.s) > 1]
        return san, lines, panel(runs, size_of(svg)[0]), runs

    def test_the_words_stand_under_the_move_inside_the_panel_in_every_theme(self):
        for words in self.SAID + self.WIDEST:
            d = dict(HOUSE, last=dict(HOUSE["last"], san="Qxd6+", words=words))
            for tone in TONES:
                for variant in SHEETS:
                    san, lines, (px0, px1), _ = self.lines(d, tone, variant)
                    with self.subTest(words=words[:20], tone=tone, variant=variant):
                        self.assertIn(len(lines), (1, 2))
                        for line in lines:
                            self.assertAlmostEqual(line.x0, san.x0, delta=TOL, msg="a line of its own, under the move")
                            self.assertLessEqual(line.x1, px1 + TOL)
                            self.assertGreater(line.top, san.base)

    def test_an_engines_sentence_keeps_its_size_and_every_word(self):
        for words in self.SAID:
            d = dict(HOUSE, last=dict(HOUSE["last"], words=words))
            for tone in TONES:
                for variant, size in (("wide", 11), ("narrow", 10.5)):
                    _, lines, _, _ = self.lines(d, tone, variant)
                    with self.subTest(words=words[:20], tone=tone, variant=variant):
                        self.assertEqual(" ".join(r.s for r in lines).upper(), words.upper())
                        self.assertEqual({r.size for r in lines}, {size * (1 if tone == STANDARD else Print.K)})

    def test_only_words_two_lines_cannot_hold_end_in_an_ellipsis(self):
        d = dict(HOUSE, last=dict(HOUSE["last"], words="W" * 80))
        for tone in TONES:
            for variant in SHEETS:
                _, lines, _, _ = self.lines(d, tone, variant)
                with self.subTest(tone=tone, variant=variant):
                    self.assertTrue(lines[-1].s.endswith("…"))

    def test_on_a_phone_the_sheet_grows_by_a_line_for_words_that_take_two_and_stands_the_same_in_every_theme(self):
        short = dict(HOUSE, last=dict(HOUSE["last"], words=self.SAID[0]))
        long = dict(HOUSE, last=dict(HOUSE["last"], words=self.SAID[1]))
        heights = {(tone, d is long): size_of(E.draw("chess", d, tone, "day", "narrow"))[1]
                   for tone in TONES for d in (short, long)}
        self.assertEqual(set(heights.values()), {heights[STANDARD, False], heights[STANDARD, False] + L.LEAD})
        for tone in TONES:
            self.assertEqual(heights[tone, True], heights[tone, False] + L.LEAD, tone)

    def test_the_line_under_the_words_cuts_a_login_short_and_keeps_the_day(self):
        d = dict(GAME, last=dict(GAME["last"], by="@" + W39, when="28 May"))
        for tone in TONES:
            for variant in SHEETS:
                svg, runs = drawn("chess", d, tone, variant)
                by = next(r for r in runs if r.s.upper().startswith("BY @"))
                with self.subTest(tone=tone, variant=variant):
                    self.assertLessEqual(by.x1, size_of(svg)[0] - L.PAD + TOL)
                    self.assertTrue(by.s.upper().endswith("  ·  28 MAY"), by.s)
                    if tone == STANDARD and variant == "narrow":    # elsewhere the whole login fits the floor
                        self.assertIn("…", by.s)
        _, runs = drawn("chess", GAME, STANDARD)
        self.assertEqual((one(runs, "by @tannergolden  ·  11 oct").size), 7.5, "a login that fits is set as it was")


class TurnRow(unittest.TestCase):
    """The note across from the turn's badge, the day the move is due by or that no clock runs yet, keeps clear of
    the badge in every state of the row: either side to move, in check or not, with a day or without, wide and on
    a phone, in every theme."""

    def test_the_note_keeps_clear_of_the_badge(self):
        for tone in TONES:
            sk = skin(tone)
            for variant in SHEETS:
                for base, king in ((GAME, "c8"), (HOUSE, "g1")):
                    for check in (True, False):
                        for due in ("", "18 Oct", "28 May"):
                            d = dict(base, check=king if check else "", due=due)
                            svg, runs = drawn("chess", d, tone, variant)
                            px0, px1 = panel(runs, size_of(svg)[0])
                            badge = sk.chip(f"{'GitHub' if base is GAME else '@tannergolden'}'s turn",
                                            "in check" if check else "", icon="play",
                                            size=10 if variant == "wide" else 8.5, lab="turn", msg="alert")
                            said = ({f"due by {due}".lower(), f"by {due}".lower()} if due
                                    else {"no clock until the first move", "no clock yet"})
                            note = [r for r in runs if r.s.lower() in said]
                            with self.subTest(tone=tone, variant=variant, side=d["fen"].split()[1], check=check,
                                              due=due):
                                self.assertEqual(len(note), 1)
                                if base is GAME:     # GitHub's badge on the right, the note on the left
                                    self.assertGreaterEqual(note[0].x0, px0 - TOL)
                                    self.assertLessEqual(note[0].x1, px1 - badge.w - L.GAP + TOL)
                                else:
                                    self.assertGreaterEqual(note[0].x0, px0 + badge.w + L.GAP - TOL)
                                    self.assertLessEqual(note[0].x1, px1 + TOL)

    def test_the_note_is_said_in_full_where_it_fits_and_short_where_it_does_not(self):
        _, wide = drawn("chess", OPENING, STANDARD)
        _, phone = drawn("chess", OPENING, STANDARD, "narrow")
        self.assertEqual(one(wide, "no clock until the first move").size, 7)
        self.assertEqual(one(phone, "no clock yet").size, 7)
        _, wide = drawn("chess", GAME, STANDARD)
        self.assertEqual(one(wide, "due by 18 oct").size, 7)


class Panel(unittest.TestCase):
    """The score sheet's columns and the taken pieces' badge stay in the panel at the data's limits; where the data
    fits as it always has, they stand where they always have."""

    def test_every_column_of_the_score_sheet_clears_the_next_at_the_longest_numbers_moves_and_logins(self):
        for tone in TONES:
            for variant in SHEETS:
                svg, runs = drawn("chess", LIMITS, tone, variant)
                px0, px1 = panel(runs, size_of(svg)[0])
                for n, *cells in LIMITS["history"][-2 if variant == "narrow" else -3:]:
                    number = one(runs, f"{n}.")
                    row = sorted((r for r in runs if abs(r.base - number.base) < TOL), key=lambda r: r.x0)
                    with self.subTest(tone=tone, variant=variant, row=n):
                        self.assertEqual(row[0], number)
                        for a, b in zip(row, row[1:]):
                            self.assertLessEqual(a.x1 + 4, b.x0 + TOL, (a.s, b.s))
                        self.assertLessEqual(row[-1].x1, px1 + TOL)

    def test_a_score_sheet_that_fits_keeps_its_columns(self):
        for variant in SHEETS:
            svg, runs = drawn("chess", HOUSE, STANDARD, variant)
            px0, _ = panel(runs, size_of(svg)[0])
            self.assertEqual([round(one(runs, s).x0 - px0, 1) for s in ("21.", "Nd6+", "cxd6", "@wrencastellan")],
                             [0, 26, 82, 136])

    def test_the_lead_in_material_stays_in_the_panel_beside_a_full_tray(self):
        d = dict(GAME, taken={"white": "qrrbbnnpppppppp", "black": ""})
        for tone in TONES:
            sk = skin(tone)
            for variant, mini in (("wide", 20), ("narrow", 18)):
                svg, runs = drawn("chess", d, tone, variant)
                lead, chip = one(runs, "+39"), sk.chip("+39", "", size=7.5, lab="accent")
                tray = [float(x) for x in re.findall(r'<use href="#[^"]+" transform="translate\(([\d.]+) [\d.]+\) '
                                                      r'scale\(' + re.escape(fx(mini / 45, 4)) + r'\)"/>', svg)]
                with self.subTest(tone=tone, variant=variant):
                    self.assertEqual(len(tray), 15)
                    self.assertLessEqual(lead.x1 + chip.pad, size_of(svg)[0] - L.PAD + TOL)
                    self.assertLessEqual(max(tray) + mini, lead.x0 - chip.pad + TOL, "the badge clears the tray")


class Names(unittest.TestCase):
    """A winner's name and handle keep short of what stands beside them: the rule to the next column on the
    podium, the count of wins on a phone, the badge of wins in the places after; a long one is set smaller and the
    longest is cut short with an ellipsis, in every theme. A name that fitted is drawn as it was."""

    def test_on_the_podium_every_line_of_a_column_ends_where_its_bar_does_short_of_the_rule_to_the_next(self):
        for name, h in HALLS.items():
            for tone in TONES:
                svg, runs = drawn("chess-hall", h, tone, "still")
                W, _ = size_of(svg)
                colw = (W - 2 * L.PAD) / 3
                rules = {float(x) for x in re.findall(r'<path d="M([\d.]+) [\d.]+V[\d.]+"', svg)}
                for i in range(3):
                    x = L.PAD + i * colw + 66
                    rule = L.PAD + (i + 1) * colw - 6      # the rule to the next column, or as far in from the margin
                    if i < 2:
                        self.assertIn(float(f1(rule)), rules)
                    track = re.findall(rf'<rect x="{re.escape(f1(x))}" y="[\d.]+" width="([\d.]+)" height="6"', svg)
                    column = [r for r in runs if abs(r.x0 - x) < TOL]
                    with self.subTest(hall=name, tone=tone, column=i):
                        self.assertLessEqual(x + max(float(w) for w in track), rule - 2 + TOL, "the bar")
                        self.assertGreaterEqual(len(column), 4, "the name, the handle, the wins and the last win")
                        for r in column:
                            self.assertLessEqual(r.x1, x + max(float(w) for w in track) + TOL, r.s)

    def test_on_a_phone_the_name_and_handle_end_short_of_the_count_of_wins(self):
        for name, h in HALLS.items():
            for tone in TONES:
                _, runs = drawn("chess-hall", h, tone, "narrow")
                counts = [r for r in runs if abs(r.x1 - (L.NARROW - L.PAD - 34)) < TOL]
                with self.subTest(hall=name, tone=tone):
                    self.assertEqual(len(counts), 3)
                    for count in counts:
                        beside = [r for r in runs if abs(r.x0 - (L.PAD + 52)) < TOL and -9 < r.base - count.base < 6]
                        self.assertEqual(len(beside), 2, "the name and the handle")
                        for r in beside:
                            self.assertLessEqual(r.x1, count.x0 - L.GAP + TOL, r.s)

    def test_after_the_podium_the_name_and_handle_end_short_of_the_badge_of_wins(self):
        for name, h in HALLS.items():
            for tone in TONES:
                pad = skin(tone).chip("wins", "1", size=7.5, lab="label", msg="count").pad
                for variant in SHEETS:
                    svg, runs = drawn("chess-hall", h, tone, variant)
                    W, _ = size_of(svg)
                    # the badges' labels: the last two runs of WINS down the sheet, the podium's coming before
                    badges = sorted((r for r in runs if r.s.upper() == "WINS"), key=lambda r: r.base)[-2:]
                    with self.subTest(hall=name, tone=tone, variant=variant):
                        for badge in badges:
                            # the place's name and handle start beside its number, at the left of its column
                            column = L.PAD + (W - 2 * L.PAD) / 2 * (variant == "wide" and badge.x0 > W / 2)
                            beside = [r for r in runs
                                      if -7 < r.base - badge.base < 12 and abs(r.x0 - column - 28) < TOL]
                            self.assertEqual(len(beside), 2, "the name and the handle")
                            for r in beside:
                                self.assertLessEqual(r.x1, badge.x0 - pad - L.GAP + TOL, r.s)

    def test_the_longest_are_cut_short_and_a_name_that_fits_is_drawn_as_it_was(self):
        for tone in TONES:
            for variant in SHEETS:
                _, runs = drawn("chess-hall", HALLS["W names"], tone, variant)
                names = [r for r in runs if r.s.startswith("WWW")]
                with self.subTest(tone=tone, variant=variant):
                    self.assertEqual(len(names), 5)
                    for r in names:     # whole, or cut short with an ellipsis: never cut without one
                        self.assertTrue(r.s == "W" * 40 or r.s.endswith("…") and r.s.count("W") < 40, r.s)
                    self.assertTrue(names[0].s.endswith("…"), "a place on the podium cannot hold forty Ws")
                    self.assertEqual(len([r for r in runs if r.s.upper().startswith("@WWW")]), 5, "and their handles")
        _, runs = drawn("chess-hall", PEOPLE, STANDARD)
        self.assertEqual(one(runs, "IMOGEN VALE").size, 10.5)
        self.assertEqual(one(runs, "@imvale").size, 7.5)
        _, runs = drawn("chess-hall", PEOPLE, STANDARD, "narrow")
        self.assertEqual(one(runs, "IMOGEN VALE").size, 9.5)

    def test_a_bar_measures_against_the_most_wins_and_never_runs_past_its_track(self):
        self.assertEqual(L.bar(200, 40, 40), 200)
        self.assertEqual(L.bar(200, 1, 40), 5)
        self.assertEqual(L.bar(200, 1, 400), 3, "never too short to see")
        self.assertEqual(L.bar(200, 9, 0), 200)
        unsorted = hall([["imvale", 1, "2 Oct", 3], ["tokafor", 9, "3 Oct", 12], ["jhalloran", 40, "4 Oct", 50]],
                        house=10, world=50, draws=0)
        # The data's checks turn an unranked podium away before anything is drawn, so the layout is held to it alone.
        self.assertTrue(C.check_hall(unsorted))
        for tone in TONES:
            sk = Standard("day") if tone == STANDARD else Print("day", tone)
            for shape in SHEETS:
                with M.at_rest(True):
                    svg = L.hall_sheet(sk, C.hall_state(unsorted), "Chess: Hall of Fame", "", shape)
                W, _ = size_of(svg)
                for x, w in re.findall(r'<rect x="([\d.]+)" y="[\d.]+" width="([\d.]+)"', svg):
                    with self.subTest(tone=tone, shape=shape):
                        self.assertLessEqual(float(x) + float(w), W, "nothing runs off the card")


class Motion(unittest.TestCase):
    """The last move comes in as it was played: a pawn taken en passant fades on the square it stood on, a castling
    king's rook comes round it, and the still files stand still."""

    PASSANT = dict(GAME, fen="rnbqkbnr/ppp1p1pp/3P4/5p2/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 3", check="",
                   last={"san": "exd6", "from": "e5", "to": "d6", "piece": "pawn", "captured": "pawn",
                         "words": "Pawn from e5 takes the pawn on d5, en passant", "by": "@tannergolden",
                         "when": "12 Oct"},
                   history=[[2, "e5", "d5", "@imvale"], [3, "exd6", "", ""]], taken={"white": "p", "black": ""})
    CASTLE = dict(GAME, fen="r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQ1RK1 b kq - 5 4", check="",
                  last={"san": "O-O", "from": "e1", "to": "g1", "piece": "king", "captured": "",
                        "words": "Castle kingside", "by": "@tannergolden", "when": "12 Oct"},
                  history=[[3, "Bc4", "Bc5", "@imvale"], [4, "O-O", "", ""]], taken={"white": "", "black": ""})
    LONG = dict(HOUSE, fen="2kr3r/pppq1ppp/2n5/8/8/8/PPP2PPP/2KR3R w - - 4 12", check="",
                last={"san": "O-O-O", "from": "e8", "to": "c8", "piece": "king", "captured": "",
                      "words": "Castle queenside", "by": "@octocat", "when": "12 Oct"},
                history=[[11, "Kb1", "O-O-O", "@octocat"], [12, "", "", ""]])
    BOARDS = {"wide": (L.PAD + 18, L.BAND + 22, 46), "narrow": (L.PAD + 14, L.BAND + 18, 37)}

    def taken_at(self, svg: str) -> tuple[float, float]:
        """Where the piece the last move took fades: the one piece drawn unseen until it does."""
        found = re.findall(r'<use href="#[^"]+" transform="translate\(([\d.]+) ([\d.]+)\) scale\([\d.]+\)" '
                           r'opacity="0"><animate attributeName="opacity"', svg)
        self.assertEqual(len(found), 1)
        return float(found[0][0]), float(found[0][1])

    def test_a_pawn_taken_en_passant_fades_on_the_square_it_stood_on(self):
        for tone in (STANDARD, "blackprint"):
            for variant, (x0, y0, s) in self.BOARDS.items():
                at = self.taken_at(E.draw("chess", self.PASSANT, tone, "day", variant))
                self.assertEqual(at, tuple(float(f1(v)) for v in L.sq_xy("d5", x0, y0, s)), (tone, variant))
        at = self.taken_at(E.draw("chess", HOUSE, STANDARD, "day", "wide"))
        self.assertEqual(at, tuple(float(f1(v)) for v in L.sq_xy("d6", *self.BOARDS["wide"])), "any other capture")
        self.assertEqual(L.passed(C.board_state(self.PASSANT)["last"], C.board_state(self.PASSANT)["placement"]), "d5")

    def test_a_castling_kings_rook_comes_round_it(self):
        for d, corner, beside in ((self.CASTLE, "h1", "f1"), (self.LONG, "a8", "d8")):
            st = C.board_state(d)
            self.assertEqual(L.castled(st["last"], st["placement"]), (corner, beside))
            for tone in (STANDARD, "blackprint"):
                for variant, (x0, y0, s) in self.BOARDS.items():
                    svg = E.draw("chess", d, tone, "day", variant)
                    (cx, _), (bx, _) = L.sq_xy(corner, x0, y0, s), L.sq_xy(beside, x0, y0, s)
                    with self.subTest(king=d["last"]["san"], tone=tone, variant=variant):
                        self.assertEqual(svg.count('type="scale"'), 2, "the king and its rook come in")
                        self.assertIn(f'values="{f1(cx - bx)} 0;{f1(cx - bx)} 0;', svg, "the rook from its corner")
        st = C.board_state(HOUSE)
        self.assertIsNone(L.castled(st["last"], st["placement"]))
        self.assertEqual(E.draw("chess", HOUSE, STANDARD, "day", "wide").count('type="scale"'), 1)

    def test_the_still_files_stand_still(self):
        for d in (self.PASSANT, self.CASTLE, self.LONG):
            for tone in (STANDARD, "blackprint"):
                for variant in ("still", "narrow-still"):
                    self.assertNotIn("<animate", E.draw("chess", d, tone, "dark", variant), (d["last"]["san"], tone))


if __name__ == "__main__":
    unittest.main()
