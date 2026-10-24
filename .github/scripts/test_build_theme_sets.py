#!/usr/bin/env python3
"""Tests for the theme-sets page builder.

WHY THIS EXISTS. docs/references/themes is what the README sends a reader to when they
choose a theme, and the builder that draws it runs rarely: by hand, after a
theme changes. A broken path or a stale template would only show up as a
blank picture on a page nobody re-checks. These tests draw two themes into a
temporary folder, one of them a holiday set, and hold the result to what the
page reads and what the repository's own checks demand of a committed file.

Run it:

    python3 .github/scripts/test_build_theme_sets.py
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import pathlib
import re
import tempfile
import unittest
from unittest import mock

SCRIPT = pathlib.Path(__file__).resolve().parent / 'build-theme-sets.py'
_spec = importlib.util.spec_from_file_location('build_theme_sets', SCRIPT)
builder = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(builder)

ONLY = ['standard', 'halloween']


def manifest_of(page: str) -> dict:
    found = re.search(r'<script type="application/json" id="manifest">(.*?)</script>', page, re.S)
    return json.loads(found[1])


def drawings_of(entry: dict) -> list[str]:
    return builder.paths(entry)


class TestFiles(unittest.TestCase):
    """The repository's copy: the page beside one SVG per drawing."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = pathlib.Path(cls.tmp.name) / 'themes'
        with contextlib.redirect_stdout(io.StringIO()):
            builder.main([str(cls.out), '--only', ','.join(ONLY)])
        cls.page = (cls.out / 'index.html').read_text(encoding='utf-8')
        cls.manifest = manifest_of(cls.page)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_the_page_is_a_whole_document_with_every_slot_filled(self) -> None:
        self.assertTrue(self.page.startswith('<!doctype html>\n'))
        self.assertIn('<meta charset="utf-8">', self.page[:1024])
        self.assertIn(builder.MARK, self.page)
        self.assertNotRegex(self.page, r'__[A-Z]+__')

    def test_it_draws_only_the_themes_asked_for_in_the_kits_order(self) -> None:
        self.assertEqual([t['key'] for t in self.manifest['themes']], ONLY)
        self.assertEqual(self.manifest['payload'], 'files')

    def test_every_drawing_the_page_names_is_beside_it(self) -> None:
        for entry in self.manifest['themes']:
            names = drawings_of(entry) + list(entry['thumb'].values())
            for name in names:
                self.assertTrue((self.out / name).is_file(), name)

    def test_a_moving_header_keeps_its_still_pair(self) -> None:
        heads = self.manifest['themes'][0]['sections'][0]['items']
        self.assertTrue(heads)
        for it in heads:
            self.assertIn('sday', it)
            self.assertIn('sdark', it)
            self.assertNotEqual(it['day'], it['sday'])

    def test_every_file_passes_the_whitespace_rules_of_the_repository(self) -> None:
        # validate-repository.py fails a tracked file with no final newline or a line with trailing whitespace.
        for path in self.out.rglob('*'):
            if path.is_file():
                text = path.read_text(encoding='utf-8')
                self.assertTrue(text.endswith('\n'), path)
                self.assertNotIn('\r', text, path)
                self.assertFalse(any(line != line.rstrip() for line in text.splitlines()), path)

    def test_a_holiday_set_shows_its_badges_on_both_kinds_of_page(self) -> None:
        halloween = self.manifest['themes'][1]
        badges = [s for s in halloween['sections'] if s['key'] == 'badges'][0]
        self.assertEqual([r['label'] for r in badges['rows']], ["On a standard page", "On a print's page"])
        self.assertEqual(halloween['use'], 'holidays: true')

    def test_every_theme_shows_its_trophy_case_drawn_in_its_own_look(self) -> None:
        for entry, look in zip(self.manifest['themes'], ('night', 'halloween night')):
            trophies = [s for s in entry['sections'] if s['key'] == 'trophies'][0]
            self.assertEqual([r['label'] for r in trophies['rows']],
                             ['Level and next up', 'The five styles', 'Every tier', 'Achievements'])
            self.assertEqual([len(r['chips']) for r in trophies['rows'][1:3]], [5, 6])
            dark = (self.out / trophies['rows'][1]['chips'][0]['dark']).read_text(encoding='utf-8')
            self.assertIn(f'<!--markdown-kit v1 trophy {look}-->', dark, entry['key'])

    def test_it_never_empties_a_folder_that_is_not_its_own(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            keep = pathlib.Path(tmp) / 'notes.md'
            keep.write_text('mine\n', encoding='utf-8')
            with self.assertRaises(SystemExit):
                builder.clear(pathlib.Path(tmp))
            self.assertTrue(keep.is_file())


def pixel_sets() -> tuple[list[str], list[str], dict[str, list[str]]]:
    """The labels the sets a game is drawn in carry: each holiday's set by its name and the Birthday set after them,
    then each pixel theme by its name, then each design of every collection with all twelve drawn by its month, by
    collection, as the page gives each collection a section of its own."""
    sets = [builder.holidays.NAMES[k] for k in builder.holidays.KEYS if k in builder.holidays.SETS]
    sets.append(f'the {builder.birthday.NAME} set')
    pixels = [builder.pixelthemes.name_of(k) for k in builder.pixelthemes.themes()]
    years = {c: [f'{builder.collections.MONTHS[i]}: {builder.collections.name_of(k)}'
                 + (", the profile's" if k == builder.PROFILE_LOOK else '')
                 for i, k in enumerate(builder.collections.COLLECTIONS[c].keys)]
             for c in builder.collections.themes()}
    return sets, pixels, years


class APixelTheme(unittest.TestCase):
    """A pixel theme is one entry of its own group, drawn whole as the set draws it every day of the year: its
    headers, phones, footers, elements, badges and trophy case, and what to write to wear it."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = pathlib.Path(cls.tmp.name) / 'themes'
        cls.key = builder.pixelthemes.themes()[0]
        with contextlib.redirect_stdout(io.StringIO()):
            builder.main([str(cls.out), '--only', cls.key])
        cls.entry = manifest_of((cls.out / 'index.html').read_text(encoding='utf-8'))['themes'][0]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_it_is_its_own_kind_and_says_what_to_write_to_wear_it(self) -> None:
        theme = builder.pixelthemes.THEMES[self.key]
        self.assertEqual((self.entry['key'], self.entry['name'], self.entry['group'], self.entry['tag']),
                         (self.key, theme.name, 'pixel', 'all year'))
        self.assertEqual(self.entry['use'], f'theme: {self.key}')
        self.assertTrue(self.entry['note'].startswith(theme.summary))
        self.assertEqual({s['role'] for s in self.entry['swatches']},
                         {f'{role}, {when}' for role in ('title', 'accent', 'body') for when in ('day', 'night')})

    def test_it_is_drawn_whole_in_its_own_pixels(self) -> None:
        sections = {s['key']: s for s in self.entry['sections']}
        self.assertEqual(list(sections), ['headers', 'phones', 'footers', 'elements', 'badges', 'trophies'])
        self.assertEqual([r['label'] for r in sections['badges']['rows']], ['In its classic styles', 'As a plate'])
        for name in drawings_of(self.entry) + list(self.entry['thumb'].values()):
            self.assertTrue((self.out / name).is_file(), name)
        h2 = (self.out / self.entry['thumb']['dark']).read_text(encoding='utf-8')
        self.assertIn(f' {self.key} ', h2.split('-->')[0])
        dark = (self.out / sections['trophies']['rows'][1]['chips'][0]['dark']).read_text(encoding='utf-8')
        self.assertIn(f'<!--markdown-kit v1 trophy {self.key} night-->', dark)


class TheGame(unittest.TestCase):
    """The game the kit draws for @tannergolden's profile alone is one entry beside the themes: its sheets in the
    standard theme and every print, in every holiday's set and every month's design of a collection, from the sample
    game, and in place of what to write, where to see it live."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = pathlib.Path(cls.tmp.name) / 'themes'
        with contextlib.redirect_stdout(io.StringIO()):
            builder.main([str(cls.out), '--only', 'chess'])
        cls.entry = manifest_of((cls.out / 'index.html').read_text(encoding='utf-8'))['themes'][0]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_it_is_a_game_that_says_where_to_see_it_live(self) -> None:
        self.assertEqual((self.entry['key'], self.entry['group']), ('chess', 'game'))
        self.assertEqual(self.entry['use'], '', 'nothing to write: no other page can draw it')
        self.assertEqual(self.entry['where'], "On @tannergolden's profile README, and nowhere else")
        self.assertEqual(self.entry['link'], 'https://github.com/tannergolden')
        self.assertEqual(self.entry['link_text'], "See the games live on @tannergolden's profile →")

    def test_its_board_is_drawn_in_the_standard_theme_and_every_print_as_the_other_boards_are(self) -> None:
        tones = [builder.prints.STANDARD, *builder.prints.PRINTS]
        sections = {s['key']: s for s in self.entry['sections']}
        _, _, years = pixel_sets()
        self.assertEqual(list(sections), ['board', 'holidays', 'pixel-themes', *years, 'phones'],
                         'its Hall of Fame is the four games\' own entry now')
        items = sections['board']['items']
        self.assertEqual([it['label'].split(', ')[1] for it in items], tones)
        self.assertTrue(all(it['label'].startswith('Board') for it in items))
        self.assertTrue(all('sday' in it and 'sdark' in it for it in items), 'each with its still pair')
        self.assertEqual([it['label'] for it in sections['phones']['items']],
                         ['Board, standard', "Board, blackprint"])

    def test_every_drawing_the_entry_names_is_beside_the_page(self) -> None:
        for name in drawings_of(self.entry) + list(self.entry['thumb'].values()):
            self.assertTrue((self.out / name).is_file(), name)

    def test_its_board_is_drawn_in_every_holidays_set_and_every_months_design_in_their_pixels(self) -> None:
        sets, pixels, years = pixel_sets()
        sections = {s['key']: s for s in self.entry['sections']}
        self.assertEqual([it['label'] for it in sections['holidays']['items']], [f'Board, {n}' for n in sets])
        self.assertEqual([it['label'] for it in sections['pixel-themes']['items']], [f'Board, {n}' for n in pixels])
        for c, months in years.items():
            self.assertEqual([it['label'] for it in sections[c]['items']], [f'Board, {n}' for n in months], c)
        for section in ('holidays', 'pixel-themes', *years):
            for it in sections[section]['items']:
                self.assertTrue('sday' in it and 'sdark' in it, 'each with its still pair')
                self.assertEqual(it['w'], 830)
                key = it['day'].split('/')[1].removeprefix('chess-wide-').removesuffix('-day.svg')
                for side in ('day', 'dark', 'sday', 'sdark'):
                    head = (self.out / it[side]).read_text(encoding='utf-8').split('-->')[0]
                    self.assertIn(f' {key} elements chess ', head, it[side])

    def test_a_set_that_hands_a_game_back_to_the_pages_look_is_never_shown_under_its_name(self) -> None:
        builder.in_set.cache_clear()
        try:
            with mock.patch.object(builder.elements_data, 'held_game', lambda *a: None), \
                    self.assertRaises(SystemExit) as raised:
                builder.in_set('chess', 'halloween')
            self.assertIn("halloween drew chess in the page's own look", str(raised.exception))
        finally:
            builder.in_set.cache_clear()

    def test_a_sample_game_the_kit_would_turn_away_is_never_drawn(self) -> None:
        bad = 'elements:\n  chess:\n    kind: chess\n    fen: not a position\n'
        with tempfile.TemporaryDirectory() as tmp:
            game = pathlib.Path(tmp) / 'chess.yaml'
            game.write_text(bad, encoding='utf-8')
            builder.sample_game.cache_clear()
            try:
                with mock.patch.object(builder, 'GAME', game), self.assertRaises(SystemExit):
                    builder.sample_game()
            finally:
                builder.sample_game.cache_clear()


class TheGamesBesideChess(unittest.TestCase):
    """Checkers, Pentago and Tic-Tac are each one entry in the Games group, after chess's and in the README's
    order: the board in the standard theme and every print, and the files a phone gets, each from its own sample
    game, checked as a run checks it."""

    KEYS = ('checkers', 'pentago', 'tictac')

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = pathlib.Path(cls.tmp.name) / 'themes'
        with contextlib.redirect_stdout(io.StringIO()):
            builder.main([str(cls.out), '--only', ','.join(cls.KEYS)])
        cls.entries = {e['key']: e for e in manifest_of((cls.out / 'index.html').read_text(encoding='utf-8'))['themes']}

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_each_is_a_game_in_its_tiers_order_that_says_where_to_see_it_live(self) -> None:
        self.assertEqual(list(self.entries), list(self.KEYS))
        self.assertEqual(builder.GAMES, ('chess', 'checkers', 'pentago', 'tictac'), 'the README\'s order')
        for key, entry in self.entries.items():
            with self.subTest(key=key):
                self.assertEqual(entry['group'], 'game')
                self.assertEqual(entry['use'], '', 'nothing to write: no other page can draw it')
                self.assertEqual(entry['where'], "On @tannergolden's profile README, and nowhere else")
                self.assertEqual(entry['link'], 'https://github.com/tannergolden')

    def test_its_board_is_drawn_in_the_standard_theme_and_every_print_and_on_a_phone(self) -> None:
        tones = [builder.prints.STANDARD, *builder.prints.PRINTS]
        for key, entry in self.entries.items():
            sections = {s['key']: s for s in entry['sections']}
            with self.subTest(key=key):
                sets, pixels, years = pixel_sets()
                self.assertEqual(list(sections), ['board', 'holidays', 'pixel-themes', *years, 'phones'])
                self.assertEqual([len(sections[k]['items']) for k in ('holidays', 'pixel-themes', *years)],
                                 [len(sets), len(pixels), *(len(m) for m in years.values())])
                items = sections['board']['items']
                self.assertEqual([it['label'].split(', ')[1] for it in items], tones)
                self.assertTrue(all('sday' in it and 'sdark' in it for it in items), 'each with its still pair')
                self.assertEqual([it['label'] for it in sections['phones']['items']],
                                 ['Board, standard', "Board, blackprint"])
                self.assertTrue(all(it['w'] == 360 for it in sections['phones']['items']))
                for name in drawings_of(entry) + list(entry['thumb'].values()):
                    self.assertTrue((self.out / name).is_file(), name)

    def test_the_samples_of_the_games_under_the_ghost_rule_name_the_sides_the_arbiter_drew(self) -> None:
        # Tic-Tac's sample: the house drawn to place the first ghost and GitHub to make the first mark; Pentago's:
        # the house drawn to set the first ghost and the first marble
        tictac, pentago = builder.sample_game('tictac')['tictac'], builder.sample_game('pentago')['pentago']
        self.assertEqual((tictac['places'], tictac['opens']), ('house', 'github'))
        self.assertEqual((pentago['places'], pentago['opens']), ('house', 'house'))
        self.assertNotIn('dark', builder.sample_game('checkers')['checkers'], 'GitHub plays Black and opens Checkers')
        for key in ('tictac', 'pentago'):
            with self.subTest(key=key):
                self.assertIn('Under the Ghost Rule', self.entries[key]['note'])
                self.assertIn('Under the Ghost Rule', builder.sample_game(key)[key]['note'])

    def test_a_sample_game_the_kit_would_turn_away_is_never_drawn(self) -> None:
        # a board of Tic-Tac-Toe's three rows under Tic-Tac's name
        bad = 'elements:\n  tictac:\n    kind: tictac\n    board: XXX/XXX/XXX\n    places: house\n'
        with tempfile.TemporaryDirectory() as tmp:
            game = pathlib.Path(tmp) / 'chess.yaml'
            (pathlib.Path(tmp) / 'tictac.yaml').write_text(bad, encoding='utf-8')
            builder.sample_game.cache_clear()
            try:
                with mock.patch.object(builder, 'GAME', game), self.assertRaises(SystemExit) as raised:
                    builder.sample_game('tictac')
                self.assertIn("tictac.yaml: tictac: board 'XXX/XXX/XXX' is not nine rows of nine X, O, G or dots",
                              str(raised.exception))
            finally:
                builder.sample_game.cache_clear()


class TheHallOfFame(unittest.TestCase):
    """The Hall of Fame of all four games is one entry after them in the Games group: its sheet in the standard theme
    and every print, in every holiday's set and every month's design of a collection, the files a phone gets and the
    winners' badges, from its own sample, checked as a run checks it, and in place of what to write, where to see it
    live."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = pathlib.Path(cls.tmp.name) / 'themes'
        with contextlib.redirect_stdout(io.StringIO()):
            builder.main([str(cls.out), '--only', 'chess,hall-of-fame'])
        cls.entries = {e['key']: e for e in manifest_of((cls.out / 'index.html').read_text(encoding='utf-8'))['themes']}
        cls.entry = cls.entries['hall-of-fame']

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_it_comes_after_the_games_and_says_where_to_see_it_live(self) -> None:
        self.assertEqual(list(self.entries), ['chess', 'hall-of-fame'], 'after the four games')
        self.assertEqual((self.entry['group'], self.entry['hall']), ('game', True), 'counted apart from the games')
        self.assertEqual(self.entry['use'], '', 'nothing to write: no other page can draw it')
        self.assertEqual(self.entry['where'], "On @tannergolden's profile README, and nowhere else")
        self.assertEqual(self.entry['link'], 'https://github.com/tannergolden')

    def test_its_sheet_phones_and_badges_are_drawn_in_the_standard_theme_and_every_print(self) -> None:
        tones = [builder.prints.STANDARD, *builder.prints.PRINTS]
        sets, pixels, years = pixel_sets()
        months = [n for m in years.values() for n in m]
        sections = {s['key']: s for s in self.entry['sections']}
        self.assertEqual(list(sections), ['hall', 'holidays', 'pixel-themes', *years, 'phones', 'badges'])
        self.assertEqual([it['label'] for it in sections['pixel-themes']['items']],
                         [f'Hall of Fame, {n}' for n in pixels])
        self.assertEqual([it['label'] for it in sections['holidays']['items']], [f'Hall of Fame, {n}' for n in sets])
        for c, labels in years.items():
            self.assertEqual([it['label'] for it in sections[c]['items']], [f'Hall of Fame, {n}' for n in labels], c)
        items = sections['hall']['items']
        self.assertEqual([it['label'].split(', ')[1] for it in items], tones)
        self.assertTrue(all(it['label'].startswith('Hall of Fame') for it in items))
        self.assertTrue(all('sday' in it and 'sdark' in it for it in items), 'each with its still pair')
        self.assertEqual([it['label'] for it in sections['phones']['items']],
                         ['Hall of Fame, standard', "Hall of Fame, blackprint"])
        self.assertTrue(all(it['w'] == 360 for it in sections['phones']['items']))
        self.assertEqual([r['label'] for r in sections['badges']['rows']],
                         ['In standard', "In blackprint"] + [f'In {n}' for n in sets + pixels + months])
        self.assertEqual({len(r['chips']) for r in sections['badges']['rows']}, {5}, 'a badge for each winner')

    def test_every_drawing_the_entry_names_is_beside_the_page(self) -> None:
        for name in drawings_of(self.entry) + list(self.entry['thumb'].values()):
            self.assertTrue((self.out / name).is_file(), name)

    def test_its_sample_is_the_four_games_own_and_passes_the_kits_checks(self) -> None:
        sample = builder.sample_game('hall-of-fame')
        self.assertEqual(list(sample), ['hall-of-fame'])
        self.assertEqual(list(sample['hall-of-fame']['series']), ['tictac', 'pentago', 'checkers', 'chess'])


class TestBundle(unittest.TestCase):
    """The copy for a host that caps its files: the page and one data file per theme."""

    def test_each_theme_carries_every_drawing_its_sheet_shows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = pathlib.Path(tmp) / 'site'
            with contextlib.redirect_stdout(io.StringIO()):
                builder.main([str(out), '--bundle', '--only', 'standard'])
            page = (out / 'index.html').read_text(encoding='utf-8')
            manifest = manifest_of(page)
            self.assertEqual(manifest['payload'], 'bundles')
            self.assertFalse(page.startswith('<!doctype'))
            files = json.loads((out / 'themes' / 'standard.json').read_text(encoding='utf-8'))
            self.assertEqual(set(files), set(drawings_of(manifest['themes'][0])))
            self.assertTrue(all(svg.lstrip().startswith('<svg') for svg in files.values()))



class ACollection(unittest.TestCase):
    """A collection with all twelve designs drawn is one entry, its year of twelve headers, with its own page
    beside it; one still being drawn is not shown at all."""

    def setUp(self):
        C = builder.collections
        drawn = [k for c in C.COLLECTIONS.values() for k in c.keys if C.is_drawn(k)]
        keys = [f'standin-{m.lower()}' for m in C.MONTHS]
        borrowed = {k: drawn[i % len(drawn)] for i, k in enumerate(keys)}
        package = C.package
        complete = C.Collection('standin', 'Stand-in', tuple((k, f'Design {i + 1}') for i, k in enumerate(keys)))
        self.pages = []
        for p in (mock.patch.object(C, 'COLLECTIONS', {'standin': complete}),
                  mock.patch.object(C, 'package', lambda k: package(borrowed.get(k, k))),
                  mock.patch.object(builder, 'collection_page', lambda *a: self.pages.append(a))):
            p.start()
            self.addCleanup(p.stop)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = pathlib.Path(self.tmp.name) / 'themes'

    def test_a_complete_collection_is_one_entry_with_its_year_and_its_own_page(self):
        with contextlib.redirect_stdout(io.StringIO()):
            manifest = builder.build(self.out, only=['standin'])
        (entry,) = manifest['themes']
        self.assertEqual((entry['group'], entry['name'], entry['use'], entry['link']),
                         ('collection', 'Stand-in', 'theme: standin', 'standin/index.html'))
        self.assertEqual(len(entry['slices']), 12)
        (year,) = entry['sections']
        self.assertEqual([it['label'] for it in year['items']][:2], ['January: Design 1', 'February: Design 2'])
        self.assertEqual(len(year['items']), 12)
        for path in drawings_of(entry) + [p for pair in entry['slices'] for p in pair.values()]:
            self.assertTrue((self.out / path).is_file(), path)
        self.assertEqual(self.pages, [('standin', self.out / 'standin', False)])

    def test_its_year_draws_each_design_as_its_months_design_so_its_headers_carry_the_mark(self):
        C = builder.collections
        asked, drawn_by = [], C.drawn_by
        builder.drawn.cache_clear()     # drawn afresh, not as an earlier test drew it
        with mock.patch.object(C, 'drawn_by', lambda key: asked.append(key) or drawn_by(key)):
            with contextlib.redirect_stdout(io.StringIO()):
                builder.build(self.out, only=['standin'])
        dated = {k for k in asked if ':' in k}
        self.assertEqual(dated, {f'standin-{m.lower()}:2026-{i + 1:02d}-01' for i, m in enumerate(C.MONTHS)})

    def test_a_collection_still_being_drawn_is_not_shown(self):
        C = builder.collections
        with mock.patch.object(C, 'is_drawn', lambda k: not k.endswith('december')):
            self.assertNotIn('standin', C.themes())
            with self.assertRaises(SystemExit):
                with contextlib.redirect_stdout(io.StringIO()):
                    builder.build(self.out, only=['standin'])


if __name__ == '__main__':
    unittest.main()
