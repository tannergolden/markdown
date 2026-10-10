#!/usr/bin/env python3
"""Tests for the theme-sets page builder.

WHY THIS EXISTS. docs/themes is what the README sends a reader to when they
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

    def test_it_never_empties_a_folder_that_is_not_its_own(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            keep = pathlib.Path(tmp) / 'notes.md'
            keep.write_text('mine\n', encoding='utf-8')
            with self.assertRaises(SystemExit):
                builder.clear(pathlib.Path(tmp))
            self.assertTrue(keep.is_file())


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
